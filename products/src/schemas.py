from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import enum

class GetProductSchema(BaseModel):
    id: int
    title: str 
    description: str
    user_id: int 
    quantity: int
    created_at: datetime


class CreateProductSchema(BaseModel):
    title: str
    description: str
    quantity: Optional[int] = 1

class ProductStatus(enum.Enum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'

class UpdateProductSchema(BaseModel):
    title: str
    description: str
    quantity: int
    status: Optional[ProductStatus] = None

