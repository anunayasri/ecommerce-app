################
# TODO: Move the authentication logic of web api here
################

# from datetime import datetime, timedelta, timezone
# from typing import Annotated
#
# from fastapi import Depends
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# import jwt
# from jwt.exceptions import InvalidTokenError
# from passlib.context import CryptContext
# from pydantic import BaseModel
# import sqlalchemy as sa
# import sqlalchemy.orm as so
#
# from repository.users_sql_repository import UsersSQLRepository
# from users_service.entities import User
# from users_service.users_service import UsersService
# from users_service.auth import verify_password
#
# SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30
#
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#
# class Token(BaseModel):
#     access_token: str
#     token_type: str
#
#
# class TokenData(BaseModel):
#     username: str | None = None
#
#
# def authenticate_user(session, username: str, password: str):
#     user = get_user(session, username)
#
#     if not user:
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#     return user
#
# def create_access_token(data: dict, expires_delta: timedelta | None = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.now(timezone.utc) + expires_delta
#     else:
#         expire = datetime.now(timezone.utc) + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt
#
# def get_user(session, username):
#     repo = UsersSQLRepository(session)
#     user_srv = UsersService(repo)
#     return user_srv.get_user_by_username(username)
#
#
# async def get_current_user(
#     token: Annotated[str, Depends(oauth2_scheme)],
#     session: so.Session,
# ):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except InvalidTokenError:
#         raise credentials_exception
#     
#     # session defined globally
#     user = get_user(session, token_data.username)
#     if user is None:
#         raise credentials_exception
#     return user
