import sqlalchemy as sa
import sqlalchemy.orm as so
from datetime import datetime
import enum

class Base(so.DeclarativeBase):
    pass

class UserRole(enum.Enum):
    BUYER = "BUYER"
    SELLER = "SELLER"

class User(Base):
    __tablename__ = 'users'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    first_name: so.Mapped[str]
    last_name: so.Mapped[str]
    username: so.Mapped[str] = so.mapped_column(unique=True)
    email: so.Mapped[str] = so.mapped_column(unique=True)
    hashed_password: so.Mapped[str]

    role: so.Mapped[UserRole]

    created_at: so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow)
    updated_at: so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<User id:{self.id} first_name:{self.first_name} " + \
            f"last_name:{self.last_name} username:{self.username}>"


class BuyerProfile(Base):
    __tablename__ = 'buyer_profile'

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"), primary_key=True)
    user: so.Mapped["User"] = so.relationship()
    shipping_address: so.Mapped[str]


class SellerProfile(Base):
    __tablename__ = 'seller_profile'

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"), primary_key=True)
    user: so.Mapped["User"] = so.relationship()
    store_name: so.Mapped[str]
