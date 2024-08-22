import sqlalchemy.orm as so
from datetime import datetime

Base = so.declarative_base()

class UserModel(Base):
    __tablename__ = 'users'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    first_name: so.Mapped[str]
    last_name: so.Mapped[str]
    username: so.Mapped[str] = so.mapped_column(unique=True)
    email: so.Mapped[str] = so.mapped_column(unique=True)
    hashed_password: so.Mapped[str]
    created_at: so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow)
    updated_at: so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<User id:{self.id} first_name:{self.first_name} " + \
            f"last_name:{self.last_name} username:{self.username}>"
