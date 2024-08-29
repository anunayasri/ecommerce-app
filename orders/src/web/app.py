from functools import lru_cache
from typing import Optional, Annotated, Dict
import enum

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import uvicorn
import sqlalchemy as sa
import sqlalchemy.orm as so

from cryptography.x509 import load_pem_x509_certificate
import jwt

from config import AppConfig
from orders_service.exceptions import OrderNotFoundException, ProductNotBookedException
from orders_service.orders_service import OrdersService
from orders_service.orders import Order, OrderItem
from repository.orders_repository import OrdersRepository
from web.schemas import (
    GetOrderSchema,
    CreateOrderSchema,
    GetOrdersSchema,
)
from pathlib import Path

public_key_text = Path(AppConfig().AUTH_JWT_PUBLIC_KEY_FILE).read_text()
PUBLIC_KEY = load_pem_x509_certificate(public_key_text.encode()).public_key()

app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bearer_auth = HTTPBearer()

class UserRole(enum.Enum):
    SELLER = "SELLER"
    BUYER = "BUYER"
    ORDER_SRV = "ORDER_SRV"

@lru_cache
def get_config() -> AppConfig:
    return AppConfig()


def get_session(conf: Annotated[AppConfig, Depends(get_config)]):
    # engine = sa.create_engine("sqlite:///orders.db", echo=True)
    engine = sa.create_engine(conf.ORDERS_DB_URL, echo=True)
    s = so.Session(engine)
    try:
        yield s 
    finally:
        s.close()

def get_jwt_payload(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_auth)]
) -> Dict:

    """Validates the jwt token in the Authentication header.
    """

    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            key=PUBLIC_KEY,
            algorithms=['RS256'],
        )

        return payload

    except jwt.InvalidTokenError as e:
        print(f"invalid token : {e}")
        raise credentials_exception

def get_current_user(jwt_payload: Annotated[Dict, Depends(get_jwt_payload)]) -> int:
    user_id = jwt_payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user details",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return int(user_id)

def get_user_role(jwt_payload: Annotated[Dict, Depends(get_jwt_payload)]) -> UserRole | None:
    role = jwt_payload.get('role')
    if not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Role is mandatory",
            headers={"WWW-Authenticate": "Bearer"},
        ) 
    return UserRole(role)

@app.get(
    "/orders",
    response_model=GetOrdersSchema,
    tags=["Order"],
)
def get_orders(
    session: Annotated[so.Session, Depends(get_session)],
    user_id: Annotated[int, Depends(get_current_user)],
):
    repo = OrdersRepository(session)
    orders_service = OrdersService(repo)
    try:
        results = orders_service.list_orders(user_id=user_id)
    except OrderNotFoundException:
        # return an empty list
        return {"orders": []}

    return {"orders": [result.dict() for result in results]}


@app.post(
    "/orders",
    status_code=status.HTTP_201_CREATED,
    response_model=GetOrderSchema,
    tags=["Order"],
)
def create_order(
    payload: CreateOrderSchema,
    session: Annotated[so.Session, Depends(get_session)],
    user_id: Annotated[int, Depends(get_current_user)],

):
    repo = OrdersRepository(session)
    orders_service = OrdersService(repo)
    items_json = payload.dict()["items"]

    items = [OrderItem(**item) for item in items_json]

    try:
        order = orders_service.place_order(items, user_id)
        session.commit()
        return order.dict()

    except ProductNotBookedException:
        # rollback any changes made to the DB
        session.rollback()
        # reraise the exception
        raise ProductNotBookedException()


@app.get(
    "/orders/{order_id}",
    response_model=GetOrderSchema,
    tags=["Products"],
)
def get_order(
    order_id: int,
    session: Annotated[so.Session, Depends(get_session)],
    user_id: Annotated[int, Depends(get_current_user)],
):
    repo = OrdersRepository(session)
    orders_service = OrdersService(repo)

    try:
        order = orders_service.get_order(
            order_id=order_id, user_id=user_id,
        )
        return order.dict()
    except OrderNotFoundException:
        raise HTTPException(
            status_code=404, detail=f"Order with ID {order_id} not found"
        )

if __name__ == '__main__':
        uvicorn.run("web.app:app", host="0.0.0.0", port=8003, reload=True)
