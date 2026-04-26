from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    database_name: str = "ecommerce_db"
    producer_url: str = "http://localhost:8080/api/orders"
    
    class Config:
        env_file = ".env"

settings = Settings()
