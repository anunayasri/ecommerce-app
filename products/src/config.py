from pydantic_settings import BaseSettings

class AppConfig(BaseSettings):
    PRODUCTS_DB_URL: str = 'sqlite:///users.db'
    AUTH_JWT_PUBLIC_KEY_FILE: str = 'public_key.pem'
    AUTH_JWT_PRIVATE_KEY_FILE: str = 'private_key.pem'

