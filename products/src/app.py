import os
from typing import Optional, Annotated
from uuid import UUID

from pathlib import Path
import yaml
import jwt
from jwt.exceptions import InvalidTokenError
from cryptography.x509 import load_pem_x509_certificate

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.params import Depends
import sqlalchemy as sa
import sqlalchemy.orm as so

from db import Base, Product, ProductStatus
from schemas import CreateProductSchema, GetProductSchema

app = FastAPI(debug=True)

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

engine = sa.create_engine("sqlite:///products.db", echo=True)
Session = so.sessionmaker(autocommit=False, autoflush=False, bind=engine)

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
security = HTTPBearer()

def get_session():
    s = Session()
    try:
        yield s 
    finally:
        s.close()
    
def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> int: # def get_current_user() -> int:

    """Validates the jwt token in the Authentication header.
    Returns the user_id from jwt token.
    """

    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        public_key_text = (Path(__file__).parent / "../public_key.pem").read_text()
        public_key = load_pem_x509_certificate(public_key_text.encode()).public_key()

        payload = jwt.decode(
            token,
            key=public_key,
            algorithms=['RS256'],
            audience=["PRODUCTS_SRV"],
        )

        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception

    except InvalidTokenError as e:
        print(f"invalid token : {e}")
        raise credentials_exception
    
    # user_id is an int
    return int(user_id)

@app.get('/')
async def main():
    return {'msg': 'Hello World'}


@app.post(
    "/products",
    status_code=status.HTTP_201_CREATED,
    response_model=GetProductSchema,
)
def create_order(
    payload: CreateProductSchema, 
    session: Annotated[so.Session, Depends(get_session)],
    user_id: Annotated[int, Depends(get_current_user)],
):
    product = Product(
        title=payload.title,
        description=payload.description,
        quantity=payload.quantity,
        status=ProductStatus.ACTIVE,
        user_id=user_id,
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


# @app.get("/orders", response_model=GetOrdersSchema)
# def get_orders(
#     request: Request,
#     cancelled: Optional[bool] = None,
#     limit: Optional[int] = None,
# ):
#     pass
#
#
# @app.post(
#     "/orders",
#     status_code=status.HTTP_201_CREATED,
#     response_model=GetOrderSchema,
# )
# def create_order(request: Request, payload: CreateOrderSchema):
#     pass
