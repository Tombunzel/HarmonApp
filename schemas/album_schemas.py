from datetime import date
from typing import Optional, List

from pydantic import BaseModel


class AlbumBase(BaseModel):
    artist_id: int
    name: str
    release_date: date
    price: float


class AlbumCreate(AlbumBase):
    pass


class AlbumUpdate(BaseModel):
    artist_id: Optional[int] = None
    name: Optional[str] = None
    release_date: Optional[date] = None
    price: Optional[float] = None


class AlbumTrackResponse(BaseModel):
    artist_id: int
    name: str
    release_date: date
    price: float
    path: str

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat()
        }


class AlbumTracksResponse(BaseModel):
    album_id: int
    tracks: List[AlbumTrackResponse]

    class Config:
        from_attributes = True


class AlbumResponse(AlbumBase):
    id: int

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat()
        }
