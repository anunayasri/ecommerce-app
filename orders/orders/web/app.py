from typing import Optional
import os
from uuid import UUID

from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from starlette import status
from starlette.middleware.base import (
    RequestResponseEndpoint,
    BaseHTTPMiddleware,
)
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse


from orders.orders_service.exceptions import OrderNotFoundError
from orders.orders_service.orders_service import OrdersService
from orders.repository.orders_repository import OrdersRepository
from orders.web.api.schemas import (
    GetOrderSchema,
    CreateOrderSchema,
    GetOrdersSchema,
)

from orders.web.api.auth import decode_and_validate_token

from pathlib import Path
import yaml

app = FastAPI(debug=True, )

orders_doc = yaml.safe_load(
    (Path(__file__).parent / '../../orders.yaml').read_text()
)
app.openapi = lambda: orders_doc

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

engine = create_engine("sqlite:///orders.db", echo=True)

class AuthorizeRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if os.getenv("AUTH_ON", "False") != "True":
            request.state.user_id = "test"
            return await call_next(request)

        if request.url.path in ["/docs", "/openapi.json"]:
            return await call_next(request)
        if request.method == "OPTIONS":
            return await call_next(request)

        bearer_token = request.headers.get("Authorization")
        if not bearer_token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "detail": "Missing access token",
                    "body": "Missing access token",
                },
            )
        try:
            auth_token = bearer_token.split(" ")[1].strip()
            token_payload = decode_and_validate_token(auth_token)
        except (
            ExpiredSignatureError,
            ImmatureSignatureError,
            InvalidAlgorithmError,
            InvalidAudienceError,
            InvalidKeyError,
            InvalidSignatureError,
            InvalidTokenError,
            MissingRequiredClaimError,
        ) as error:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": str(error), "body": str(error)},
            )
        else:
            request.state.user_id = token_payload["sub"]
        return await call_next(request)


app.add_middleware(AuthorizeRequestMiddleware)

@app.get("/orders", response_model=GetOrdersSchema)
def get_orders(
    request: Request,
    cancelled: Optional[bool] = None,
    limit: Optional[int] = None,
):
    # with UnitOfWork() as unit_of_work:
    #     repo = OrdersRepository(unit_of_work.session)
    #     orders_service = OrdersService(repo)
    #     results = orders_service.list_orders(
    #         limit=limit, cancelled=cancelled, user_id=request.state.user_id
    #     )

    with Session(engine) as session:
        repo = OrdersRepository(session)
        orders_service = OrdersService(repo)
        results = orders_service.list_orders(
            # limit=limit, cancelled=cancelled, user_id=request.state.user_id
            limit=limit, cancelled=cancelled, user_id='1'
        )

    return {"orders": [result.dict() for result in results]}


@app.post(
    "/orders",
    status_code=status.HTTP_201_CREATED,
    response_model=GetOrderSchema,
)
def create_order(request: Request, payload: CreateOrderSchema):
    with Session(engine) as session:
        repo = OrdersRepository(session)
        orders_service = OrdersService(repo)
        order = payload.dict()["order"]
        for item in order:
            item["size"] = item["size"].value
        order = orders_service.place_order(order, request.state.user_id)
        session.commit()
        return_payload = order.dict()
    return return_payload


@app.get("/orders/{order_id}", response_model=GetOrderSchema)
def get_order(request: Request, order_id: UUID):
    # try:
    #     with UnitOfWork() as unit_of_work:
    #         repo = OrdersRepository(unit_of_work.session)
    #         orders_service = OrdersService(repo)
    #         order = orders_service.get_order(
    #             order_id=order_id, user_id=request.state.user_id
    #         )
    #     return order.dict()
    # except OrderNotFoundError:
    #     raise HTTPException(
    #         status_code=404, detail=f"Order with ID {order_id} not found"
        
    try:
        with Session(engine) as session:
            repo = OrdersRepository(session)
            orders_service = OrdersService(repo)
            order = orders_service.get_order(
                # order_id=order_id, user_id=request.state.user_id
                order_id=order_id, # user_id=request.state.user_id
            )
        return order.dict()
    except OrderNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Order with ID {order_id} not found"
        
        )
