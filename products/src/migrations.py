import sqlalchemy as sa
import sqlalchemy.orm as so
from db import Base, ProductStatus, Product

from config import AppConfig

def main():
    conf = AppConfig()

    engine = sa.create_engine(conf.PRODUCTS_DB_URL, echo=True)

    print("Tring to create seed data for Products DB")
    print("Note: The script will fail if the data already exists in the table")

    print("Creating tables in Products DB")
    Base.metadata.create_all(engine)
    print("Successfully created tables in Products DB")

    print("Creating seed data in Products DB")

    session = so.Session(engine)

    products = [
        Product(
            id=1,
            title='Cetaphil Skin Cleanser',
            description='Replenishes skin lipids and moisturises the skin',
            user_id=1,
            status=ProductStatus.ACTIVE,
            quantity=100,
        ),
        Product(
            id=2,
            title='Apple iPhone 15',
            description='Best phone with the best camera',
            user_id=1,
            status=ProductStatus.ACTIVE,
            quantity=40,
        ),
    ]

    session.add_all(products)

    session.commit()

    print("Created following data")
    stmt = sa.select(Product)
    for product in session.scalars(stmt):
        print(product)

if __name__ == '__main__':
    main()
