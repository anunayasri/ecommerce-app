import uuid
from datetime import datetime
import enum
from typing import List

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
import sqlalchemy.dialects.postgresql as pg
import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from orders.orders_service.orders import OrderStatus

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class OrderModel(Base):
    __tablename__ = "orders"

    # TODO: Use type UUID. 
    # uuid DB type?
    id: so.Mapped[str] = so.mapped_column(primary_key=True, default=generate_uuid)
    user_id: so.Mapped[int]
    # Using OrderStatus from the service layer
    status: so.Mapped[OrderStatus]
    created_at: so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow)
    updated_at: so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow)

    items: so.Mapped[List["OrderItemModel"]] = relationship(back_populates="order")

    def dict(self):
        return {
            "id": self.id,
            "items": [item.dict() for item in self.items],
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class OrderItemModel(Base):
    __tablename__ = "order_items"

    id: so.Mapped[str] = so.mapped_column(primary_key=True, default=generate_uuid)
    order_id: so.Mapped[str] = so.mapped_column(sa.ForeignKey('orders.id'))
    order: so.Mapped["OrderModel"] = relationship(back_populates="items")
    product_id: so.Mapped[int]  # product_id from product service
    quantity: so.Mapped[int]

    def dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "quantity": self.quantity,
        }
