from dataclasses import dataclass


@dataclass
class AddressEntity:
    address: str


@dataclass
class SunriseEntity:
    is_sunrise: bool
