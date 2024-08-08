from orders.orders_service.exceptions import OrderNotFoundException
from orders.repository.orders_repository import OrdersRepository


class OrdersService:
    def __init__(self, orders_repository: OrdersRepository):
        self.orders_repository = orders_repository

    def place_order(self, items, user_id):
        return self.orders_repository.add(items, user_id)

    def get_order(self, order_id, **filters):
        return self.orders_repository.get_order(order_id, **filters)


    def list_orders(self, **filters):
        limit = filters.pop("limit", None)
        return self.orders_repository.list_orders(limit=limit, **filters)

   
    # def cancel_order(self, order_id, user_id):
    #     order = self.orders_repository.get(order_id, user_id=user_id)
    #     if order is None:
    #         raise OrderNotFoundException(f"Order with id {order_id} not found")
    #     order.cancel()
    #     return self.orders_repository.update(order_id, status="cancelled")

