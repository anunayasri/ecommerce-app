import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('ORDERS_DB_URL') or \
        f'sqlite:///{basedir}/ordesdb.sqlite'

class DevConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
