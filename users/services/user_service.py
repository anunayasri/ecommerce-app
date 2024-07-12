from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass
from db.repository import UserRepo
from db.sql_repository import User as UserModel
from sqlalchemy.exc import NoResultFound
from services import exceptions

@dataclass
class User:
    id: Optional[int] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# class User:
#     def __init__(
#         self,
#         id: Optional[int],
#         username: str,
#         first_name: str,
#         last_name: str,
#         email: str,
#         created_at: Optional[datetime],
#         updated_at: Optional[datetime],
#     ) -> None:
#
#         self.id = id
#         self.username = username
#         self.first_name = first_name
#         self.last_name = last_name
#         self.email = email
#         self.created_at = created_at
#         self.updated_at = updated_at


class UserService:
    def __init__(self, repository: UserRepo) -> None:
        self.repository = repository

    def create_user(self, user: User):
        userModel = _userEntity_to_userModel(user)
        self.repository.create_user(userModel)

    def get_user_by_username(self, username) -> Optional[User]:
        try:
            user_model = self.repository.get_user_by_username(username)
            return _userModel_to_userEntity(user_model)
        except NoResultFound:
            return None
            # raise exceptions.NoResultFound(f"No user found for username: {username}")



def _userModel_to_userEntity(user_model: UserModel) -> User:
    attr_list: List[str] = [
        'id', 'username', 'first_name', 'last_name', 'email', 'created_at',
        'updated_at',
    ]
    user_entity = User()

    for attr in attr_list:
        if hasattr(user_model, attr):
            setattr(user_entity, attr, getattr(user_model, attr))

    return user_entity


def _userEntity_to_userModel(user_entity: User) -> UserModel:
    attr_list: List[str] = [
        'id', 'username', 'first_name', 'last_name', 'email', 'created_at',
        'updated_at',
    ]
    user_model = UserModel()

    for attr in attr_list:
        if hasattr(user_entity, attr):
            setattr(user_model, attr, getattr(user_entity, attr))

    return user_model
