from pgeo.geoserver.geoserver import Geoserver
from pgeo.config.settings import settings
from pgeo.utils import log
from pgeo.error.custom_exceptions import PGeoException
import sys

log = log.logger("pgeo.geoserver.geoserver_test")


g = Geoserver(settings["geoserver"])


layer_to_publish = {
    "name" : "test3",
    "workspace" : "fenix",
    "path" : "/home/vortex/Desktop/LAYERS/MODIS/AB_NDVI_4326.tif"
}



try:
    layer = g.publish_coveragestore(layer_to_publish, False)
except PGeoException, e:
    log.error(e)
