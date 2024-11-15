from typing import List, Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from HarmonApp import models
from HarmonApp.datamanager.database import get_db
from HarmonApp.routes.user import get_current_active_user, get_current_admin_user
from HarmonApp.schemas import order_schemas

router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)


@router.post("/", response_model=order_schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
        current_user: Annotated[models.User, Depends(get_current_active_user)],
        order: order_schemas.OrderCreate,
        db: Session = Depends(get_db)
):
    db_order = models.Order(
        user_id=order.user_id,
        total=0.0,
        payment_method_id=order.payment_method_id
    )

    try:
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad payment method id"
        )


@router.get("/", response_model=List[order_schemas.OrderResponse])
def get_orders(
        current_user: Annotated[models.User, Depends(get_current_admin_user)],
        order_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    query = db.query(models.Order)

    if order_id is not None:
        order = query.filter(models.Order.id == order_id).first()
        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        return [order]  # Return as a list for consistent response model

    return query.offset(skip).limit(limit).all()


@router.get("/me", response_model=List[order_schemas.OrderResponse])
async def read_orders_me(
        current_user: Annotated[models.User, Depends(get_current_active_user)],
        db: Session = Depends(get_db)
):
    user_orders = (
        db.query(models.Order)
        .filter(models.Order.user_id == current_user.id).all()
    )
    if not user_orders:
        return []

    return user_orders


@router.put("/{order_id}", response_model=order_schemas.OrderResponse)
def update_order(
        current_admin: Annotated[models.User, Depends(get_current_admin_user)],
        current_user: Annotated[models.User, Depends(get_current_active_user)],
        order_id: int,
        order: order_schemas.OrderUpdate,
        db: Session = Depends(get_db)
):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()

    if current_user.id != db_order.user_id or current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this order"
        )

    if db_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    update_data = order.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_order, key, value)

    try:
        db.commit()
        db.refresh(db_order)
        return db_order
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order already exists"
        )


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
        current_admin: Annotated[models.User, Depends(get_current_admin_user)],
        current_user: Annotated[models.User, Depends(get_current_active_user)],
        order_id: int,
        db: Session = Depends(get_db)
):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()

    if current_user.id != db_order.user_id or current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this order"
        )

    if db_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    db.delete(db_order)
    db.commit()
    return None
