from pgeo.gis import raster
from pgeo.utils import log
from pgeo.gis import geocoding
from os import path
import sys

log = log.logger(__name__)



def processing_raster():
    config = {
        "descriptive_statistics": {
            "force": True
        },
        "histogram": {
            "buckets": 256,
            "force": True
        }
    }
    raster_path = '/home/vortex/Desktop/LAYERS/TRMM/data/trmm/3B42RT.2014010100.7.03hr/3B42RT.2014010100.7.03hr.geotiff'
    query = "select * from spatial.g2008_0 where adm0_code IN('68')"
    db_connection_string = "PG:host=localhost port=5432 dbname=pgeo user=fenix password=Qwaszx"

    raster_processed_path = raster.crop_by_vector_database(raster_path, query, db_connection_string)
    stats = raster.get_statistics(raster_processed_path, config)
    log.info(stats)


def location_values(lat, lon):
    #tiffs = glob.glob("/home/vortex/programs/layers/raster/TRMM/3B42RT/2014/03/original/*.tif")
    # tiffs = glob.glob("/home/vortex/programs/layers/raster/RASTER/Vegetation/NDVI/*.tif")
    #tiffs = glob.glob("/home/vortex/programs/layers/raster/TRMM/3B42RT/2014/03/original/geotiff/*.tif")
    tiffs = [
        "/home/vortex/Desktop/LAYERS/TRMM/2014/07/output/trmm_07_2014.tif"
    ]
    #return raster.location_values(tiffs, 41.005, 12.22)
    #return raster.location_values(tiffs, 1452160.76088, 5096412.999)
    return raster.location_values(tiffs, lat, lon)

l = geocoding.get_location("via bonn, aprilia")
log.info(location_values(l.latitude, l.longitude))

l = geocoding.get_location("via morrovalle 58, roma")
log.info(location_values(l.latitude, l.longitude))


