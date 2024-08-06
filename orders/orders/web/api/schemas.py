from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import field_validator, Field, ConfigDict, BaseModel
from typing_extensions import Annotated


class Size(Enum):
    small = "small"
    medium = "medium"
    big = "big"


class Status(Enum):
    created = "created"
    paid = "paid"
    progress = "progress"
    cancelled = "cancelled"
    dispatched = "dispatched"
    delivered = "delivered"


class OrderItemSchema(BaseModel):
    product: str
    size: Size
    quantity: Optional[Annotated[int, Field(ge=1, strict=True)]] = 1
    model_config = ConfigDict(extra="forbid")

    @field_validator("quantity")
    @classmethod
    def quantity_non_nullable(cls, value):
        assert value is not None, "quantity may not be None"
        return value


class CreateOrderSchema(BaseModel):
    order: Annotated[List[OrderItemSchema], Field(min_length=1)]
    model_config = ConfigDict(extra="forbid")


class GetOrderSchema(CreateOrderSchema):
    id: UUID
    created: datetime
    status: Status


class GetOrdersSchema(BaseModel):
    orders: List[GetOrderSchema]
    model_config = ConfigDict(extra="forbid")
