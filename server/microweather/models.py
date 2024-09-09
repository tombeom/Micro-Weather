from pydantic import BaseModel
from datetime import datetime


class NowcastModel(BaseModel):
    # 항목명 (단위)
    PTY: float  # 강수형태 (코드값) 0: 없음, 1: 비, 2: 비/눈, 3: 눈, 5: 빗방울 6: 빗방울눈날림. 7: 눈날림
    REH: float  # 습도 (%)
    RN1: float  # 1시간 강수량 (mm)
    T1H: float  # 기온 (℃)
    UUU: float  # 동서바람성분 (m/s)
    VEC: float  # 풍향 (deg)
    VVV: float  # 남북바람성분 (m/s)
    WSD: float  # 풍속 (m/s)


class ForecastModel(BaseModel):
    LGT: float  # 낙뢰 (kA)
    PTY: float  # 강수형태(코드값) 0: 없음, 1: 비, 2: 비/눈, 3: 눈, 5: 빗방울 6: 빗방울눈날림. 7: 눈날림
    RN1: str  # 1시간 강수량 (범주) "강수없음", "1.0mm 미만", "1.0mm~29.9mm", "30.0~50.0mm", "50.0mm 이상"
    SKY: float  # 하늘상태 (코드값) 1: 맑음, 3: 구름많음, 4: 흐림
    T1H: float  # 기온 (℃)


class ParticulateMatterModel(BaseModel):
    pm10Value: int | None
    pm25Value: int | None 


class CommonNowcastModel(BaseModel):
    datetime: datetime  # 발표일자, 시각
    items: NowcastModel


class CommonForecastModel(BaseModel):
    datetime: datetime
    items: ForecastModel


class CommonParticulateMatterModel(BaseModel):
    datetime: datetime
    station_name: str
    items: ParticulateMatterModel


class CommonWeatherModel(BaseModel):
    type: str
    success: bool
    messages: str | None
    processing_time: float | None
    data: CommonNowcastModel | list[CommonForecastModel] | CommonParticulateMatterModel | None


class WeatherModel(BaseModel):
    address: str | None = None
    is_sunrise: bool
    nowcast: CommonWeatherModel
    forecast: CommonWeatherModel
    particulate_matter: CommonWeatherModel
    pm_count: int
    process_time: float
