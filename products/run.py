import sqlalchemy as sa
from src.db import Base

engine = sa.create_engine("sqlite:///products.db", echo=True)

Base.metadata.create_all(engine)
