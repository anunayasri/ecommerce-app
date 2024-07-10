from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import DeclarativeBase, Mapped, Session
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.engine import Engine
from db.repository import OrderSrvRepo

class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Order(Base):
    '''
    id: int
    buyer_id: int
    address_id: int
    payable: float
    payable_currency: str
    status: str : CREATED, PAYMENT_FAILED, PAYMENT_SUCCESS
    created_at: datetime
    updated_at: datetime
    '''
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    buyer_id: Mapped[int] = mapped_column()

    def __repr__(self) -> str:
        return  f"Order(id: {self.id}, buyer_id: {self.buyer_id})"


class OrderSrvSQLRepo(OrderSrvRepo):
    def __init__(self, engine: Engine):
        self.engine = engine

    def create_order(self, order: Order):
        with Session(self.engine) as session:
            session.add(order)
            session.commit()

    def get_order_by_id(self, order_id: int) -> Order:
        with Session(self.engine) as session:
            stmt = select(Order).where(Order.id.in_([order_id]))
            ord = session.scalars(stmt).one()
            return ord

