from fastapi import Depends
from app.pm.model import ParticulateMatterModel
from app.pm.entity import ParticulateMatterStationEntity
from app.pm.repository import ParticulateMatterRepository, get_particulate_matter_repository


class ParticulateMatterService:
    def __init__(
            self,
            repository: ParticulateMatterRepository
    ):
        self.repository = repository

    async def get_particulate_matter(
            self,
            latitude: float,
            longitude: float
    ) -> ParticulateMatterModel:
        stations: ParticulateMatterStationEntity = await self.repository.get_near_particulate_matter_stations(
            latitude=latitude,
            longitude=longitude
        )

        return ParticulateMatterModel.from_dataclass(
            await self.repository.get_particulate_matter_by_stations(
                stations=stations
            )
        )


def get_particulate_matter_service(
        repository: ParticulateMatterRepository = Depends(get_particulate_matter_repository)
) -> ParticulateMatterService:
    return ParticulateMatterService(repository=repository)
