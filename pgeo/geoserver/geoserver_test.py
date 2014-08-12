from pgeo.geoserver.geoserver import Geoserver
from pgeo.config.settings import settings
from pgeo.utils import log
from pgeo.error.custom_exceptions import PGeoException
import sys
import random

log = log.logger("pgeo.geoserver.geoserver_test")


g = Geoserver(settings["geoserver"])

randomName = random.random()
name = "test" + str(randomName).replace(".", "")

layer_to_publish = {
    "name" : name,
    "title" : "MODIS iuhadiuh",
    "description" : "MODIS iuhadiuh",
    "workspace" : "fenix",
    "path" : "/home/vortex/Desktop/LAYERS/MODIS/AB_NDVI_4326.tif"
}


try:
    if g.publish_coveragestore(layer_to_publish, True):
        log.info("upload done")
    else:
        log.error("not uploaded")
except PGeoException, e:
    log.error(e)

