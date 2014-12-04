from geopy.geocoders import Nominatim
from pgeo.error.custom_exceptions import PGeoException
import time

geolocator = Nominatim()

cached_places = {}

def get_locations(places):
    try:
        results = []
        for place in places:
            if place in cached_places:
                results.append(cached_places[place])
            else:
                time.sleep(1.1)
                result = get_location(place)
                cached_places[place] = result
                results.append(result)
        return results
    except Exception, e:
        pass

def get_location(place):
    """
    @param place: place to search i.e. "FAO, roma"
    @type: string:
    @return: location obj containing the location.raw, location.address and location.latitude location.longitude
             return None if place not found
    """
    try:
        location = geolocator.geocode(place)
        return [location.latitude, location.longitude]
        #return geolocator.geocode(place)
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