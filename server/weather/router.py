from typing import Annotated
from fastapi import APIRouter, Depends
from app.weather.model import WeatherModel
from app.utils.coordinate import CoordinatesModel
from app.weather.service import WeatherService, get_weather_service

router = APIRouter(prefix="/weather")

CoordinatesQueryParams = Annotated[CoordinatesModel, Depends(CoordinatesModel)]
WeatherService = Annotated[WeatherService, Depends(get_weather_service)]


@router.get(
    "/nowcast",
    status_code=200,
    response_model=WeatherModel
)
async def get_nowcast(
        coordinates: CoordinatesQueryParams,
        service: WeatherService,
) -> WeatherModel:
    return await service.get_nowcast(
        latitude=coordinates.latitude,
        longitude=coordinates.longitude
    )


@router.get(
    "/forecast",
    status_code=200,
    response_model=list[WeatherModel]
)
async def get_forecast(
        coordinates: CoordinatesQueryParams,
        service: WeatherService,
) -> list[WeatherModel]:
    return await service.get_forecast(
        latitude=coordinates.latitude,
        longitude=coordinates.longitude
    )
