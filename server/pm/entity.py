from datetime import datetime
from dataclasses import dataclass


@dataclass
class ParticulateMatterEntity:
    datetime: datetime
    station_name: str
    pm10Value: int | None
    pm10Grade: int | None
    pm25Value: int | None
    pm25Grade: int | None


@dataclass
class ParticulateMatterStationEntity:
    stations: list[str]

