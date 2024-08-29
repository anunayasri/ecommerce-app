from sqlalchemy import create_engine
import sqlalchemy as sa
import sqlalchemy.orm as so

from config import AppConfig
from repository.models import Base, OrderModel, OrderItemModel


def main():
    conf = AppConfig()
    engine = create_engine(conf.ORDERS_DB_URL)

    print(f"Tring to create seed data for Orders DB: {conf.ORDERS_DB_URL}")
    print("Note: The script will fail if the data already exists in the table")

    print("Creating tables in Orders DB")
    Base.metadata.create_all(engine)
    print("Successfully created tables in Orders DB")

    # print("Creating seed data in Orders DB")
    # with so.Session(engine) as session:
    #     items = [
    #         OrderItemModel(id=1, product_id=1, quantity=3),
    #         OrderItemModel(id=2, product_id=2, quantity=10),
    #     ]
    #
    #     order = OrderModel(id=1, items=items, status='CREATED', user_id=1)
    #
    #     session.add(order)
    #
    #     session.commit()
    #
    #     print("Created following data")
    #     stmt = sa.select(OrderModel)
    #     for order in session.scalars(stmt):
    #         print(order)
    #         print([item for item in order.items])

if __name__ == '__main__':
    main()
