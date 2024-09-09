from fastapi import APIRouter
from app.microweather.service import WeatherService
from app.microweather.models import WeatherModel

router = APIRouter(prefix="/weather")


@router.get("", response_model=WeatherModel)
async def get_weather(latitude: float, longitude: float):
    weather_data = await WeatherService(latitude=latitude, longitude=longitude).get_weather()
    return weather_data
