from datetime import datetime, timedelta, timezone
import os
from typing import Optional, Union, Literal

import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import models
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Define separate schemes for users and artists
user_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")
artist_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="artists/token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None,
        token_type: Literal["user", "artist"] = "user"
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({
        "exp": expire,
        "token_type": token_type
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_entity(
        token: str,
        db: Session,
        token_type: Literal["user", "artist", "label", "admin"]
) -> Union[models.User, models.Artist]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        entity_id: str = payload.get("sub")
        token_type_from_payload: str = payload.get("token_type")

        if entity_id is None:
            raise credentials_exception

        # Verify token type matches expected type
        if token_type_from_payload != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {token_type} token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except jwt.InvalidTokenError:
        raise credentials_exception

    # Query appropriate model based on token type
    if token_type == "user":
        entity = db.query(models.User).filter(models.User.id == entity_id).first()
    else:
        entity = db.query(models.Artist).filter(models.Artist.id == entity_id).first()

    if entity is None:
        raise credentials_exception

    return entity
