import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DEBUG = os.getenv('DEBUG')
    TESTING = os.getenv('TESTING')
    USERS_DB_URL = os.getenv('USERS_DB_URL')

