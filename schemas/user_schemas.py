from datetime import date, datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class UserBase(BaseModel):
    username: str
    email: EmailStr
    name: str
    date_of_birth: date
    role: UserRole = UserRole.USER  # Default role is regular user


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    date_of_birth: Optional[date] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    disabled: bool = False

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat()
        }
