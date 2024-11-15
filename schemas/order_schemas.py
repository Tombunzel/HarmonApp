from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel


class OrderBase(BaseModel):
    user_id: int
    payment_method_id: int


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    payment_method_id: Optional[int] = None


class OrderResponse(OrderBase):
    id: int
    status: str
    order_date: datetime
    total: float

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat()
        }
