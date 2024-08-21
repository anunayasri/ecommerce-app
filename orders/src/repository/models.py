from datetime import datetime
from typing import List

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
import sqlalchemy.dialects.postgresql as pg
import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy.orm import DeclarativeBase, relationship
from orders_service.orders import OrderStatus


class Base(so.DeclarativeBase):
    pass


class OrderModel(Base):
    __tablename__ = "orders"

    id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)
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

    def __repr__(self):
        return f"<Order id:{self.id} status:{self.status} " + \
        f"created_at: {self.created_at}>"


class OrderItemModel(Base):
    __tablename__ = "order_items"

    id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)
    order_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('orders.id'))
    order: so.Mapped["OrderModel"] = relationship(back_populates="items")
    product_id: so.Mapped[int]  # product_id from product service
    quantity: so.Mapped[int]

    def dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "quantity": self.quantity,
        }

    def __repr__(self):
        return f"<OrderItem id:{self.id} product_id:{self.product_id} " + \
        f"quantity: {self.quantity}>"
