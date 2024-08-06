from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr

class GetUserSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: EmailStr

    model_config = ConfigDict(extra="forbid")
