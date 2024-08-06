import sqlalchemy as sa
from repository.models import UserModel
from repository.users_repository import UsersRepository
from users_service.entities import User
from users_service.exceptions import UserNotFoundException

class UsersSQLRepository(UsersRepository):
    def __init__(self, session):
        self.session = session

    def get_user_by_username(self, username: str) -> User:
        stmt = sa.select(UserModel).where(UserModel.username == username)
        user_model = self.session.scalars(stmt).one_or_none()
        if not user_model:
            raise UserNotFoundException()

        return _UserModel_to_User(user_model)


    def add(self, user: User) -> User:
        """Creates a user in the DB. Returns the User object having DB generated
        values like id, created_at, updated_at etc.
        """
        user_model = _User_to_UserModel(user)
        self.session.add(user_model)
        self.session.commit()

        return _UserModel_to_User(user_model)


def _UserModel_to_User(user_model: UserModel) -> User:
    return User(
        id=user_model.id,
        first_name=user_model.first_name,
        last_name=user_model.last_name,
        email=user_model.email,
        username=user_model.username,
        hashed_password=user_model.hashed_password,
        created_at=user_model.created_at,
        updated_at=user_model.updated_at,
    )

def _User_to_UserModel(user: User) -> UserModel:
    return UserModel(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        username=user.username,
        hashed_password=user.hashed_password,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
