from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from HarmonApp import models
from HarmonApp.datamanager.database import get_db
from HarmonApp.routes.user import get_current_active_user, get_current_admin_user
from HarmonApp.schemas import user_payment_method_schemas

router = APIRouter(
    prefix="/user_payment_methods",
    tags=["user_payment_methods"]
)


@router.post("/", response_model=user_payment_method_schemas.UserPaymentMethodResponse,
             status_code=status.HTTP_201_CREATED)
def create_user_payment_method(
        current_user: Annotated[models.User, Depends(get_current_active_user)],
        user_payment_method: user_payment_method_schemas.UserPaymentMethodCreate,
        db: Session = Depends(get_db)
):
    db_user_payment_method = models.UserPaymentMethod(
        user_id=user_payment_method.user_id,
        type=user_payment_method.type,
        provider=user_payment_method.provider,
        account_number=user_payment_method.account_number,
        expiry_date=user_payment_method.expiry_date,
        cvv=user_payment_method.cvv,
        shipping_address=user_payment_method.shipping_address,
        billing_address=user_payment_method.billing_address,
        phone_number=user_payment_method.phone_number,
        is_default=user_payment_method.is_default
    )

    try:
        db.add(db_user_payment_method)
        db.commit()
        db.refresh(db_user_payment_method)
        return db_user_payment_method
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment method already exists"
        )


@router.get("/me", response_model=List[user_payment_method_schemas.UserPaymentMethodResponse])
async def read_user_payment_methods_me(
        current_user: Annotated[models.User, Depends(get_current_active_user)],
        db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user_payment_methods = (
        db.query(models.UserPaymentMethod)
        .filter(models.UserPaymentMethod.user_id == current_user.id).all()
    )
    if not user_payment_methods:
        return []

    return user_payment_methods


@router.get("/", response_model=List[user_payment_method_schemas.UserPaymentMethodResponse])
def get_user_payment_methods(
        current_admin: Annotated[models.User, Depends(get_current_admin_user)],
        payment_method_id: int,
        db: Session = Depends(get_db)
):
    query = db.query(models.UserPaymentMethod)

    user_payment_method = query.filter(models.UserPaymentMethod.id == payment_method_id).first()
    if user_payment_method is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )

    return [user_payment_method]  # Return as a list for consistent response model


@router.put("/{payment_method_id}", response_model=user_payment_method_schemas.UserPaymentMethodResponse)
def update_user_payment_method(
        current_user: Annotated[models.User, Depends(get_current_active_user)],
        payment_method_id: int,
        user_payment_method: user_payment_method_schemas.UserPaymentMethodUpdate,
        db: Session = Depends(get_db)
):
    db_user_payment_method = (db.query(models.UserPaymentMethod)
                              .filter(models.UserPaymentMethod.id == payment_method_id)
                              .first())

    if current_user.id != db_user_payment_method.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this payment method"
        )

    if db_user_payment_method is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )

    update_data = user_payment_method.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_user_payment_method, key, value)

    try:
        db.commit()
        db.refresh(db_user_payment_method)
        return db_user_payment_method
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integrity Error"
        )


@router.delete("/{payment_method_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_payment_method(
        current_user: Annotated[models.User, Depends(get_current_active_user)],
        current_admin: Annotated[models.User, Depends(get_current_admin_user)],
        payment_method_id: int,
        db: Session = Depends(get_db)):
    db_payment_method = (db.query(models.UserPaymentMethod)
                         .filter(models.UserPaymentMethod.id == payment_method_id)
                         .first())

    if current_user.id != db_payment_method.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this payment method"
        )

    if db_payment_method is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )

    db.delete(db_payment_method)
    db.commit()
    return None
