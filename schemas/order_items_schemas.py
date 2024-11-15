from datetime import date
from typing import Optional

from pydantic import BaseModel


class OrderItemBase(BaseModel):
    order_id: int
    item_id: int
    type: str
    quantity: int


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemUpdate(BaseModel):
    item_id: Optional[int] = None
    type: Optional[str] = None
    quantity: Optional[int] = None


class OrderItemResponse(OrderItemBase):
    id: int
    price: float
    subtotal: float

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat()
        }
