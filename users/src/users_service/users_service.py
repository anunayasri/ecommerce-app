from repository.users_repository import UsersRepository
from users_service.entities import User
from users_service.exceptions import UserNotFoundException, InvalidPasswordException
from users_service.auth import verify_password, hash_password

class UsersService:
    def __init__(self, users_repository: UsersRepository):
        self.users_repository = users_repository

    def get_user_by_username(self, username: str) -> User:
        user = self.users_repository.get_user_by_username(username)
        if user is None:
            raise UserNotFoundException(f"User with username {username} not found")

        return user

    def create_user(
        self, 
        first_name: str, 
        last_name: str,
        username: str,
        email: str,
        password: str
    ) -> User:

        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            hashed_password=hash_password(password),
        )
        return self.users_repository.add(user)

    def authenticate_user(self, username: str, password: str) -> User:
        """User with username exists.
        The password is correct.
        Returns a User entity.

        Raises -
            UserNotFoundException: Wrong username
            InvalidPasswordException: Wrong password
        """
        user = self.get_user_by_username(username)

        if not verify_password(password, user.hashed_password):
            raise InvalidPasswordException()

        return user
