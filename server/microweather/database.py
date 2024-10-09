import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection


class Database:
    def __init__(self):
        self.user = os.getenv("MONGODB_USERNAME")
        self.password = os.getenv("MONGODB_PASSWORD")
        self.client = AsyncIOMotorClient(f"mongodb://{self.user}:{self.password}@microweather-db")
        self.database: AsyncIOMotorDatabase = self.client["microweather"]
        self.nowcast: AsyncIOMotorCollection = self.database["nowcast"]
        self.forecast: AsyncIOMotorCollection = self.database["forecast"]
        self.pm_station: AsyncIOMotorCollection = self.database["pm_station"]
        self.pm_data: AsyncIOMotorCollection = self.database["pm_data"]

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.client.close()