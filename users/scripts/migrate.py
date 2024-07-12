import os
import logging
from sqlalchemy import create_engine
from db.sql_repository import Base

def init_db(engine):
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    db_url: str = os.getenv('USERS_DB_URL')
    if not db_url:
        logging.exception('USERS_DB_URL env var is empty')

    logging.info(f"DB Url for migration: {db_url}")

    if db_url.startswith('sqlite:///'):
        filepath = db_url[len('sqlite:///'):]
        absfilepath = os.path.abspath(filepath)
        logging.info(f"Found sqlite DB. Filepath: {absfilepath}")
        db_url = f"sqlite:///{absfilepath}"


    sqlite_engine = create_engine(db_url, echo=True)
    init_db(sqlite_engine)

