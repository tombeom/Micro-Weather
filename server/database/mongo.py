from app.settings import Settings
from fastapi import Request, Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection


class Mongo:
    def __init__(self, client: AsyncIOMotorClient):
        self.client: AsyncIOMotorClient = client
        self.database: AsyncIOMotorDatabase = self.client["microweather"]
        self.nowcast: AsyncIOMotorCollection = self.database["nowcast"]
        self.forecast: AsyncIOMotorCollection = self.database["forecast"]
        self.pm_station: AsyncIOMotorCollection = self.database["pm_station"]
        self.pm_data: AsyncIOMotorCollection = self.database["pm_data"]
        self.location: AsyncIOMotorCollection = self.database["location"]

    @classmethod
    def create_client(cls) -> AsyncIOMotorClient:
        settings = Settings.get_settings()
        return AsyncIOMotorClient(
            f"mongodb://{settings.MONGODB_USERNAME}:{settings.MONGODB_PASSWORD}@{settings.MONGODB_URL}"
        )


def get_mongo_client(request: Request) -> AsyncIOMotorClient:
    return request.app.state.client


def get_mongo(
        client: AsyncIOMotorClient = Depends(get_mongo_client)
) -> Mongo:
    return Mongo(client=client)
