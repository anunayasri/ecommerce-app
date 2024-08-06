from abc import ABC, abstractmethod
from users_service.entities import User

class UsersRepository(ABC):
    @abstractmethod
    def get_user_by_username(self, username: str) -> User:
        pass

    @abstractmethod
    def add(self, user: User) -> User:
        """Creates a user in the DB. Returns the User object having DB generated
        values like id, created_at, updated_at etc.
        """
        pass
