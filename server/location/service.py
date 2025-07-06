from fastapi import HTTPException, Depends
from app.location.model import AddressModel, SunriseModel
from app.location.entity import AddressEntity, SunriseEntity
from app.location.repository import LocationRepository, get_location_repository


class LocationService:
    def __init__(
            self,
            repository: LocationRepository
    ):
        self.repository = repository

    async def get_address(
            self,
            latitude: float,
            longitude: float
    ) -> AddressModel:
        try:
            address: AddressEntity = await self.repository.get_address_by_coordinates(
                latitude=latitude,
                longitude=longitude
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail="Invalid coordinates or address not found"
            )
        else:
            return AddressModel.from_dataclass(address_entity=address)

    async def is_sunrise(
            self,
            latitude: float,
            longitude: float
    ) -> SunriseModel:
        try:
            sunrise: SunriseEntity = await self.repository.is_sunrise_by_coordinates(
                latitude=latitude,
                longitude=longitude
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail="Invalid coordinates or sunrise data not found"
            )
        else:
            return SunriseModel.from_dataclass(sunrise_entity=sunrise)


def get_location_service(
        repository: LocationRepository = Depends(get_location_repository)
) -> LocationService:
    return LocationService(repository=repository)
