from pydantic import BaseModel, Field, field_validator
from typing import List
import re

class ProductSearchDTO(BaseModel):
    query: str = Field(..., min_length=1, max_length=50)

    @field_validator("query")
    @classmethod
    def sanitize_query(cls, value: str) -> str:
        if not re.match(r"^[a-zA-Z0-9\s\-]+$", value):
            raise ValueError("Caracteres no permitidos en el criterio de búsqueda.")
        return value

class ItemDTO(BaseModel):
    sku: str = Field(..., pattern=r"^SKU\-[0-9]{3,6}$")
    name: str = Field(..., max_length=100)
    price: float = Field(..., gt=0.0, le=5000.0)
    emoji: str = Field(default="📦", max_length=10)

    class Config:
        extra = "forbid"

class TransactionCreateDTO(BaseModel):
    items: List[ItemDTO] = Field(..., min_items=1)

    class Config:
        extra = "forbid"  # BLOQUEO CRÍTICO: Rechaza discount_pct con HTTP 422

class ReceiptResponseDTO(BaseModel):
    receipt_id: str
    store_id: str
    cashier_id: str
    timestamp: str
    items: List[ItemDTO]
    subtotal: float
    total_amount: float
    discount_pct: float
    status: str