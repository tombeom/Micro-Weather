from typing import Annotated
from fastapi import APIRouter, Depends
from app.pm.model import ParticulateMatterModel
from app.utils.coordinate import CoordinatesModel
from app.pm.service import ParticulateMatterService, get_particulate_matter_service

router = APIRouter(prefix="/particulate-matter")

CoordinatesQueryParams = Annotated[CoordinatesModel, Depends(CoordinatesModel)]
ParticulateMatterService = Annotated[ParticulateMatterService, Depends(get_particulate_matter_service)]


@router.get(
    "",
    status_code=200,
    response_model=ParticulateMatterModel
)
async def get_particulate_matter(
        coordinates: CoordinatesQueryParams,
        service: ParticulateMatterService
) -> ParticulateMatterModel:
    return await service.get_particulate_matter(
        latitude=coordinates.latitude,
        longitude=coordinates.longitude
    )
