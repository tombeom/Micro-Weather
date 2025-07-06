from typing import Annotated
from fastapi import APIRouter, Depends
from app.utils.coordinate import CoordinatesModel
from app.location.model import AddressModel, SunriseModel
from app.location.service import LocationService, get_location_service

router = APIRouter(prefix="/location")

CoordinatesQueryParams = Annotated[CoordinatesModel, Depends(CoordinatesModel)]
LocationService = Annotated[LocationService, Depends(get_location_service)]


@router.get(
    "/address",
    status_code=200,
    response_model=AddressModel
)
async def get_address(
        coordinates: CoordinatesQueryParams,
        service: LocationService,
) -> AddressModel:
    return await service.get_address(
        latitude=coordinates.latitude,
        longitude=coordinates.longitude,
    )


@router.get(
    "/sunrise",
    status_code=200,
    response_model=SunriseModel
)
async def is_sunrise(
        coordinates: CoordinatesQueryParams,
        service: LocationService,
) -> SunriseModel:
    return await service.is_sunrise(
        latitude=coordinates.latitude,
        longitude=coordinates.longitude
    )
