from datetime import datetime
from dataclasses import dataclass


@dataclass
class ForecastEntity:
    datetime: datetime
    LGT: float | None
    PTY: float | None
    RN1: float | None
    SKY: float | None
    T1H: float | None

    @classmethod
    def from_dict(
            cls,
            forecast_entity: dict
    ) -> "ForecastEntity":
        return cls(
            datetime=forecast_entity["effective_time"],
            LGT=forecast_entity.get("LGT", None),
            PTY=forecast_entity.get("PTY", None),
            RN1=forecast_entity.get("RN1", None),
            SKY=forecast_entity.get("SKY", None),
            T1H=forecast_entity.get("T1H", None)
        )


@dataclass
class NowcastEntity(ForecastEntity):
    datetime: datetime
    REH: float | None

    @classmethod
    def from_dict(
            cls,
            nowcast_entity: dict
    ) -> "NowcastEntity":

        return cls(
            datetime=nowcast_entity["tm"],
            LGT=nowcast_entity["LGT"],
            PTY=nowcast_entity.get("PTY", None),
            RN1=nowcast_entity.get("RN1", None),
            SKY=nowcast_entity["SKY"],
            T1H=nowcast_entity.get("T1H", None),
            REH=nowcast_entity.get("REH", None),
        )
