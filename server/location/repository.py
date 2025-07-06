from fastapi import Depends
from datetime import datetime, timedelta
from app.database.mongo import Mongo, get_mongo
from app.location.entity import AddressEntity, SunriseEntity

from astropy import units
from astropy.time import Time
from astroplan import Observer
from astropy.coordinates import EarthLocation


class LocationRepository:
    def __init__(
            self,
            mongo: Mongo
    ):
        self.mongo = mongo

    async def get_address_by_coordinates(
            self,
            latitude: float,
            longitude: float
    ) -> AddressEntity:
        try:
            address: dict = await self.mongo.location.find_one({
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
        except Exception as e:
            raise ValueError("Invalid coordinates or address not found")
        else:
            if address:
                return AddressEntity(address=address["location"])
            else:
                raise ValueError("Address not found")

    @staticmethod
    async def is_sunrise_by_coordinates(
            latitude: float,
            longitude: float
    ) -> SunriseEntity:
        current_time: datetime = datetime.now()

        location: EarthLocation = EarthLocation(
            lon=longitude * units.deg,
            lat=latitude * units.deg
        )
        observer: Observer = Observer(
            location=location,
            name="Observer"
        )

        time: Time = Time(
            (current_time - timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S'),
            format='iso',
            scale='utc'
        )

        sunrise_utc: Time = observer.sun_rise_time(
            time, which="previous", horizon=-0.8333 * units.deg
        ).to_datetime()
        sunset_utc: Time = observer.sun_set_time(
            time, which="next", horizon=-0.8333 * units.deg
        ).to_datetime()

        sunrise = sunrise_utc + timedelta(hours=9)
        sunset = sunset_utc + timedelta(hours=9)

        if sunrise < current_time < sunset:
            return SunriseEntity(is_sunrise=True)
        else:
            return SunriseEntity(is_sunrise=False)


def get_location_repository(
        mongo: Mongo = Depends(get_mongo)
) -> LocationRepository:
    return LocationRepository(mongo=mongo)
