import ephem
import asyncio
from fastapi import HTTPException
from pyproj import Proj, Transformer
from datetime import datetime, timedelta
from app.microweather.database import Database
from app.microweather.models import WeatherModel, NowcastModel, ForecastModel, ParticulateMatterModel


class WeatherService:
    def __init__(self, latitude: float, longitude: float) -> None:
        """
        클래스 초기화 메소드
        :param latitude: 위도
        :param longitude: 경도
        """
        self.longitude: float = longitude
        self.latitude: float = latitude
        self._is_valid_coordinates(latitude=self.latitude, longitude=self.longitude)
        self.grid_coord: dict = self._get_grid_coordinates(latitude=self.latitude, longitude=self.longitude)

    async def get_weather(self) -> WeatherModel:
        """
        클래스 외부 실행용 최종 데이터 반환 메소드
        :return: WeatherModel
        """
        address, is_sunrise, nowcast_model, forecast_model, particulate_matter = await asyncio.gather(
            self._get_address(latitude=self.latitude, longitude=self.longitude),
            self._is_sunrise(latitude=self.latitude, longitude=self.longitude),
            self._get_nowcast(grid_x=self.grid_coord["grid_x"], grid_y=self.grid_coord["grid_y"]),
            self._get_forecast(grid_x=self.grid_coord["grid_x"], grid_y=self.grid_coord["grid_y"]),
            self._get_particulate_matter(latitude=self.latitude, longitude=self.longitude)
        )
        return WeatherModel(
            address=address,
            is_sunrise=is_sunrise,
            nowcast=nowcast_model,
            forecast=forecast_model,
            particulate_matter=particulate_matter
        )

    @staticmethod
    async def _get_address(latitude: float, longitude: float) -> str:
        """
        위경도 값으로 위치한 읍면동 위치를 확인하는 메소드
        :param latitude: float
        :param longitude: float
        :return: str
        """
        async with Database() as db:
            address: dict = await db.location.find_one({
                "geometry": {
                    "$geoIntersects": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates":
                                [longitude, latitude],
                        }
                    }
                }
            })
        return address["location"]

    @staticmethod
    def _is_valid_coordinates(latitude: float, longitude: float) -> None:
        """
        위경도가 기상청 동네예보 격자영역 내에 위치해있는지 확인하는 메소드
        """
        min_latitude: float = 33.10000000
        max_latitude: float = 38.45000000
        min_longitude: float = 125.06666667
        max_longitude: float = 131.87222222

        if not ((min_latitude <= latitude <= max_latitude) and (min_longitude <= longitude <= max_longitude)):
            raise HTTPException(status_code=404, detail="Coordinates are outside the support area.")

    @staticmethod
    def _get_grid_coordinates(latitude: float, longitude: float) -> dict:
        """
        위경도를 기상청 동네예보에서 사용하는 격자 좌표로 변환하는 메소드
        :return: dict
        """
        params: dict = {
            "proj": "lcc",
            "lat_1": 30.0,
            "lat_2": 60.0,
            "lat_0": 38.0,
            "lon_0": 126.0,
            "datum": "WGS84",
            "units": "m"
        }

        x_meters, y_meters = Transformer.from_proj("EPSG:4326", Proj(params), always_xy=True).transform(longitude, latitude)

        grid_x: int = int((x_meters / 5000) + 43)
        grid_y: int = int((y_meters / 5000) + 136)

        return {"grid_x": grid_x, "grid_y": grid_y}

    @staticmethod
    async def _is_sunrise(latitude: float, longitude: float) -> bool:
        """
        위경도 값으로 일출 여부를 확인하는 메소드
        :param latitude: float
        :param longitude: float
        :return: bool
        """
        current_time: datetime = datetime.now()

        observer: ephem = ephem.Observer()
        observer.lat = latitude
        observer.lon = longitude
        observer.date = current_time

        sun: ephem = ephem.Sun()
        sunrise: datetime = observer.previous_rising(sun).datetime() + timedelta(hours=9)
        sunset: datetime = observer.previous_setting(sun).datetime() + timedelta(hours=9)

        if sunrise < current_time < sunset:
            return True
        else:
            return False

    @staticmethod
    async def _set_near_stations(latitude: float, longitude: float) -> list[str]:
        """
        근접 측정소 조회 메소드
        :param latitude: float
        :param longitude: float
        :return: list[str]
        """
        async with Database() as db:
            near_stations: list[dict] = await db.pm_station.find({
                "geometry": {
                    "$near": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [longitude, latitude]
                        },
                    }
                }
            }).to_list(length=3)

        near_station_list: list[str] = [station["station_name"] for station in near_stations]
        return near_station_list

    @staticmethod
    async def _get_nowcast(grid_x: int, grid_y: int) -> NowcastModel:
        """
        초단기실황 데이터 조회 메소드
        :param grid_x: int
        :param grid_y: int
        :return: NowcastModel
        """
        async with Database() as db:
            nowcast_data: dict = await db.nowcast.find_one({"nx": grid_x, "ny": grid_y}, sort=[("tm", -1)])
        return NowcastModel(
            datetime=nowcast_data["tm"],
            PTY=nowcast_data["PTY"] if nowcast_data["PTY"] is not None else 0,
            REH=nowcast_data["REH"] if nowcast_data["REH"] is not None else 99,
            RN1=nowcast_data["RN1"] if nowcast_data["RN1"] is not None else 0,
            T1H=nowcast_data["T1H"] if nowcast_data["T1H"] is not None else 99
        )

    @staticmethod
    async def _get_forecast(grid_x: int, grid_y: int) -> list[ForecastModel]:
        """
        초단기예보 데이터 조회 메소드
        :param grid_x: int
        :param grid_y: int
        :return: list[ForecastModel]
        """
        async with Database() as db:
            forecast_data: dict = await db.forecast.find_one({"nx": grid_x, "ny": grid_y}, sort=[("tm", -1)])

        forecast_model_list: list[ForecastModel] = [
            ForecastModel(
                datetime=data["effective_time"],
                LGT=data["LGT"] if data["LGT"] is not None else 0,
                PTY=data["PTY"] if data["PTY"] is not None else 0,
                RN1=data["RN1"] if data["RN1"] is not None else 99,
                SKY=data["SKY"] if data["SKY"] is not None else 1,
                T1H=data["T1H"] if data["T1H"] is not None else 99
            )
            for data in forecast_data["items"]
        ]
        return forecast_model_list

    @staticmethod
    async def _get_particulate_matter(latitude: float, longitude: float) -> ParticulateMatterModel:
        """
        미세먼지 데이터 조회 메소드
        :param latitude: float
        :param longitude: float
        :return: ParticulateMatterModel
        """
        async with Database() as db:
            near_stations: list[dict] = await db.pm_station.find({
                "geometry": {
                    "$near": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [longitude, latitude]
                        },
                    }
                }
            }).to_list(length=3)
            near_station_list: list[str] = [station["station_name"] for station in near_stations]
            particulate_matter_list: list[dict] = await db.pm_data.find({"station_name": {"$in": near_station_list}}, sort=[("tm", -1)]).to_list(length=None)

        for particulate_matter in particulate_matter_list:
            if (particulate_matter.get("pm10Value") is not None) or (particulate_matter.get("pm25Value") is not None):
                return ParticulateMatterModel(
                    datetime=particulate_matter.get("dataTime"),
                    station_name=particulate_matter.get("station_name"),
                    pm10Value=particulate_matter.get("pm10Value"),
                    pm10Grade=particulate_matter.get("pm10Grade1h"),
                    pm25Value=particulate_matter.get("pm25Value"),
                    pm25Grade=particulate_matter.get("pm25Grade1h")
                )

        return ParticulateMatterModel(
            datetime=particulate_matter_list[0].get("dataTime"),
            station_name=particulate_matter_list[0].get("station_name"),
            pm10Value=particulate_matter_list[0].get("pm10Value"),
            pm10Grade=particulate_matter_list[0].get("pm10Grade1h"),
            pm25Value=particulate_matter_list[0].get("pm25Value"),
            pm25Grade=particulate_matter_list[0].get("pm25Grade1h")
        )
