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

from orders.orders_service.exceptions import OrderNotFoundException, ProductNotBookedException
from orders.orders_service.orders_service import OrdersService
from orders.orders_service.orders import Order, OrderItem
from orders.repository.orders_repository import OrdersRepository
from orders.web.api.schemas import (
    GetOrderSchema,
    CreateOrderSchema,
    GetOrdersSchema,
)

from pathlib import Path

public_key_text = Path("public_key.pem").read_text()
PUBLIC_KEY = load_pem_x509_certificate(public_key_text.encode()).public_key()

app = FastAPI(debug=True)

# orders_doc = yaml.safe_load(
#     (Path(__file__).parent / '../../orders.yaml').read_text()
# )
# app.openapi = lambda: orders_doc

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = sa.create_engine("sqlite:///orders.db", echo=True)


bearer_auth = HTTPBearer()

class UserRole(enum.Enum):
    SELLER = "SELLER"
    BUYER = "BUYER"
    ORDER_SRV = "ORDER_SRV"

def get_session():
    s = so.Session(engine)
    try:
        yield s 
    finally:
        s.close()

def get_jwt_payload(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_auth)]
) -> int:

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

@app.get("/orders", response_model=GetOrdersSchema)
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


@app.get("/orders/{order_id}", response_model=GetOrderSchema)
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
        uvicorn.run("orders.web.app:app", host="0.0.0.0", port=8003, reload=True)
