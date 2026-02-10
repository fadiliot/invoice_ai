from fastapi import APIRouter
from app.database import SessionLocal
from app.models import Invoice

router = APIRouter()

@router.get("/api/review")
def get_pending_reviews():
    db = SessionLocal()
    return db.query(Invoice).filter(Invoice.status == "REVIEW").all()
