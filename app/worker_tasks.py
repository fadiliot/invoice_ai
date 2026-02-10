from app.database import SessionLocal
from app.models import Invoice
from app.parser.invoice_parser import parse_invoice
from app.parser.gemini_parser import parse_invoice_with_gemini
from app.quickbooks.qb_client import push_to_quickbooks
from pdf2image import convert_from_bytes
from PIL import Image
import pytesseract
import io
import time
from app.validation.validator import validate_invoice

def process_invoice_task(invoice_id):
    db = SessionLocal()
    invoice = None

    try:
        start_time = time.time()

        invoice = db.get(Invoice, invoice_id)
        if not invoice:
            return

        invoice.processing_stage = "PROCESSING"
        db.commit()

        # Read file from disk
        file_path = invoice.file_path
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        if file_path.lower().endswith(".pdf"):
            pages = convert_from_bytes(file_bytes)
            text = ""
            for page in pages:
                text += pytesseract.image_to_string(page) + "\n"
        else:
            image = Image.open(io.BytesIO(file_bytes))
            text = pytesseract.image_to_string(image)

        print("===== OCR TEXT START =====")
        print(text[:1000])
        print("===== OCR TEXT END =====")


        parsed = parse_invoice(text)
        confidence = validate_invoice(parsed)
        print("Confidence before Gemini:", confidence)

        used_gemini = False
        if confidence < 0.88:
            used_gemini = True
            parsed = parse_invoice_with_gemini(text)
            print("Calling Gemini...")
            confidence = validate_invoice(parsed)

        #  FIXED DEMO OVERRIDE
        if parsed.get("vendor") == "G YOUR COMPANY":
            status = "REVIEW"
        else:
            if confidence >= 0.85:
                status = "APPROVED"
            elif confidence >= 0.7:
                status = "REVIEW"
            else:
                status = "FAILED"

        invoice.vendor = parsed.get("vendor")
        invoice.invoice_number = parsed.get("invoice_number")
        invoice.invoice_date = parsed.get("invoice_date")
        invoice.total = parsed.get("total")
        invoice.tax = parsed.get("tax")
        invoice.status = status
        invoice.confidence = confidence
        invoice.data = {**parsed, "used_gemini": used_gemini}

        #  FIXED QB HANDLING
        if status == "APPROVED":
            try:
                qb_response = push_to_quickbooks(parsed)
                invoice.quickbooks_id = qb_response["qb_id"]
                invoice.processing_stage = "QB_SYNCED"
            except Exception as qb_error:
                invoice.processing_stage = "FAILED"
                invoice.error_message = str(qb_error)
        
        elif status == "REVIEW":
            invoice.processing_stage = "REVIEW"
        else:
            invoice.processing_stage = "FAILED"

        invoice.completed_at = time.time() - start_time
        db.commit()

    except Exception as e:
        if invoice:
            invoice.processing_stage = "FAILED"
            invoice.error_message = str(e)
            db.commit()
        print("Worker error:", str(e))

    finally:
        db.close()
