from fastapi import FastAPI, UploadFile , File, Depends
from requests import Session
from app.utils import save_file
from app.ocr.ocr_service import extract_text
from app.parser.invoice_parser import parse_invoice
from app.validation.validator import validate_invoice
from app.quickbooks.qb_client import push_to_quickbooks
from app.database import SessionLocal
from app.models import Invoice
from app.logs.logger import log
from app.config import CONFIDENCE_THRESHOLD
from app.review.review_api import router as review_router
from app.parser.gemini_parser import parse_invoice_with_gemini
from app.quickbooks.oauth import router as qb_auth_router
from sqlalchemy import update
from typing import List
from pdf2image import convert_from_bytes
from PIL import Image
import io
import pytesseract
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from app.queue import invoice_queue
from app.worker_tasks import process_invoice_task
from app.schemas import InvoiceUpdate
from fastapi.middleware.cors import CORSMiddleware






app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(review_router)
app.include_router(qb_auth_router)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def process_invoice(file: UploadFile, db: Session):

    filename = file.filename.lower()
    contents = await file.read()

    # 1 Extract text
    if filename.endswith(".pdf"):
        pages = convert_from_bytes(contents)
        text = ""
        for page in pages:
            text += pytesseract.image_to_string(page) + "\n"
    else:
        image = Image.open(io.BytesIO(contents))
        text = pytesseract.image_to_string(image)

    # 2 Try rule-based parser first
    parsed = parse_invoice(text)  # rule-based parser
    print(parsed)

    
    confidence = validate_invoice(parsed)
    print(confidence)

    # 3 Only call Gemini if confidence is low
    if confidence < 0.85:
        print("🔄 Falling back to Gemini parser")
        parsed = parse_invoice_with_gemini(text)
        confidence = validate_invoice(parsed)

    if confidence >= 0.85:
        status = "APPROVED"
    elif confidence >= 0.7:
        status = "REVIEW"
    else:
        status = "FAILED"


    # 4 Save to DB
    invoice = Invoice(
        vendor=parsed.get("vendor"),
        invoice_number=parsed.get("invoice_number"),
        invoice_date=parsed.get("invoice_date"),
        total=parsed.get("total"),
        tax=parsed.get("tax"),
        status=status,
        confidence=confidence,
        data=parsed
    )

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    qb_id = None

    # 5 Push to QuickBooks if approved
    if status == "APPROVED":
        qb_response = push_to_quickbooks(parsed)
        qb_id = qb_response["qb_id"]

        invoice.quickbooks_id = qb_id
        db.commit()

    return {
        "invoice_id": invoice.id,
        "status": invoice.status,
        "quickbooks_id": qb_id
    }



@app.post("/upload-invoices")
async def upload_invoices(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    results = []

    for file in files:
        contents = await file.read()

        # Save file to disk (make sure save_file returns file path)
        file_path = save_file(contents, file.filename)
        print("Saved file path:", file_path)


        # Create PENDING invoice with file path stored
        invoice = Invoice(
            status="PENDING",
            processing_stage="PENDING",
            file_path=file_path
        )

        db.add(invoice)
        db.commit()
        db.refresh(invoice)

        # Enqueue only invoice ID (NOT file bytes)
        invoice_queue.enqueue(
            process_invoice_task,
            invoice.id
        )

        results.append({
            "invoice_id": invoice.id,
            "status": "PENDING"
        })

    return {"results": results}


@app.get("/invoice/{id}")
def get_invoice(id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == id).first()
    if not invoice:
        return {"error": "Invoice not found"}
    return invoice



@app.put("/invoice/{id}")
def update_invoice(
    id: int,
    payload: InvoiceUpdate,
    db: Session = Depends(get_db)
):
    invoice = db.query(Invoice).filter(Invoice.id == id).first()

    if not invoice:
        return {"error": "Invoice not found"}

    if payload.vendor is not None:
        invoice.vendor = payload.vendor

    if payload.invoice_number is not None:
        invoice.invoice_number = payload.invoice_number

    if payload.invoice_date is not None:
        invoice.invoice_date = payload.invoice_date

    if payload.total is not None:
        invoice.total = payload.total

    if payload.tax is not None:
        invoice.tax = payload.tax

    # also update JSON data
    invoice.data.update({
        "vendor": invoice.vendor,
        "invoice_number": invoice.invoice_number,
        "invoice_date": invoice.invoice_date,
        "total": invoice.total,
        "tax": invoice.tax,
    })

    db.commit()
    db.refresh(invoice)

    return invoice

@app.post("/invoice/{id}/approve")
def approve_invoice(id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == id).first()

    if not invoice:
        return {"error": "Invoice not found"}

    # Push to QuickBooks
    qb_response = push_to_quickbooks(invoice.data)

    invoice.quickbooks_id = qb_response["qb_id"]
    invoice.status = "APPROVED"
    invoice.processing_stage = "QB_SYNCED"

    db.commit()

    return {
        "message": "Invoice approved and synced",
        "quickbooks_id": invoice.quickbooks_id
    }

from sqlalchemy import desc, asc
from fastapi import Query

@app.get("/api/invoices")
def get_invoices(
    page: int = 1,
    limit: int = 10,
    search: str = "",
    status: str = "",
    sort: str = "created_at",
    order: str = "desc",
    db: Session = Depends(get_db)
):
    query = db.query(Invoice)

    if search:
        query = query.filter(
            (Invoice.vendor.ilike(f"%{search}%")) |
            (Invoice.invoice_number.ilike(f"%{search}%"))
        )

    if status:
        query = query.filter(Invoice.processing_stage == status)

    total = query.count()

    sort_column = getattr(Invoice, sort, Invoice.created_at)
    query = query.order_by(
        sort_column.desc() if order == "desc" else sort_column.asc()
    )

    invoices = query.offset((page - 1) * limit).limit(limit).all()

    def serialize(inv):
        return {
            "id": inv.id,
            "vendor": inv.vendor,
            "invoice_number": inv.invoice_number,
            "invoice_date": inv.invoice_date,
            "total": inv.total,
            "tax": inv.tax,
            "confidence": inv.confidence,
            "status": inv.status,
            "processing_stage": inv.processing_stage,
            "quickbooks_id": inv.quickbooks_id,
            "created_at": inv.created_at.isoformat() if inv.created_at else None,
            "completed_at": inv.completed_at,
            "error_message": inv.error_message,
        }

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": [serialize(inv) for inv in invoices],
    }

@app.get("/api/dashboard-stats")
def dashboard_stats(db: Session = Depends(get_db)):
    total = db.query(Invoice).count()
    approved = db.query(Invoice).filter(Invoice.status == "APPROVED").count()
    review = db.query(Invoice).filter(Invoice.processing_stage == "REVIEW").count()
    failed = db.query(Invoice).filter(Invoice.processing_stage == "FAILED").count()
    pending = db.query(Invoice).filter(Invoice.processing_stage == "PENDING").count()
    synced = db.query(Invoice).filter(Invoice.processing_stage == "QB_SYNCED").count()

    return {
        "total": total,
        "approved": approved,
        "review": review,
        "failed": failed,
        "pending": pending,
        "synced": synced,
    }

@app.get("/health")
def health():
    return {"status": "ok"}

# Path to built React app
frontend_path = Path(__file__).resolve().parent / "frontend_dist"

# Serve React static assets (JS, CSS)
app.mount(
    "/assets",
    StaticFiles(directory=frontend_path / "assets"),
    name="assets",
)




# Catch-all route to serve React (SPA support)
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    index_file = frontend_path / "index.html"
    return FileResponse(index_file)