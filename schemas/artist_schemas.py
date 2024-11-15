from datetime import date, datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class ArtistRole(str, Enum):
    ARTIST = "artist"
    LABEL = "label"


class ArtistBase(BaseModel):
    username: str
    email: EmailStr
    name: str
    genre: str
    role: ArtistRole = ArtistRole.ARTIST  # Default role is regular artist


class ArtistCreate(ArtistBase):
    password: str


class ArtistUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[ArtistRole] = None


class ArtistResponse(ArtistBase):
    id: int
    created_at: datetime
    disabled: bool = False

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat()
        }
