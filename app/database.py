from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "library")
COLLECTION_NAME = "books"

class Database:
    client: AsyncIOMotorClient = None

    async def connect_to_database(self):
        self.client = AsyncIOMotorClient(MONGO_URL)

    async def close_database_connection(self):
        if self.client is not None:
            self.client.close()


db = Database()


async def get_collection():
    return db.client[DB_NAME][COLLECTION_NAME]