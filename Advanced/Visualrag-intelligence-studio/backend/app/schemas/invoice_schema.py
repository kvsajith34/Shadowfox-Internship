"""Invoice extraction request/response schemas."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class InvoiceLineItem(BaseModel):
    description: str = ""
    quantity: float = 0
    unit_price: float = 0
    total: float = 0


class InvoiceResponseData(BaseModel):
    vendor_name: str = ""
    customer_name: str = ""
    invoice_number: str = ""
    invoice_date: str = ""
    due_date: str = ""
    subtotal: float = 0
    tax_amount: float = 0
    total_amount: float = 0
    currency: str = "USD"
    payment_status: str = "unknown"
    line_items: List[InvoiceLineItem] = []
    missing_fields: List[str] = []
    confidence_score: float = 0.0
    safety_note: str = ""
    raw_extracted_text: str = ""
