from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import field_validator, Field, ConfigDict, BaseModel
from typing_extensions import Annotated
from orders.orders_service.orders import OrderStatus


# class OrderStatus(Enum):
#     CREATED = "CREATED"
#     PAID = "PAID"
#     PROGRESS = "PROGRESS"
#     CANCELLED = "CANCELLED"
#     DISPATCHED = "DISPATCHED"
#     DELIVERED = "DELIVERED"


class OrderItemSchema(BaseModel):
    product_id: int
    quantity: Optional[Annotated[int, Field(ge=1, strict=True)]] = 1
    model_config = ConfigDict(extra="forbid")

    @field_validator("quantity")
    @classmethod
    def quantity_non_nullable(cls, value):
        assert value is not None, "quantity may not be None"
        return value


class CreateOrderSchema(BaseModel):
    items: Annotated[List[OrderItemSchema], Field(min_length=1)]
    model_config = ConfigDict(extra="forbid")


class GetOrderSchema(CreateOrderSchema):
    id: int
    created_at: datetime
    status: OrderStatus


class GetOrdersSchema(BaseModel):
    orders: List[GetOrderSchema]
    model_config = ConfigDict(extra="forbid")
