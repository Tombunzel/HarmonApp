from datetime import date
from typing import Optional

from pydantic import BaseModel


class UserPaymentMethodBase(BaseModel):
    user_id: int
    type: str
    provider: str
    expiry_date: str
    is_default: bool


class UserPaymentMethodCreate(UserPaymentMethodBase):
    account_number: str
    cvv: str
    shipping_address: str
    billing_address: str
    phone_number: str


class UserPaymentMethodUpdate(BaseModel):
    user_id: Optional[int] = None
    type: Optional[str] = None
    provider: Optional[str] = None
    account_number: Optional[str] = None
    expiry_date: Optional[str] = None
    cvv: Optional[str] = None
    shipping_address: Optional[str] = None
    billing_address: Optional[str] = None
    phone_number: Optional[str] = None
    is_default: Optional[bool] = None


class UserPaymentMethodResponse(UserPaymentMethodBase):
    id: int

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat()
        }
