from datetime import datetime
from pydantic import BaseModel
from app.weather.entity import NowcastEntity, ForecastEntity


class WeatherModel(BaseModel):
    datetime: datetime
    ICON: str
    T1H: float
    RN1: float
    REH: float | None = None

    @staticmethod
    def get_weather_icon(
            lightning: float,
            precipitation_type: float,
            sky_code: float,
            rain_1hr: float
    ) -> str:
        precipitation_map: dict = {
            1: "rain",  # 비
            2: "rain",  # 비/눈
            3: "snow",  # 눈
            5: "shower",  # 빗방울
            6: "shower",  # 빗방울/눈날림
            7: "snowDrifting",  # 눈날림
        }

        sky_map: dict = {
            1: "clear",
            3: "mostlyCloudy",
            4: "cloudy",
        }

        if lightning > 0:
            return "thunderStorm" if rain_1hr > 0 else "lightning"

        if icon := precipitation_map.get(precipitation_type):
            return icon

        if precipitation_type == 0:
            if rain_1hr > 0:
                return "shower"

            return sky_map.get(sky_code, "clear")
        return "clear"

    @classmethod
    def from_forecast_entity(
            cls,
            forecast_entity: ForecastEntity
    ) -> "WeatherModel":
        required_fields: list[str] = ["LGT", "PTY", "SKY", "RN1", "T1H"]

        if failed_fields := [
            field for field in required_fields
            if getattr(forecast_entity, field) is None
        ]:
            raise ValueError(f"Failed to fetch data for: {', '.join(failed_fields)}")

        return cls(
            datetime=forecast_entity.datetime,
            ICON=cls.get_weather_icon(
                lightning=forecast_entity.LGT,
                precipitation_type=forecast_entity.PTY,
                sky_code=forecast_entity.SKY,
                rain_1hr=forecast_entity.RN1
            ),
            RN1=forecast_entity.RN1,
            T1H=forecast_entity.T1H,
            REH=None
        )

    @classmethod
    def from_nowcast_entity(
            cls,
            nowcast_entity: NowcastEntity
    ) -> "WeatherModel":
        required_fields: list[str] = ["PTY", "RN1", "T1H", "REH"]

        if failed_fields := [
            field for field in required_fields
            if getattr(nowcast_entity, field) is None
        ]:
            raise ValueError(f"Failed to fetch data for: {', '.join(failed_fields)}")

        return cls(
            datetime=nowcast_entity.datetime,
            ICON=cls.get_weather_icon(
                lightning=nowcast_entity.LGT,
                precipitation_type=nowcast_entity.PTY,
                sky_code=nowcast_entity.SKY,
                rain_1hr=nowcast_entity.RN1
            ),
            RN1=nowcast_entity.RN1,
            T1H=nowcast_entity.T1H,
            REH=nowcast_entity.REH
        )
