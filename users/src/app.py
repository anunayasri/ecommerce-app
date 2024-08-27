from contextlib import asynccontextmanager
from functools import lru_cache
from datetime import datetime, timedelta, timezone
from typing import Annotated
import uvicorn
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.x509 import load_pem_x509_certificate
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
import sqlalchemy as sa
import sqlalchemy.orm as so

from auth import hash_password, verify_password
from config import AppConfig
from schemas import (
    GetUserSchema, CreateUserSchema, CreateBuyerProfile, CreateSellerProfile,
    GetBuyerProfile,
)
from db import BuyerProfile, User, SellerProfile, UserRole

# to get a string like this run:
# openssl rand -hex 32
# SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

conf = AppConfig()

public_key_text = Path(conf.AUTH_JWT_PUBLIC_KEY_FILE).read_text()
PUBLIC_KEY = load_pem_x509_certificate(public_key_text.encode()).public_key()
ALGORITHM = "RS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     print(">>>> staring lifespan")
#     yield
#     print(">>>> Leaving lifespan")
#

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sqlite_db = "users.db"

engine = sa.create_engine(conf.USERS_DB_URL)
# Session = so.sessionmaker(engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None

@lru_cache
def get_config() -> AppConfig:
    return AppConfig()


def get_session(conf: Annotated[AppConfig, Depends(get_config)]):
    engine = sa.create_engine(conf.USERS_DB_URL, echo=True)
    s = so.Session(engine)
    try:
        yield s
    finally:
        s.close()


def authenticate_user(
        session: Annotated[so.Session, Depends(get_session)],
        username: str,
        password: str,
):
    user = get_user(session, username)

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})

    private_key_text = Path(conf.AUTH_JWT_PRIVATE_KEY_FILE).read_text()
    private_key = serialization.load_pem_private_key(
        private_key_text.encode(),
        password=None,
    )

    encoded_jwt = jwt.encode(to_encode, key=private_key, algorithm=ALGORITHM)
    return encoded_jwt


def get_user(session, username):
    stmt = sa.select(User).where(User.username == username)
    user = session.scalars(stmt).one_or_none()

    return user


async def get_current_user(
    session: Annotated[so.Session, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, key=PUBLIC_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if not username:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception
    
    user = get_user(session, username)
    if user is None:
        raise credentials_exception

    return user

@app.post("/users/token")
async def login_for_access_token(
    session: Annotated[so.Session, Depends(get_session)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:

    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "username": user.username,
        },
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=GetUserSchema)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


@app.post("/users", response_model=GetUserSchema)
async def register_user(
    session: Annotated[so.Session, Depends(get_session)],
    payload: CreateUserSchema,
):


    stmt = sa.select(User).where(
        User.username == payload.username,
        User.email == payload.email
    )
    existing_user = session.scalars(stmt).one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate username or email",
        )

    user = User(
        first_name = payload.first_name,
        last_name = payload.last_name,
        username = payload.username,
        email = payload.email,
        hashed_password = hash_password(payload.password),
        role = payload.role.value,
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@app.post("/buyer_profile", response_model=GetBuyerProfile)
async def create_buyer_profile(
    session: Annotated[so.Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    payload: CreateBuyerProfile,
):

    stmt = sa.select(BuyerProfile).where(
        BuyerProfile.user_id == current_user.id,
    )
    existing_buyer_pf = session.scalars(stmt).one_or_none()

    if existing_buyer_pf:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Buyer profile already exists",
        )
    
    if current_user.role != UserRole.BUYER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not registered as a buyer.",
        )


    buyer_profile = BuyerProfile(
        user=current_user,
        shipping_address=payload.shipping_address,
    )

    session.add(buyer_profile)
    session.commit()
    session.refresh(buyer_profile)

    return buyer_profile


@app.post("/seller_profile")
async def create_seller_profile(
    session: Annotated[so.Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    payload: CreateSellerProfile,
):
    stmt = sa.select(SellerProfile).where(
        SellerProfile.user_id == current_user.id,
    )
    existing_seller_pf = session.scalars(stmt).one_or_none()

    if existing_seller_pf:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seller profile already exists",
        )

    if current_user.role != UserRole.SELLER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not registered as a seller.",
        )

    seller_profile = SellerProfile(
        user=current_user,
        store_name=payload.store_name,
    )

    session.add(seller_profile)
    session.commit()
    session.refresh(seller_profile)

    return seller_profile


if __name__ == '__main__':
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)
