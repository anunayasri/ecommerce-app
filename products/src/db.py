import enum
from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.orm as so

class Base(so.DeclarativeBase):
    pass

class ProductStatus(enum.Enum):
    ACTIVE = 'ACTIVE'
    DEACTIVE = 'DEACTIVE'

class Product(Base):
    __tablename__ = "products"

    id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)
    title: so.Mapped[str]
    description: so.Mapped[str]
    user_id: so.Mapped[int]
    status: so.Mapped[ProductStatus]
    quantity: so.Mapped[int]
    created_at: so.Mapped[datetime] = so.mapped_column(server_default=sa.func.current_timestamp())
    updated_at: so.Mapped[datetime] = so.mapped_column(
        server_default=sa.func.current_timestamp(),
        server_onupdate=sa.func.current_timestamp(),
    )
