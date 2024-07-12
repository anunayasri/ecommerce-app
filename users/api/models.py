# from pydantic.dataclasses import dataclass
from pydantic import BaseModel, field_serializer
from datetime import datetime
from services.user_service import User

# @dataclass
class CreateUserReq(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str

# @dataclass
class UserResp(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    email: str
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at')
    def serialize_created_at(self, dt: datetime, _info):
        return dt.isoformat()

    @field_serializer('updated_at')
    def serialize_updated_at(self, dt: datetime, _info):
        return dt.isoformat()


def User_to_UserResp(user: User) -> UserResp:
    return UserResp(
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        created_at=user.created_at,
        updated_at=user.updated_at,

    )
