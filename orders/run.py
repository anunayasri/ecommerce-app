from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from orders.orders_service.orders_service import OrdersService
from orders.repository.orders_repository import OrdersRepository
from orders.repository.models import Base


engine = create_engine("sqlite:///orders.db", echo=True)

# Base.metadata.create_all(engine)


with Session(engine) as session:
    repo = OrdersRepository(session)
    ord_srv = OrdersService(repo)

    _order_items = [
        {'product': 'shirt', 'size': 'M', 'quantity': 3},
        {'product': 'cap', 'size': 'M', 'quantity': 10},
    ]

    _order = ord_srv.place_order(_order_items, '1')
    session.commit()

    print(_order.id)
