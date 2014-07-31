from pgeo.gis import raster
from pgeo.utils import log
from os import path
import sys

log = log.logger(__name__)



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