from geopy.geocoders import Nominatim
from pgeo.error.custom_exceptions import PGeoException, errors
from pgeo.utils import log

geolocator = Nominatim()

def get_location(place):
    """
    @param place: place to search i.e. "FAO, roma"
    @param string:
    @return: location obj containing the location.address and  location.latitude location.longitude
             retrun None if place not found
    """
    try:
        return geolocator.geocode(place)
    except Exception, e:
        raise PGeoException(e, status_code=400)