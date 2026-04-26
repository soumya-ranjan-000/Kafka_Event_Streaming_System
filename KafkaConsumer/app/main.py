import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import db_instance
from .consumer import order_consumer
from .routers import orders, products
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up database connection...")
    await db_instance.connect()
    
    logger.info("Starting up Kafka consumer...")
    await order_consumer.start()
    
    yield
    
    logger.info("Shutting down Kafka consumer...")
    await order_consumer.stop()
    
    logger.info("Shutting down database connection...")
    await db_instance.close()

app = FastAPI(lifespan=lifespan, title="Kafka Consumer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orders.router)
app.include_router(products.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/stats")
async def get_stats():
    return {
        "status": "online",
        "processedCount": order_consumer.processed_count,
        "instanceId": id(order_consumer)
    }
