from datetime import date
from typing import Optional

from pydantic import BaseModel


class TrackBase(BaseModel):
    artist_id: int
    album_id: int
    name: str
    release_date: date
    price: float
    path: str


class TrackCreate(TrackBase):
    pass


class TrackUpdate(BaseModel):
    artist_id: Optional[int] = None
    album_id: Optional[int] = None
    name: Optional[str] = None
    release_date: Optional[date] = None
    price: Optional[float] = None
    path: Optional[str] = None


class TrackResponse(TrackBase):
    id: int

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat()
        }
