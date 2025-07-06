from fastapi import Depends
from app.database.mongo import Mongo, get_mongo
from app.pm.entity import ParticulateMatterEntity, ParticulateMatterStationEntity


class ParticulateMatterRepository:
    def __init__(
            self,
            mongo: Mongo
    ):
        self.mongo = mongo

    async def get_particulate_matter_by_stations(
            self,
            stations: ParticulateMatterStationEntity
    ) -> ParticulateMatterEntity:
        particulate_matter: dict | None = await self.mongo.pm_data.find_one(
            {
                "station_name": {
                    "$in": stations.stations
                },
                "$or": [
                    {"pm10Value": {"$ne": None}},
                    {"pm25Value": {"$ne": None}}
                ]
            },
            sort=[("dataTime", -1)]
        )

        if not particulate_matter:
            particulate_matter = await self.mongo.pm_data.find_one(
                {
                    "station_name": {
                        "$in": stations.stations
                    }
                },
                sort=[("dataTime", -1)]
            )

        return ParticulateMatterEntity(
            datetime=particulate_matter["dataTime"],
            station_name=particulate_matter["station_name"],
            pm10Value=particulate_matter.get("pm10Value"),
            pm10Grade=particulate_matter.get("pm10Grade"),
            pm25Value=particulate_matter.get("pm25Value"),
            pm25Grade=particulate_matter.get("pm25Grade")
        )

    async def get_near_particulate_matter_stations(
            self,
            latitude: float,
            longitude: float
    ) -> ParticulateMatterStationEntity:
        stations: list[dict] = await self.mongo.pm_station.find({
            "geometry": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [longitude, latitude]
                    },
                }
            }
        }).to_list(length=3)
        return ParticulateMatterStationEntity(
            stations=[station["station_name"] for station in stations]
        )


def get_particulate_matter_repository(
        mongo: Mongo = Depends(get_mongo)
) -> ParticulateMatterRepository:
    return ParticulateMatterRepository(mongo=mongo)
