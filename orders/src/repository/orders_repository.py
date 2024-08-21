from typing import List
from orders_service.orders import Order, OrderItem, OrderStatus
from repository.models import OrderModel, OrderItemModel
from orders_service.exceptions import OrderNotFoundException
import sqlalchemy as sa

# The repository layer should not expose internal dependencies to business layer.
# Return Order entity instead of OrderModel which a DB model.
# Similarly, raise exceptions that service layer understands like 
# OrderNotFoundException instead of sqlalchemy's NotFoundException

class OrdersRepository:
    def __init__(self, session):
        self.session = session

    def add(self, items: List[OrderItem], user_id: int) -> Order:
        order_items_for_db = [
            _OrderItem_to_OrderItemModel(item)
            for item in items
        ]
        order_model = OrderModel(
            items=order_items_for_db,
            user_id=user_id,
            status=OrderStatus.CREATED.value,
        )
        self.session.add(order_model)

        # print(f">>>>> om {order_model.id} | {order_model.created_at}")

        # Don't commit the session here
        ord = _OrderModel_to_Order(order_model)

        # print(f">>>>> ord {ord.id} | {ord.created_at}")
        return ord

    def _get(self, id_, **filters):
        return (
            self.session.query(OrderModel)
            .filter(OrderModel.id == str(id_))
            .filter_by(**filters)
        )

    def get_order(self, order_id, **filters):
        order_model = self._get(order_id, **filters).one_or_none()
        if not order_model:
            raise OrderNotFoundException()

        return _OrderModel_to_Order(order_model)


    def list_orders(self, limit=None, **filters):
        # query = self.session.query(OrderModel)
        # records = query.filter_by(**filters).limit(limit).all()
        stmt = sa.select(OrderModel).filter_by(**filters).limit(limit)
        orders = self.session.scalars(stmt).all()

        if not orders:
            raise OrderNotFoundException()

        return [_OrderModel_to_Order(ord) for ord in orders]


    def delete(self, id_):
        self.session.delete(self._get(id_))


def _OrderModel_to_Order(m: OrderModel) -> Order:
    return Order(
        id=m.id,
        status=OrderStatus(m.status),
        items=[_OrderItemModel_to_OrderItem(item) for item in m.items],
        user_id=m.user_id,
        order_=m,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )

def _Order_to_OrderModel(o: Order) -> OrderModel:
    return OrderModel(
        id=o.id,
        status=o.status.value,
        iteos=[_OrderItem_to_OrderItemModel(item) for item in o.items],
        user_id=o.user_id,
        created_at=o.created_at,
        updated_at=o.updated_at,

    )

def _OrderItemModel_to_OrderItem(m: OrderItemModel) -> OrderItem:
    return OrderItem(
        id=m.id,
        product_id=m.product_id,
        quantity=m.quantity,
    )

def _OrderItem_to_OrderItemModel(i: OrderItem) -> OrderItemModel:
    return OrderItemModel(
        id=i.id,
        product_id=i.product_id,
        quantity=i.quantity,
    )
