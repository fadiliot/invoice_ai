from sqlalchemy import Column, DateTime, Integer, String, Float, JSON
from app.database import Base
from datetime import datetime

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True)
    vendor = Column(String, nullable=True)
    invoice_number = Column(String, nullable=True)
    invoice_date = Column(String, nullable=True)
    total = Column(Float, nullable=True)
    tax = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    status = Column(String)
    data = Column(JSON)
    quickbooks_id = Column(String, nullable=True)
    processing_stage = Column(String, default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(Float, nullable=True)  # processing time in seconds
    error_message = Column(String, nullable=True)
    file_path = Column(String, nullable=True)



