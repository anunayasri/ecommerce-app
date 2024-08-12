from typing import Annotated

from pathlib import Path
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from starlette.types import HTTPExceptionHandler
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
from schemas import CreateProductSchema, GetProductSchema, UpdateProductSchema

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


@app.put( "/product/{product_id}", response_model=GetProductSchema)
def update_product(
    product_id: int,
    product_data: UpdateProductSchema,
    session: Annotated[so.Session, Depends(get_session)],
    curr_user_id: Annotated[int, Depends(get_current_user)],
):
    """Seller can update the title, description, quantity of the product.
    Deletion is not supported. However, the owner can delist the product by
    setting the status field to INACTIVE
    """
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
    product.status = product_data.status or product.status

    session.commit()
    session.refresh(product)

    return product

@app.post('/product/{product_id}/buy')
def buy_product(
    product_id: int,
    order_quantity: int,
    session: Annotated[so.Session, Depends(get_session)],
    # curr_user_id: Annotated[int, Depends(get_current_user)],
) -> JSONResponse:
    """This api is used by the orders service to buy a product.
    The product quantity will be descreased by the order amount.
    The api will return an error if the inventory is insufficient.
    """

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

    return JSONResponse(HTTP_200_OK)
