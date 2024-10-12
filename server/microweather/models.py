from pydantic import BaseModel
from datetime import datetime

class NowcastModel(BaseModel):
    datetime: datetime
    PTY: float
    REH: float
    RN1: float
    T1H: float

class ForecastModel(BaseModel):
    datetime: datetime
    LGT: float
    PTY: float
    RN1: float
    SKY: float
    T1H: float

class ParticulateMatterModel(BaseModel):
    datetime: datetime
    station_name: str
    pm10Value: int | None
    pm10Grade: int | None
    pm25Value: int | None
    pm25Grade: int | None

class WeatherModel(BaseModel):
    address: str
    is_sunrise: bool
    nowcast: NowcastModel
    forecast: list[ForecastModel]
    particulate_matter: ParticulateMatterModel
