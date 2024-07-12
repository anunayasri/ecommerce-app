from datetime import datetime
from sqlalchemy import DateTime, String, Integer
from sqlalchemy import select, func
from sqlalchemy.orm import DeclarativeBase, Mapped, Session
from sqlalchemy.orm import mapped_column
from sqlalchemy.engine import Engine
from db.repository import UserRepo

class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class User(Base):
    '''
    id: int
    username: str
    first_name: str
    last_name: str
    email: str
    status: str : INIT, ACTIVE, BLOCKED
    created_at: datetime
    updated_at: datetime
    '''
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    first_name: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    last_name: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=True)

    def __repr__(self) -> str:
        return  f"User(username: {self.username}, email: {self.email})"


class UserSQLRepo(UserRepo):
    def __init__(self, engine: Engine):
        self.engine = engine

    def create_user(self, user: User):
        with Session(self.engine) as session:
            session.add(user)
            session.commit()

    def get_user_by_username(self, username: str) -> User:
        with Session(self.engine) as session:
            stmt = select(User).where(User.username == username)
            user = session.scalars(stmt).one()
            return user

