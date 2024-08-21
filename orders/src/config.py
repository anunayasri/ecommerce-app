from pydantic_settings import BaseSettings, SettingsConfigDict

class AppConfig(BaseSettings):
    ORDERS_DB_URL: str = 'orders.db'
    PRODUCT_SRV_HOST: str = 'http://localhost'
    PRODUCT_SRV_PORT: str = '8002'
    AUTH_JWT_PUBLIC_KEY_FILE: str = 'public_key.pem'
    AUTH_JWT_PRIVATE_KEY_FILE: str = 'private_key.pem'

    model_config = SettingsConfigDict(env_file=".env")

