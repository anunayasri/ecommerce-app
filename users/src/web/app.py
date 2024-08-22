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

from config import AppConfig
from repository.users_sql_repository import UsersSQLRepository
from users_service.entities import User
from users_service.users_service import UsersService
from users_service.auth import verify_password

from web.schemas import GetUserSchema

# to get a string like this run:
# openssl rand -hex 32
# SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

conf = AppConfig()

public_key_text = Path(conf.AUTH_JWT_PUBLIC_KEY_FILE).read_text()
PUBLIC_KEY = load_pem_x509_certificate(public_key_text.encode()).public_key()
ALGORITHM = "RS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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
Session = so.sessionmaker(engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


def authenticate_user(session, username: str, password: str):
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

def get_user(Session, username):
    with Session() as session:
        repo = UsersSQLRepository(session)
        user_srv = UsersService(repo)
        return user_srv.get_user_by_username(username)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
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
    
    # session defined globally
    user = get_user(Session, username)
    if user is None:
        raise credentials_exception

    return user

@app.post("/users/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(Session, form_data.username, form_data.password)
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

if __name__ == '__main__':
        uvicorn.run("web.app:app", host="0.0.0.0", port=8001, reload=True)
