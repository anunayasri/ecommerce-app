import sqlalchemy as sa
import sqlalchemy.orm as so

from config import AppConfig
from db import Base, User, BuyerProfile, SellerProfile, UserRole
from auth import hash_password


def main():
    conf = AppConfig()
    engine = sa.create_engine(conf.USERS_DB_URL)

    print(f"Tring to create seed data for Users DB at {conf.USERS_DB_URL}")
    print("Note: The script will fail if the data already exists in the table")

    print("Creating tables in Users DB")
    Base.metadata.create_all(engine)
    print("Successfully created tables in Users DB")

    return

    print("Creating seed data in Users DB")
    with so.Session(engine) as session:

        user = User(
            id=1,
            first_name='FirstName',
            last_name='LastName',
            username='anunaya',
            email=f'anunaya@email.com',
            hashed_password=hash_password('password'),
            role=UserRole.BUYER,
        )

        buyer_profile = BuyerProfile(
            user=user, 
            shipping_address='earth',
        )

        session.add(buyer_profile)

        session.commit()

        print("Created following data")
        stmt = sa.select(User)
        for user in session.scalars(stmt):
            print(user)

if __name__ == '__main__':
    main()

