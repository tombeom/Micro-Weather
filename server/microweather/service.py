import os
import ephem
import httpx
import asyncio
from time import time
from fastapi import HTTPException
from pyproj import Proj, Transformer
from datetime import datetime, timedelta
from app.microweather.models import WeatherModel, CommonWeatherModel, CommonForecastModel, CommonNowcastModel, CommonParticulateMatterModel, ForecastModel, NowcastModel, ParticulateMatterModel

class WeatherService:
    def __init__(self, latitude: float, longitude: float) -> None:
        """
        클래스 초기화 메소드
        :param latitude: 위도
        :param longitude: 경도
        """
        self.longitude: float = longitude
        self.latitude: float = latitude
        self.current_time: datetime = datetime.now()
        self.open_api_key: str = os.getenv("OPEN_API_KEY")
        self.kma_hub_key: str = os.getenv("KMA_HUB_KEY")

        self._is_valid_coordinates()
        self.nowcast_datetime: dict = self._get_nowcast_datetime()
        self.forecast_datetime: dict = self._get_forecast_datetime()
        self.grid_coord: dict = self._get_grid_coordinates()
        self.utm_coord: dict = self._get_utm_coordinates()

    def _is_valid_coordinates(self) -> None:
        """
        위경도가 기상청 동네예보 API에서 지원하는 격자영역 내에 위치해있는지 확인하는 메소드
        """
        min_latitude: float = 33.10000000
        max_latitude: float = 38.45000000
        min_longitude: float = 125.06666667
        max_longitude: float = 131.87222222

        if not ((min_latitude <= self.latitude <= max_latitude) and (min_longitude <= self.longitude <= max_longitude)):
            raise HTTPException(status_code=404, detail="Coordinates are outside the support area.")

    def _get_nowcast_datetime(self) -> dict:
        """
        기상청 API허브 초단기실황 API 시간값 설정 메소드
        :return: dict
        """
        current_time: datetime = self.current_time
        if (current_time.hour == 0) and (current_time.minute < 10):
            nowcast_date: str = (current_time - timedelta(days=1)).strftime("%Y%m%d")
            nowcast_time: str = "2300"
            nowcast_datetime: dict = {"date": nowcast_date, "time": nowcast_time}
            return nowcast_datetime
        else:
            nowcast_date: str = current_time.strftime("%Y%m%d")
            if current_time.minute < 10:
                nowcast_time: str = (current_time - timedelta(hours=1)).strftime("%H") + "00"
            else:
                nowcast_time: str = current_time.strftime("%H") + "00"
            nowcast_datetime: dict = {"date": nowcast_date, "time": nowcast_time}
            return nowcast_datetime

    def _get_forecast_datetime(self) -> dict:
        """
        기상청 API허브 초단기예보 API 시간값 설정 메소드
        :return: dict
        """
        current_time: datetime = self.current_time
        if (current_time.hour == 0) and (current_time.minute < 45):
            forecast_date: str = (current_time - timedelta(days=1)).strftime("%Y%m%d")
            forecast_time: str = "2330"
            forecast_datetime: dict = {"date": forecast_date, "time": forecast_time}
            return forecast_datetime
        else:
            forecast_date: str = current_time.strftime("%Y%m%d")
            if current_time.minute < 30:
                forecast_time: str = (current_time - timedelta(hours=1)).strftime("%H") + "30"
            else:
                forecast_time: str = current_time.strftime("%H") + "30"
            forecast_datetime: dict = {"date": forecast_date, "time": forecast_time}
            return forecast_datetime

    def _get_grid_coordinates(self) -> dict:
        """
        위경도를 기상청 동네예보 API에서 사용하는 격자 좌표로 변환하는 메소드
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

        x_meters, y_meters = Transformer.from_proj("EPSG:4326", Proj(params), always_xy=True).transform(self.longitude,
                                                                                                        self.latitude)

        grid_x: int = int((x_meters / 5000) + 43)
        grid_y: int = int((y_meters / 5000) + 136)

        return {"grid_x": grid_x, "grid_y": grid_y}

    def _get_utm_coordinates(self) -> dict:
        """
        위경도를 EPSG:5178(UTM-K Bessel) 좌표계 기반의 좌표로 변환하는 메소드
        :return: dict
        """
        utm_x, utm_y = Transformer.from_crs("EPSG:4326", "EPSG:5178", always_xy=True).transform(self.longitude,
                                                                                                self.latitude)

        return {"utm_x": utm_x, "utm_y": utm_y}

    def _is_sunrise(self) -> bool:
        """
        위경도 값으로 일출 여부를 확인하는 메소드
        :return: bool
        """
        observer: ephem = ephem.Observer()
        observer.lat = self.latitude
        observer.lon = self.longitude
        observer.date = self.current_time

        sun: ephem = ephem.Sun()
        sunrise: datetime = observer.previous_rising(sun).datetime() + timedelta(hours=9)
        sunset: datetime = observer.previous_setting(sun).datetime() + timedelta(hours=9)

        if sunrise < self.current_time < sunset:
            return True
        else:
            return False

    def _set_near_stations(self) -> list | None:
        """
        한국환경공단 OPEN API를 사용해 TM 좌표 기반 근접 측정소 목록을 불러오는 메소드
        :return: list | None
        """
        try:
            url: str = "http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getNearbyMsrstnList"
            params: dict = {
                "serviceKey": self.open_api_key,
                "returnType": "json",
                "tmX": self.utm_coord["utm_x"],
                "tmY": self.utm_coord["utm_y"],
                "ver": "1.2"
            }
            response: httpx.Response = httpx.get(url=url, params=params, timeout=10.0)
            response_data: dict = response.json()
        except Exception as e:
            return None
        else:
            response_code: str = response_data["response"]["header"]["resultCode"]
            if not response_code == "00":
                return None
            else:
                particulate_matter_stations_list: list[dict, dict, dict] = response_data["response"]["body"]["items"]
                station_list: list = [station_dict["stationName"] for station_dict in particulate_matter_stations_list]
                return station_list
        finally:
            ...

    async def _get_address(self, client: httpx.AsyncClient) -> str | None:
        """
        Nominatim API를 사용해 위경도 값을 OpenStreetMap의 주소로 역지오코딩하는 메소드
        :param client: httpx.AsyncClient
        :return: str | None
        """
        url: str = "https://nominatim.openstreetmap.org/reverse"
        params: dict = {
            "format": "json",
            "lat": self.latitude,
            "lon": self.longitude,
            "zoom": "18"
        }
        response_data: dict = (await client.get(url=url, params=params, timeout=10.0)).json()
        address = response_data["address"]

        city_or_county = address.get("city") or address.get("county")
        road_or_village = address.get("road") or address.get("village")

        return f"{city_or_county} {road_or_village}"

    async def _get_nowcast(self, client: httpx.AsyncClient) -> CommonWeatherModel:
        """
        기상청 API허브의 초단기실황 조회 메소드
        :param client: httpx.AsyncClient
        :return: CommonWeatherModel
        """
        start = time()
        try:
            url: str = "https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0/getUltraSrtNcst"
            params: dict = {
                "authKey": self.kma_hub_key,
                "numOfRows": "30",
                "pageNo": "1",
                "dataType": "JSON",
                "base_date": self.nowcast_datetime["date"],
                "base_time": self.nowcast_datetime["time"],
                "nx": self.grid_coord["grid_x"],
                "ny": self.grid_coord["grid_y"]
            }
            response_data: dict = (await client.get(url=url, params=params, timeout=10.0)).json()
        except Exception as e:
            return CommonWeatherModel(type="nowcast", success=False, messages=str(e), processing_time=None, data=None)
        else:
            response_code: str = response_data["response"]["header"]["resultCode"]
            if not response_code == "00":
                return CommonWeatherModel(type="nowcast", success=False,
                                          messages=response_data["response"]["header"]["resultMsg"],
                                          processing_time=None, data=None)
            else:
                nowcast_list: list = response_data["response"]["body"]["items"]["item"]
                nowcast_dict: dict = {data["category"]: data["obsrValue"] for data in nowcast_list}

                nowcast_datetime: datetime = datetime.strptime(f"{response_data['response']['body']['items']['item'][0]['baseDate']} {response_data['response']['body']['items']['item'][0]['baseTime']}", "%Y%m%d %H%M")
                common_nowcast_model: CommonNowcastModel = CommonNowcastModel(datetime=nowcast_datetime, items=NowcastModel(PTY=nowcast_dict["PTY"], REH=nowcast_dict["REH"], RN1=nowcast_dict["RN1"], T1H=nowcast_dict["T1H"], UUU=nowcast_dict["UUU"], VEC=nowcast_dict["VEC"], VVV=nowcast_dict["VVV"], WSD=nowcast_dict["WSD"]))

                process_time: float = round(time() - start, 4)

                return CommonWeatherModel(type="nowcast", success=True, messages=None, processing_time=process_time,
                                          data=common_nowcast_model)
        finally:
            ...

    async def _get_forecast(self, client: httpx.AsyncClient) -> CommonWeatherModel:
        """
        기상청 API허브의 초단기예보 조회 메소드
        :param client: httpx.AsyncClient
        :return: CommonWeatherModel
        """
        start = time()
        try:
            url: str = "https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0/getUltraSrtFcst"
            params: dict = {
                "authKey": self.kma_hub_key,
                "numOfRows": "30",
                "pageNo": "1",
                "dataType": "JSON",
                "base_date": self.forecast_datetime["date"],
                "base_time": self.forecast_datetime["time"],
                "nx": self.grid_coord["grid_x"],
                "ny": self.grid_coord["grid_y"]
            }
            response_data: dict = (await client.get(url=url, params=params)).json()
        except Exception as e:
            return CommonWeatherModel(type="forecast", success=False, messages=str(e), processing_time=None, data=None)
        else:
            response_code: str = response_data["response"]["header"]["resultCode"]
            if not response_code == "00":
                return CommonWeatherModel(type="forecast", success=False,
                                          messages=response_data["response"]["header"]["resultMsg"],
                                          processing_time=None, data=None)
            else:
                forecast_list: list = response_data["response"]["body"]["items"]["item"]

                forecast_dict: dict = {
                    datetime.strptime(f"{data['fcstDate']} {data['fcstTime']}", "%Y%m%d %H%M"):
                        {data['category']: data['fcstValue'] for data in forecast_list if
                         data['fcstDate'] == data['fcstDate'] and data['fcstTime'] == data['fcstTime']}
                    for data in forecast_list
                }

                common_forecast_model_list: list[CommonForecastModel] = [
                    CommonForecastModel(
                        datetime=forecast_datetime,
                        items=ForecastModel(
                            LGT=forecast_data["LGT"],
                            PTY=forecast_data["PTY"],
                            RN1=forecast_data["RN1"],
                            SKY=forecast_data["SKY"],
                            T1H=forecast_data["T1H"]
                        )
                    )
                    for forecast_datetime, forecast_data in forecast_dict.items()
                ]

                process_time: float = round(time() - start, 4)

                return CommonWeatherModel(type="forecast", success=True, messages=None, processing_time=process_time,
                                          data=common_forecast_model_list)
        finally:
            ...

    async def _get_particulate_matter(self, client: httpx.AsyncClient, station_list: list, index: int = 0) -> CommonWeatherModel:
        """
        한국환경공단 OPEN API를 사용해 측정소명으로 실시간 대기 측정 정보를 조회하는 메소드
        :param client: httpx.AsyncClient
        :param station_list: list
        :param index: int
        :return:
        """
        start = time()
        try:
            url: str = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty"
            params: dict = {
                "serviceKey": self.open_api_key,
                "returnType": "json",
                "stationName": station_list[index],
                "dataTerm": "DAILY",
                "ver": "1.5",
            }
            response_data: dict = (await client.get(url=url, params=params)).json()
        except Exception as e:
            return CommonWeatherModel(type="particulate_matter", success=False, messages=str(e), processing_time=None, data=None)
        else:
            response_code: str = response_data["response"]["header"]["resultCode"]
            if not response_code == "00":
                return CommonWeatherModel(type="particulate_matter", success=False, messages=response_data["response"]["header"]["resultMsg"], processing_time=None, data=None)

            if not response_data["response"]["body"]["items"]:
                return CommonWeatherModel(type="particulate_matter", success=False, messages="No data", processing_time=None, data=None)

            particulate_matter_data: dict = response_data["response"]["body"]["items"][0]

            pm_10_value = None if particulate_matter_data["pm10Value"] == "-" else \
                particulate_matter_data["pm10Value"]
            pm_25_value = None if particulate_matter_data["pm25Value"] == "-" else \
                particulate_matter_data["pm25Value"]

            particulate_matter_datetime = datetime.strptime(particulate_matter_data["dataTime"], "%Y-%m-%d %H:%M")

            common_particulate_matter_model: CommonParticulateMatterModel = CommonParticulateMatterModel(datetime=particulate_matter_datetime, station_name=station_list[index], items=ParticulateMatterModel(pm10Value=pm_10_value, pm25Value=pm_25_value))
            process_time = round(time() - start, 4)
            return CommonWeatherModel(type="particulate_matter", success=True, messages=None, processing_time=process_time, data=common_particulate_matter_model)

    async def _fetch_weather_data(self, client: httpx.AsyncClient, station_list: list, index: int) -> tuple:
        """
        비동기 API 호출 메소드
        :param client: httpx.AsyncClient
        :param station_list: list
        :param index: list
        :return: tuple
        """
        return await asyncio.gather(
            self._get_address(client=client),
            self._get_nowcast(client=client),
            self._get_forecast(client=client),
            self._get_particulate_matter(client=client, station_list=station_list, index=index)
        )

    async def get_weather(self) -> WeatherModel:
        """
        클래스 외부 실행용 최종 데이터 반환 메소드
        :return: WeatherModel
        """
        start = time()
        is_sunrise: bool = self._is_sunrise()
        station_list: list = self._set_near_stations()
        pm_count = 0

        async with httpx.AsyncClient(timeout=10.0) as client:
            weather_data_list: tuple = await self._fetch_weather_data(client=client, station_list=station_list, index=pm_count)

            particular_matter_model = weather_data_list[3]

            if particular_matter_model.success is False:
                pm_count = pm_count + 1
                particular_matter_model = await self._get_particulate_matter(client=client, station_list=station_list, index=pm_count)

            if particular_matter_model.success is False:
                pm_count = pm_count + 1
                particular_matter_model = await self._get_particulate_matter(client=client, station_list=station_list, index=pm_count)

        process_time = round(time() - start, 4)
        return WeatherModel(
            address=weather_data_list[0],
            is_sunrise=is_sunrise,
            nowcast=weather_data_list[1],
            forecast=weather_data_list[2],
            particulate_matter=particular_matter_model,
            pm_count=(pm_count + 1),
            process_time=process_time
        )
