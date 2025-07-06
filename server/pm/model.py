from datetime import datetime
from pydantic import BaseModel
from app.pm.entity import ParticulateMatterEntity


class ParticulateMatterModel(BaseModel):
    datetime: datetime
    station_name: str
    pm10Value: int | None
    pm10Grade: int | None
    pm25Value: int | None
    pm25Grade: int | None

    @classmethod
    def from_dataclass(
            cls,
            particulate_matter_entity: ParticulateMatterEntity
    ) -> "ParticulateMatterModel":
        return cls(
            datetime=particulate_matter_entity.datetime,
            station_name=particulate_matter_entity.station_name,
            pm10Value=particulate_matter_entity.pm10Value,
            pm10Grade=particulate_matter_entity.pm10Grade,
            pm25Value=particulate_matter_entity.pm25Value,
            pm25Grade=particulate_matter_entity.pm25Grade
        )
