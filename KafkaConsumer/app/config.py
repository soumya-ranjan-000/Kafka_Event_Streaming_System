from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic: str = "orders-topic"
    kafka_dlq_topic: str = "orders-topic.dlq"
    kafka_consumer_group: str = "order-processor-group"
    mongodb_uri: str = "mongodb://localhost:27017"
    database_name: str = "ecommerce_db"
    
    class Config:
        env_file = ".env"

settings = Settings()
