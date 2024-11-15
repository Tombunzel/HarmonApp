from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from HarmonApp import models
from HarmonApp.datamanager.database import get_db
from HarmonApp.routes.user import get_current_admin_user, get_current_active_user
from HarmonApp.schemas import order_items_schemas, order_schemas

router = APIRouter(
    prefix="/order_items",
    tags=["order_items"]
)


def get_item_price(db: Session, item_id: int, item_type: str) -> float:
    if item_type == "track":
        return db.query(models.Track.price).filter(models.Track.id == item_id).scalar()
    elif item_type == "album":
        return db.query(models.Album.price).filter(models.Album.id == item_id).scalar()
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid item type")


def calculate_subtotal(quantity: int, price: float) -> float:
    return quantity * price


def get_order_total(db: Session, order_id: int) -> float:
    subtotals = db.query(models.OrderItem.subtotal).filter(models.OrderItem.order_id == order_id).all()
    return sum(subtotal[0] for subtotal in subtotals)


@router.post("/", response_model=order_items_schemas.OrderItemResponse, status_code=status.HTTP_201_CREATED)
def create_order_item(
    current_admin: Annotated[models.User, Depends(get_current_admin_user)],
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    order_item: order_items_schemas.OrderItemCreate,
    db: Session = Depends(get_db)
):
    price = get_item_price(db, order_item.item_id, order_item.type)
    subtotal = calculate_subtotal(order_item.quantity, price)

    db_order_item = models.OrderItem(
        order_id=order_item.order_id,
        item_id=order_item.item_id,
        type=order_item.type,
        quantity=order_item.quantity,
        price=price,
        subtotal=subtotal
    )

    try:
        db.add(db_order_item)
        db.commit()
        db.refresh(db_order_item)

        # Update the order's total
        db_order = db.query(models.Order).filter(models.Order.id == db_order_item.order_id).first()
        db_order.total = get_order_total(db, db_order_item.order_id)
        db.add(db_order)
        db.commit()

        return db_order_item
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad request, check input"
        )


@router.get("/", response_model=List[order_items_schemas.OrderItemResponse])
def get_order_items(
        current_admin: Annotated[models.User, Depends(get_current_admin_user)],
        current_user: Annotated[models.User, Depends(get_current_active_user)],
        order_id: int,
        db: Session = Depends(get_db)
):
    query = db.query(models.OrderItem)
    order_items = query.filter(models.OrderItem.order_id == order_id).all()
    order = db.query(models.Order).filter(models.Order.id == order_id).first()

    if current_user.id != order.user_id or current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to see this order's items"
        )

    if order_items is None:
        return []

    return order_items  # Return as a list for consistent response model


@router.put("/{order_item_id}", response_model=order_items_schemas.OrderItemResponse)
def update_order_item(
        current_admin: Annotated[models.User, Depends(get_current_admin_user)],
        current_user: Annotated[models.User, Depends(get_current_active_user)],
        order_item_id: int,
        order_item: order_items_schemas.OrderItemUpdate,
        db: Session = Depends(get_db)
):
    db_order_item = db.query(models.OrderItem).filter(models.OrderItem.id == order_item_id).first()
    order = db.query(models.Order).filter(models.Order.id == db_order_item.order_id).first()

    if current_user.id != order.user_id or current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this item"
        )

    if db_order_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order item not found"
        )

    update_data = order_item.dict(exclude_unset=True)

    # Update price and subtotal if item_id or type is changed
    if "item_id" in update_data or "type" in update_data:
        price = get_item_price(db,
                               update_data.get("item_id", db_order_item.item_id),
                               update_data.get("type", db_order_item.type)
                               )
        db_order_item.price = price
        db_order_item.subtotal = calculate_subtotal(db_order_item.quantity, price)
    elif "quantity" in update_data:
        db_order_item.subtotal = calculate_subtotal(update_data["quantity"], db_order_item.price)

    for key, value in update_data.items():
        setattr(db_order_item, key, value)

    try:
        db.commit()
        db.refresh(db_order_item)

        # Update the order's total
        db_order = db.query(models.Order).filter(models.Order.id == db_order_item.order_id).first()
        db_order.total = get_order_total(db, db_order_item.order_id)
        db.add(db_order)
        db.commit()
        return db_order_item

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Update conflict"
        )


@router.delete("/{order_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_item(
        current_admin: Annotated[models.User, Depends(get_current_admin_user)],
        current_user: Annotated[models.User, Depends(get_current_active_user)],
        order_item_id: int,
        db: Session = Depends(get_db)
):
    db_order_item = db.query(models.OrderItem).filter(models.OrderItem.id == order_item_id).first()
    order = db.query(models.Order).filter(models.Order.id == db_order_item.order_id).first()

    if current_user.id != order.user_id or current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this item"
        )

    if db_order_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order item not found"
        )

    db.delete(db_order_item)
    db.commit()

    # Update the order's total
    order.total = get_order_total(db, order.id)
    db.add(order)
    db.commit()
    return None
