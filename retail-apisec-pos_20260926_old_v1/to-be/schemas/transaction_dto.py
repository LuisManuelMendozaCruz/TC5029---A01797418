from pydantic import BaseModel, Field, field_validator
import re

class ProductSearchDTO(BaseModel):
    query: str = Field(..., min_length=1, max_length=50)

    @field_validator("query")
    @classmethod
    def sanitize_query(cls, value: str) -> str:
        if not re.match(r"^[a-zA-Z0-9\s\-]+$", value):
            raise ValueError("Caracteres no permitidos en el criterio de búsqueda.")
        return value

class TransactionCreateDTO(BaseModel):
    product_id: str = Field(..., pattern=r"^SKU\-[0-9]{3,6}$")
    amount: float = Field(..., gt=0.0, le=50000.0)

    class Config:
        extra = "forbid"

class TransactionResponseDTO(BaseModel):
    transaction_id: int
    store_id: str
    cashier_id: str
    product_id: str
    amount: float
    discount_pct: float
    status: str