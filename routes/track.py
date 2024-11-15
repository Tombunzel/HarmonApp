from typing import List, Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from HarmonApp import models
from HarmonApp.datamanager.database import get_db
from HarmonApp.routes.artist import get_current_active_artist, get_current_admin_user
from HarmonApp.schemas import track_schemas

router = APIRouter(
    prefix="/tracks",
    tags=["tracks"]
)


@router.post("/", response_model=track_schemas.TrackResponse, status_code=status.HTTP_201_CREATED)
def create_track(
        current_artist: Annotated[models.Artist, Depends(get_current_active_artist)],
        track: track_schemas.TrackCreate,
        db: Session = Depends(get_db),
):

    db_track = models.Track(
        artist_id=track.artist_id,
        album_id=track.album_id,
        name=track.name,
        release_date=track.release_date,
        price=track.price,
        path=track.path
    )

    try:
        db.add(db_track)
        db.commit()
        db.refresh(db_track)
        return db_track
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad request, check input"
        )


@router.get("/", response_model=List[track_schemas.TrackResponse])
def get_tracks(
        track_id: Optional[int] = None, skip: int = 0, limit: int = 100,
        db: Session = Depends(get_db)
):
    query = db.query(models.Track)

    if track_id is not None:
        track = query.filter(models.Track.id == track_id).first()
        if track is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Track not found"
            )
        return [track]  # Return as a list for consistent response model

    return query.offset(skip).limit(limit).all()


@router.put("/{track_id}", response_model=track_schemas.TrackResponse)
def update_track(
        current_artist: Annotated[models.Artist, Depends(get_current_active_artist)],
        current_user: Annotated[models.User, Depends(get_current_admin_user)],
        track_id: int, track: track_schemas.TrackUpdate,
        db: Session = Depends(get_db)
):
    db_track = db.query(models.Track).filter(models.Track.id == track_id).first()

    if db_track.artist_id != current_artist.id or current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this track"
        )

    if db_track is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found"
        )

    update_data = track.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_track, key, value)

    try:
        db.commit()
        db.refresh(db_track)
        return db_track
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Track already exists"
        )


@router.delete("/{track_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_track(
        current_artist: Annotated[models.Artist, Depends(get_current_active_artist)],
        current_user: Annotated[models.User, Depends(get_current_admin_user)],
        track_id: int,
        db: Session = Depends(get_db)
):
    db_track = db.query(models.Track).filter(models.Track.id == track_id).first()

    if db_track.artist_id != current_artist.id or current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this track"
        )

    if db_track is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found"
        )

    db.delete(db_track)
    db.commit()
    return None
