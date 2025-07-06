from fastapi import Depends
from app.database.mongo import Mongo, get_mongo
from app.weather.entity import NowcastEntity, ForecastEntity


class WeatherRepository:
    def __init__(
            self,
            mongo: Mongo
    ):
        self.mongo = mongo

    async def get_nowcast_by_grid_coordinates(
            self,
            grid_x: int,
            grid_y: int
    ) -> NowcastEntity:
        nowcast: dict = await self.mongo.nowcast.find_one(
            {
                "nx": grid_x,
                "ny": grid_y
            },
            sort=[("tm", -1)]
        )

        nearest_forecast: dict = await self.mongo.forecast.find_one(
            {
                "nx": grid_x,
                "ny": grid_y
            },
            sort=[("tm", -1)]
        )

        lgt: float | None = nearest_forecast.get("items", [{}])[0].get("LGT", None)
        if lgt is not None:
            nowcast["LGT"] = lgt
        else:
            raise ValueError("No lightning data available in the nearest forecast.")

        sky: float | None = nearest_forecast.get("items", [{}])[0].get("SKY", None)
        if sky is not None:
            nowcast["SKY"] = sky
        else:
            raise ValueError("No sky data available in the nearest forecast.")

        return NowcastEntity.from_dict(
            nowcast_entity=nowcast
        )

    async def get_forecast_by_grid_coordinates(
            self,
            grid_x: int,
            grid_y: int
    ) -> list[ForecastEntity]:
        forecast: dict = await self.mongo.forecast.find_one(
            {
                "nx": grid_x,
                "ny": grid_y
            },
            sort=[("tm", -1)]
        )
        return [
            ForecastEntity.from_dict(
                forecast_entity=data
            ) for data in forecast["items"]
        ]


def get_weather_repository(
        mongo: Mongo = Depends(get_mongo)
) -> WeatherRepository:
    return WeatherRepository(mongo=mongo)
