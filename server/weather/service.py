from fastapi import HTTPException, Depends
from app.weather.model import WeatherModel
from app.utils.coordinate import CoordinatesModel
from app.weather.entity import NowcastEntity, ForecastEntity
from app.weather.repository import WeatherRepository, get_weather_repository


class WeatherService:
    def __init__(
            self,
            repository: WeatherRepository
    ):
        self.repository = repository

    async def get_nowcast(
            self,
            latitude: float,
            longitude: float,
    ) -> WeatherModel:
        grid_x, grid_y = CoordinatesModel(
            latitude=latitude,
            longitude=longitude
        ).get_grid_coordinates()

        try:
            nowcast_data: NowcastEntity = await self.repository.get_nowcast_by_grid_coordinates(
                grid_x=grid_x,
                grid_y=grid_y
            )
        except ValueError as e:
            raise HTTPException(
                status_code=500,
                detail=e
            )
        else:
            return WeatherModel.from_nowcast_entity(
                nowcast_entity=nowcast_data
            )

    async def get_forecast(
            self,
            latitude: float,
            longitude: float,
    ) -> list[WeatherModel]:
        grid_x, grid_y = CoordinatesModel(
            latitude=latitude,
            longitude=longitude
        ).get_grid_coordinates()

        try:
            forecast_data: list[ForecastEntity] = await self.repository.get_forecast_by_grid_coordinates(
                grid_x=grid_x,
                grid_y=grid_y
            )
        except ValueError as e:
            raise HTTPException(
                status_code=500,
                detail=e
            )
        else:
            return [
                WeatherModel.from_forecast_entity(
                    forecast_entity=forecast
                ) for forecast in forecast_data
            ]


def get_weather_service(
        repository: WeatherRepository = Depends(get_weather_repository)
) -> WeatherService:
    return WeatherService(repository=repository)
