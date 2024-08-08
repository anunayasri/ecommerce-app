from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import sqlalchemy as sa

from orders.orders_service.orders_service import OrdersService
from orders.orders_service.orders import Order, OrderItem, OrderStatus
from orders.repository.orders_repository import OrdersRepository
from orders.repository.models import Base, OrderModel, OrderItemModel


engine = create_engine("sqlite:///orders.db", echo=True)

Base.metadata.create_all(engine)


with Session(engine) as session:
    repo = OrdersRepository(session)
    ord_srv = OrdersService(repo)

    _order_items = [
        OrderItem(product_id=1, quantity=3),
        OrderItem(product_id=2, quantity=10),
    ]

    # order = ord_srv.place_order(_order_items, 1)

    order_id = '94450d5f-1e95-4064-a710-0581e2e55320'
    # order = ord_srv.get_order(order_id)
    orders = ord_srv.list_orders(limit=10)

    # items = [
    #     OrderItemModel(product_id=1, quantity=3),
    #     OrderItemModel(product_id=2, quantity=10),
    # ]
    #
    # order = OrderModel(items=items, status='CREATED', user_id=1)
    #
    # session.add(order)

    session.commit()

    # stmt = sa.select(OrderModel).where(OrderModel.id == '94450d5f-1e95-4064-a710-0581e2e55320')
    # order = session.scalars(stmt).one_or_none()

    # print(f"OrderId: {order.id}")

    print([order.id for order in orders])
