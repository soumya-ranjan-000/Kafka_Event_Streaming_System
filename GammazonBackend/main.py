from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.database import db_instance
from app.routers import products, orders

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Gammazon API Backend...")
    await db_instance.connect()
    yield
    # Shutdown
    logger.info("Shutting down Gammazon API Backend...")
    await db_instance.close()

app = FastAPI(
    title="Gammazon API Backend",
    description="Unified API for Gammazon Frontend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Gammazon API Backend is running"}

# Include routers
app.include_router(products.router, prefix="/api")
app.include_router(orders.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
