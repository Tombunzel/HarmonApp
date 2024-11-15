from typing import List, Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from HarmonApp import models
from HarmonApp.datamanager.database import get_db
from HarmonApp.routes.artist import get_current_active_artist
from HarmonApp.schemas import album_schemas

router = APIRouter(
    prefix="/albums",
    tags=["albums"]
)


@router.post("/", response_model=album_schemas.AlbumResponse, status_code=status.HTTP_201_CREATED)
def create_album(
        current_artist: Annotated[models.Artist, Depends(get_current_active_artist)],
        album: album_schemas.AlbumCreate,
        db: Session = Depends(get_db)
):
    db_album = models.Album(
        artist_id=album.artist_id,
        name=album.name,
        release_date=album.release_date,
        price=album.price
    )

    try:
        db.add(db_album)
        db.commit()
        db.refresh(db_album)
        return db_album
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Album already exists"
        )


@router.get("/", response_model=List[album_schemas.AlbumResponse])
def get_albums(
        album_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    query = db.query(models.Album)

    if album_id is not None:
        album = query.filter(models.Album.id == album_id).first()
        if album is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Album not found"
            )
        return [album]  # Return as a list for consistent response model

    return query.offset(skip).limit(limit).all()


@router.get("/{album_id}/tracks", response_model=List[album_schemas.AlbumTrackResponse])
def get_album_tracks(album_id: int, db: Session = Depends(get_db)):
    album = db.query(models.Album).filter(models.Album.id == album_id).first()
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Album not found"
        )

    album_tracks = db.query(models.Track).filter(models.Track.album_id == album_id).all()
    if not album_tracks:
        return []

    return album_tracks


@router.put("/{album_id}", response_model=album_schemas.AlbumResponse)
def update_album(
        current_artist: Annotated[models.Artist, Depends(get_current_active_artist)],
        album_id: int,
        album: album_schemas.AlbumUpdate,
        db: Session = Depends(get_db)
):
    db_album = db.query(models.Album).filter(models.Album.id == album_id).first()

    if current_artist.id != db_album.artist_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this album"
        )

    if db_album is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Album not found"
        )

    update_data = album.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_album, key, value)

    try:
        db.commit()
        db.refresh(db_album)
        return db_album
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Album already exists"
        )


@router.delete("/{album_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_album(
        current_artist: Annotated[models.Artist, Depends(get_current_active_artist)],
        album_id: int,
        db: Session = Depends(get_db)
):
    db_album = db.query(models.Album).filter(models.Album.id == album_id).first()

    if current_artist.id != db_album.artist_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this album"
        )

    if db_album is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Album not found"
        )

    db.delete(db_album)
    db.commit()
    return None
