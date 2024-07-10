# TODO: explicit imports
from dataclasses import dataclass
from db.repository import OrderSrvRepo
from db.sql_repository import Order as OrderModel
from sqlalchemy.exc import NoResultFound
from services import exceptions

@dataclass
class Order:
    id: int = 0
    buyer_id: int = 0
    # created_at: datetime = datetime.now()
    # updated_at: datetime = datetime.now()


class OrderService:
    def __init__(self, repository: OrderSrvRepo) -> None:
        self.repository = repository

    def create_order(self, order: Order):
        orderModel = _orderEntity_to_orderModel(order)
        self.repository.create_order(orderModel)

    def get_order_by_id(self, order_id) -> Order:
        try:
            orderModel = self.repository.get_order_by_id(order_id)
        except NoResultFound:
            raise exceptions.NoResultFound(f"No order found for id: {order_id}")

        return _orderModel_to_orderEntity(orderModel)


def _orderModel_to_orderEntity(ordModel: OrderModel) -> Order:
    return Order(
        id=ordModel.id,
        buyer_id=ordModel.buyer_id,
        # created_at=ordModel.created_at,
        # updated_at=ordModel.updated_at
    )

def _orderEntity_to_orderModel(ordEntity: Order) -> OrderModel:
    return OrderModel(
        id=ordEntity.id,
        buyer_id=ordEntity.buyer_id,
        # created_at=ordEntity.created_at,
        # updated_at=ordEntity.updated_at
    )
