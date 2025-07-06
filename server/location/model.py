from pydantic import BaseModel
from app.location.entity import AddressEntity, SunriseEntity


class AddressModel(BaseModel):
    address: str

    @classmethod
    def from_dataclass(
            cls,
            address_entity: AddressEntity
    ) -> "AddressModel":
        return cls(
            address=address_entity.address
        )



class SunriseModel(BaseModel):
    is_sunrise: bool

    @classmethod
    def from_dataclass(
            cls,
            sunrise_entity: SunriseEntity
    ) -> "SunriseModel":
        return cls(
            is_sunrise=sunrise_entity.is_sunrise
        )
