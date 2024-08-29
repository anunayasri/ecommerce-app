from dataclasses import dataclass
import enum
from pathlib import Path
from typing import Annotated
import uvicorn

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import sqlalchemy as sa
import sqlalchemy.orm as so

from cryptography.x509 import load_pem_x509_certificate
from db import Product, ProductStatus
import jwt
from jwt.exceptions import InvalidTokenError
from schemas import CreateProductSchema, GetProductSchema, UpdateProductSchema
from config import AppConfig

conf = AppConfig()
public_key_text = Path(conf.AUTH_JWT_PUBLIC_KEY_FILE).read_text()
PUBLIC_KEY = load_pem_x509_certificate(public_key_text.encode()).public_key()

app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = sa.create_engine(conf.PRODUCTS_DB_URL, echo=True)
Session = so.sessionmaker(autocommit=False, autoflush=False, bind=engine)

bearer_auth = HTTPBearer()
    
def get_session():
    s = Session()
    try:
        yield s 
    finally:
        s.close()
    

class UserRole(enum.Enum):
    seller = "seller"
    buyer = "buyer"

class TokenIssuer(enum.Enum):
    user_srv = "user_srv"
    order_srv = "order_srv"

@dataclass
class JWTPayload:
    # iss can be user_srv or order_srv based on which service issued the token
    # if iss == user_srv, then user_id, username, user_role will be not None, 
    # else they will be None
    iss: str
    user_id: int | None
    username: str | None
    user_role: str | None

def get_jwt_payload(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_auth)]
) -> JWTPayload:

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

        return JWTPayload(
            iss = payload.get('iss'),
            user_id = payload.get('user_id'),
            username = payload.get('username'),
            user_role = payload.get('user_role'),
        )

    except InvalidTokenError as e:
        raise credentials_exception

def get_current_user(jwt_payload: Annotated[JWTPayload, Depends(get_jwt_payload)]) -> int:
    user_id = jwt_payload.user_id
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return int(user_id)

def get_user_role(jwt_payload: Annotated[JWTPayload, Depends(get_jwt_payload)]) -> UserRole | None:
    role = jwt_payload.user_role
    if not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Role is mandatory",
            headers={"WWW-Authenticate": "Bearer"},
        ) 
    return UserRole(role)


@app.post(
    "/products",
    status_code=status.HTTP_201_CREATED,
    response_model=GetProductSchema,
    tags=["Product"],
)
def create_order(
    payload: CreateProductSchema, 
    session: Annotated[so.Session, Depends(get_session)],
    user_id: Annotated[int, Depends(get_current_user)],
    role: Annotated[UserRole, Depends(get_user_role)],
):
    if role != UserRole.seller:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a seller",
        )

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


@app.put(
    "/products/{product_id}",
    response_model=GetProductSchema,
    tags=["Product"],
)
def update_product(
    product_id: int,
    product_data: UpdateProductSchema,
    session: Annotated[so.Session, Depends(get_session)],
    curr_user_id: Annotated[int, Depends(get_current_user)],
    role: Annotated[UserRole, Depends(get_user_role)],
):
    """Seller can update the title, description, quantity of the product.
    Deletion is not supported. However, the owner can delist the product by
    setting the status field to INACTIVE
    """

    if role != UserRole.seller:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a seller",
        )

    stmt = sa.select(Product).where(Product.id == product_id)
    product = session.scalars(stmt).one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Product not found",
        )

    if product.user_id != curr_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the owner of the product.",
        )

    product.title = product_data.title
    product.description = product_data.description
    product.quantity = product_data.quantity
    _status = product_data.status or product.status
    product.status = _status.value

    session.commit()
    session.refresh(product)

    return product


@app.post('/products/{product_id}/buy', tags=["Product"])
def buy_product(
    product_id: int,
    order_quantity: int,
    session: Annotated[so.Session, Depends(get_session)],
    jwt_payload: Annotated[JWTPayload, Depends(get_jwt_payload)],
) -> JSONResponse:
    """This api is used by the orders service to buy a product.
    The product quantity will be descreased by the order amount.
    The api will return an error if the inventory is insufficient.
    """

    issuer = jwt_payload.iss

    if issuer != TokenIssuer.order_srv.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Thsi is an internal api",
        )

    product = session.scalars(sa.select(Product).where(
        Product.id == product_id,
        Product.status == ProductStatus.ACTIVE,
    )).one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Product not found",
        )

    if product.quantity < order_quantity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=f"Insufficient quantity. Available: {product.quantity}, Requested: {order_quantity}"
        )

    # Use optimistic concurrency control to reduce the product quantity
    stmt = sa.update(Product).where(
        Product.id == product_id,
        Product.status == ProductStatus.ACTIVE,
        Product.quantity - order_quantity >= 0,
    ).values(quantity=Product.quantity - order_quantity)

    result = session.execute(stmt)
    rows_updated = result.rowcount
    session.commit()

    # query the product again
    product = session.scalars(sa.select(Product).where(
        Product.id == product_id,
        Product.status == ProductStatus.ACTIVE,
    )).one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Product not found",
        )

    if rows_updated == 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=f"Insufficient quantity. Available: {product.quantity}, Requested: {order_quantity}"
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={},
    )
if __name__ == '__main__':
        uvicorn.run("app:app", host="0.0.0.0", port=8002, reload=True)
