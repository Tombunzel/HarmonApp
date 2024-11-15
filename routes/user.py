from datetime import timedelta
from typing import List, Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import models
from datamanager.database import get_db
from schemas import user_schemas
from schemas.user_schemas import UserRole
from auth_utils import (
    verify_password,
    create_access_token,
    get_current_entity,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_user_scheme = OAuth2PasswordBearer(tokenUrl="users/token", scheme_name="UserAuth")


# Security utility functions
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_admin_user(db: Session, user_data: user_schemas.UserCreate):
    hashed_password = get_password_hash(user_data.password)
    db_user = models.User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password,
        name=user_data.name,
        date_of_birth=user_data.date_of_birth,
        role=UserRole.ADMIN,
        disabled=False
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )


async def get_current_user(
    token: Annotated[str, Depends(oauth2_user_scheme)],
    db: Session = Depends(get_db)
) -> models.User:
    return get_current_entity(token, db, "user")


async def get_current_active_user(
        current_user: Annotated[models.User, Depends(get_current_user)]
) -> models.User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin_user(
    current_user: Annotated[models.User, Depends(get_current_active_user)]
) -> models.User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access this endpoint"
        )
    return current_user


# Authentication endpoints
@router.post("/token", response_model=user_schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
) -> user_schemas.Token:
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="user"
    )
    return user_schemas.Token(access_token=access_token, token_type="bearer")


@router.post("/admin", response_model=user_schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_new_admin(
    user: user_schemas.UserCreate,
    current_user: Annotated[models.User, Depends(get_current_admin_user)],
    db: Session = Depends(get_db)
):
    """
    Create a new admin user. Only existing admins can create new admins.
    """
    return create_admin_user(db, user)


# User management endpoints
@router.post("/", response_model=user_schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)

    db_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        name=user.name,
        date_of_birth=user.date_of_birth,
        role=UserRole.USER,  # Explicitly set role to USER
        disabled=False
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )


@router.get("/me", response_model=user_schemas.UserResponse)
async def read_users_me(
        current_user: Annotated[models.User, Depends(get_current_active_user)]
):
    return current_user


@router.get("/", response_model=List[user_schemas.UserResponse])
def get_users(
    current_user: Annotated[models.User, Depends(get_current_admin_user)],
    user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(models.User)

    if user_id is not None:
        user = query.filter(models.User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return [user]

    return query.offset(skip).limit(limit).all()


@router.put("/{user_id}", response_model=user_schemas.UserResponse)
def update_user(
        user_id: int,
        user: user_schemas.UserUpdate,
        current_user: Annotated[models.User, Depends(get_current_active_user)],
        db: Session = Depends(get_db)
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this user"
        )

    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    update_data = user.dict(exclude_unset=True)

    # Only allow role updates if the current user is an admin
    if "role" in update_data and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can modify user roles"
        )

    if "password" in update_data:
        update_data["password"] = get_password_hash(update_data["password"])

    for key, value in update_data.items():
        setattr(db_user, key, value)

    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
        user_id: int,
        current_user: Annotated[models.User, Depends(get_current_active_user)],
        db: Session = Depends(get_db)
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )

    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(db_user)
    db.commit()
    return None
