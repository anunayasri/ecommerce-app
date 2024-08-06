from datetime import datetime

class User:
    def __init__(
            self, 
            first_name:str, 
            last_name: str,
            username: str, 
            email: str, 
            hashed_password: str,
            id: int | None = None,
            created_at : datetime | None = None,
            updated_at : datetime | None = None,
    ):
        self._id = id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.created_at = None
        self.updated_at = None

    @property
    def id(self):
        return self._id

    def __repr__(self) -> str:
        return f"User<id={self.id} username={self.username} email={self.email}>"


