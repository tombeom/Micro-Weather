from pyproj import Proj, Transformer
from pydantic import BaseModel, model_validator


class CoordinatesModel(BaseModel):
    latitude: float
    longitude: float

    @model_validator(mode="after")
    @classmethod
    def validate_coordinates(
            cls,
            coordinates: "CoordinatesModel"
    ):
        if not (33.10000000 <= coordinates.latitude <= 38.45000000):
            raise ValueError("Latitude must be between 33.1 and 38.45")

        if not (125.06666667 <= coordinates.longitude <= 131.87222222):
            raise ValueError("Longitude must be between 125.06666667 and 131.87222222")

        return coordinates

    def get_grid_coordinates(
            self,
    ) -> tuple[int, int]:
        """
        위경도를 기상청 동네예보에서 사용하는 격자 좌표로 변환하는 메소드
        :return: tuple
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

        x_meters, y_meters = Transformer.from_proj(
            "EPSG:4326",
            Proj(params),
            always_xy=True
        ).transform(self.longitude, self.latitude)

        grid_x: int = int((x_meters / 5000) + 43)
        grid_y: int = int((y_meters / 5000) + 136)

        return grid_x, grid_y

