from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
from .config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

    async def connect(self):
        self.client = AsyncIOMotorClient(settings.mongodb_uri)
        self.db = self.client[settings.database_name]
        
        # Create unique index on _id to enforce idempotency
        # In MongoDB, _id is automatically unique and indexed. 
        # But we can also create other indexes if needed.
        pass

    async def close(self):
        if self.client:
            self.client.close()

db_instance = Database()

def get_db():
    return db_instance.db
