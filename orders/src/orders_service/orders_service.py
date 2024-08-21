from typing import List
from datetime import datetime, timedelta
from pathlib import Path
import requests
import jwt
from cryptography.hazmat.primitives import serialization
from orders_service.exceptions import OrderNotFoundException, ProductNotBookedException
from repository.orders_repository import OrdersRepository
from orders_service.orders import OrderItem
from config import AppConfig


class OrdersService:
    def __init__(
        self,
        orders_repository: OrdersRepository,
    ):
        self.orders_repository = orders_repository

    def place_order(self, items: List[OrderItem], user_id: int):
        # book iterms from the product service
        # TODO: Batch api to book items in product service
        PRODUCT_SRV_URL = f"{AppConfig().PRODUCT_SRV_HOST}:{AppConfig().PRODUCT_SRV_PORT}"

        # token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJQUk9EVUNUU19TUlYiLCJpYXQiOjE3MjM1OTU5NDIuMDY0MywiZXhwIjoxNzIzNjgyMzQyLjA2NDMsInVzZXJfaWQiOiIxMDAiLCJyb2xlIjoiT1JERVJfU1JWIn0.Is1RKscGbVRVST7vkGhgW0vGlXASzfvkEhDaH8-d_rOD0QWnN7cvfNrjzZmZULkFw9ZsW26wnV9Vd11rdCDDi7H0jr0IpJV-mbDlyTHan-H2uRCaN2tXsKVt8MPu9XYvO4dodly4JReYg4iGH15F2mK28kfx1j5MYDlQB73PQZR_iZOzVLQgAK3RV4-hN2sM_HU-70INQGxNRw17EhkDogr8NV1PXpoLTVnMaBERmyk8ABas_BZn30iWFcrmk8KvNjldKst4sHYrObUWcUcpnpOlAWnLwdvmHWLMuWg30RSV9mRPmnD5hpRg2V1SKrGAg7sOyzoNdQZvwhmKTJlF5g'

        # TODO: Write orders and order_items to DB in INIT state. 
        # Then call products api. Update the order_items status as per the resp.

        token = gen_token_for_product_srv(AppConfig().AUTH_JWT_PRIVATE_KEY_FILE)
        booked_items = []
        for item in items:
            try:
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                }
                # TODO: Keep the logic to call ProductSrv outside of business logic.
                resp = requests.post(
                    f'{PRODUCT_SRV_URL}/product/{item.product_id}/buy?order_quantity={item.quantity}',
                    headers = headers,
                )
                resp.raise_for_status()
                booked_items.append(item)

            except requests.exceptions.HTTPError as http_err:
                print(f"ERROR: Http error in booking product: {http_err}")
            except requests.exceptions.RequestException as err:
                print(f"ERROR: Error in booking product: {err}")

        if len(booked_items) == 0:
            raise ProductNotBookedException("No items can be booked in product service.")

        return self.orders_repository.add(booked_items, user_id)


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



def gen_token_for_product_srv(private_key_file) -> str:
    now = datetime.utcnow()
    payload = {
        "aud": "PRODUCTS_SRV",
        "iat": now.timestamp(),
        "exp": (now + timedelta(hours=24)).timestamp(),
        "role": "ORDER_SRV",
    }

    private_key_text = Path(private_key_file).read_text()
    private_key = serialization.load_pem_private_key(
        private_key_text.encode(),
        password=None,
    )
    return jwt.encode(payload=payload, key=private_key, algorithm="RS256")
