from typing import List
from enum import Enum
import uuid
from datetime import datetime

class OrderStatus(Enum):
    CREATED = "CREATED"
    PAID = "PAID"
    PROGRESS = "PROGRESS"
    CANCELLED = "CANCELLED"
    DISPATCHED = "DISPATCHED"
    DELIVERED = "DELIVERED"


class OrderItem:
    def __init__(self, product_id, quantity, id=None):
        self.id = id
        self.product_id = product_id
        self.quantity = quantity

    def dict(self):
        return {
            # "id": self.id,
            "product_id": self.product_id,
            "quantity": self.quantity,
        }


class Order:
    def __init__(
        self,
        items: List[OrderItem],
        status: OrderStatus,
        user_id: int,
        id: uuid.UUID | None,
        created_at: datetime | None,
        updated_at: datetime | None,
        order_ = None,
    ):
        # Fields to be populated by DB/default values on commit: id, created_at, 
        # updated_at.
        # Order entity will not have access to these fields before commit. 
        # We need access to the OrderModel to refresh the data populated by DB.
        # Hence, we have to add coupling with DB layer by storing the DB Model 
        # reference in order_ field.
        # We have used _id, _created_at, _updated_at private fields and getter
        # function. The getter returns the Order entity fields for existing data 
        # in the DB. For new objects, the getter gets the data from order_ 
        # sqlalchemy object.
        self._id = id
        self.order_ = order_  # Instance of OrderModel
        self.items = items
        self.status = status
        self.user_id = user_id
        self._created_at = created_at
        self._updated_at = updated_at

    @property
    def id(self):
        return self._id or self.order_.id

    @property
    def created_at(self):
        return self._created_at or self.order_.created_at

    @property
    def updated_at(self):
        return self._updated_at or self.order_.updated_at

    def dict(self):
        return {
            "id": self.id,
            "items": [item.dict() for item in self.items],
            "status": self.status.value,
            "created_at": self.created_at,
        }
