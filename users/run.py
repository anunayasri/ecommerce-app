import random
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from users_service.users_service import UsersService
from users_service.entities import User
from repository.users_sql_repository import UsersSQLRepository
# from repository.models import Base


engine = create_engine("sqlite:///users.db", echo=True)

# Base.metadata.create_all(engine)

with Session(engine) as session:
    repo = UsersSQLRepository(session)
    user_srv = UsersService(repo)

    username = 'user-' + str(random.randint(1,10000000))

    user = user_srv.create_user(
        first_name=username,
        last_name=username,
        username=username,
        email=f'{username}@gmail.com',
        password='password',
    )

    print(user)
