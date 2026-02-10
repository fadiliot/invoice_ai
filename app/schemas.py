from pydantic import BaseModel
from typing import List
from typing import Optional


class LineItem(BaseModel):
    name: str
    quantity: float
    price: float

class InvoiceSchema(BaseModel):
    vendor: str
    invoice_number: str
    invoice_date: str
    line_items: List[LineItem]
    tax: float
    total: float

class InvoiceUpdate(BaseModel):
    vendor: Optional[str]
    invoice_number: Optional[str]
    invoice_date: Optional[str]
    total: Optional[float]
    tax: Optional[float]

