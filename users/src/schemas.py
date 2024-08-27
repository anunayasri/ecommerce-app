from pydantic import BaseModel, ConfigDict, EmailStr
import enum
from db import UserRole

# class UserRole(enum.Enum):
#     BUYER = "BUYER"
#     SELLER = "SELLER"


class GetUserSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    role: UserRole

    model_config = ConfigDict(extra="forbid")


class CreateUserSchema(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password: str
    role: UserRole

    model_config = ConfigDict(extra="forbid")


class CreateBuyerProfile(BaseModel):
    shipping_address: str

    model_config = ConfigDict(extra="forbid")


class GetBuyerProfile(BaseModel):
    user: GetUserSchema
    shipping_address: str


class CreateSellerProfile(BaseModel):
    store_name: str

    model_config = ConfigDict(extra="forbid")

