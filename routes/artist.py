from datetime import timedelta
from typing import List, Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import models
from datamanager.database import get_db
from routes.user import get_current_admin_user
from schemas import artist_schemas
from schemas.artist_schemas import ArtistRole
from auth_utils import verify_password, create_access_token, get_current_entity, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(
    prefix="/artists",
    tags=["artists"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_artist_scheme = OAuth2PasswordBearer(tokenUrl="artists/token", scheme_name="ArtistAuth")


# Security utility functions
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def get_current_artist(
    token: Annotated[str, Depends(oauth2_artist_scheme)],
    db: Session = Depends(get_db)
) -> models.Artist:
    return get_current_entity(token, db, "artist")


async def get_current_active_artist(
        current_artist: Annotated[models.Artist, Depends(get_current_artist)]
) -> models.Artist:
    if current_artist.disabled:
        raise HTTPException(status_code=400, detail="Inactive artist")
    return current_artist


# Authentication endpoints
@router.post("/token", response_model=artist_schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
) -> artist_schemas.Token:
    artist = db.query(models.Artist).filter(models.Artist.username == form_data.username).first()
    if not artist or not verify_password(form_data.password, artist.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": artist.id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="artist"
    )
    return artist_schemas.Token(access_token=access_token, token_type="bearer")


# Artist management endpoints
@router.post("/", response_model=artist_schemas.ArtistResponse, status_code=status.HTTP_201_CREATED)
def create_artist(artist: artist_schemas.ArtistCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(artist.password)

    db_artist = models.Artist(
        username=artist.username,
        email=artist.email,
        password=hashed_password,
        name=artist.name,
        genre=artist.genre,
        role=ArtistRole.ARTIST,  # Explicitly set role to ARTIST
        disabled=False
    )

    try:
        db.add(db_artist)
        db.commit()
        db.refresh(db_artist)
        return db_artist
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )


@router.get("/me", response_model=artist_schemas.ArtistResponse)
async def read_artists_me(
        current_artist: Annotated[models.Artist, Depends(get_current_active_artist)]
):
    return current_artist


@router.get("/", response_model=List[artist_schemas.ArtistResponse])
def get_artists(
        current_user: Annotated[models.User, Depends(get_current_admin_user)],
        artist_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    query = db.query(models.Artist)

    if artist_id is not None:
        artist = query.filter(models.Artist.id == artist_id).first()
        if artist is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Artist not found"
            )
        return [artist]

    return query.offset(skip).limit(limit).all()


@router.put("/{artist_id}", response_model=artist_schemas.ArtistResponse)
def update_artist(
        current_artist: Annotated[models.Artist, Depends(get_current_active_artist)],
        artist_id: int,
        artist: artist_schemas.ArtistUpdate,
        db: Session = Depends(get_db)
):
    if current_artist.id != artist_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this artist"
        )

    db_artist = db.query(models.Artist).filter(models.Artist.id == artist_id).first()
    if db_artist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found"
        )

    update_data = artist.dict(exclude_unset=True)

    if "password" in update_data:
        update_data["password"] = get_password_hash(update_data["password"])

    for key, value in update_data.items():
        setattr(db_artist, key, value)

    try:
        db.commit()
        db.refresh(db_artist)
        return db_artist
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )


@router.delete("/{artist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_artist(
        artist_id: int,
        current_artist: Annotated[models.Artist, Depends(get_current_active_artist)],
        db: Session = Depends(get_db)
):
    if current_artist.id != artist_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this artist"
        )

    db_artist = db.query(models.Artist).filter(models.Artist.id == artist_id).first()
    if db_artist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found"
        )

    db.delete(db_artist)
    db.commit()
    return None
