from geopy.geocoders import Nominatim
from pgeo.error.custom_exceptions import PGeoException, errors
from pgeo.utils import log

geolocator = Nominatim()


def get_location(place):
    """
    @param place: place to search i.e. "FAO, roma"
    @type: string:
    @return: location obj containing the location.raw, location.address and location.latitude location.longitude
             return None if place not found
    """
    try:
        return geolocator.geocode(place)
    except Exception, e:
        raise PGeoException(e, status_code=400)


def get_reverse(lat, lon):
    """
    @param lat: place to search i.e. "52.509669"
    @type: float
    @param lon: place to search i.e. "13.376294"
    @type: float
    @return: location obj containing the location.raw, location.address and location.latitude location.longitude
             return None if place not found
    """
    try:
        return geolocator.reverse(lat, lon)
    except Exception, e:
        raise PGeoException(e, status_code=400)
