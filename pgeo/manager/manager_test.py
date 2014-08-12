from pgeo.config.settings import settings
from pgeo.manager.manager import Manager
from pgeo.utils import log
import json
import copy
import random

log = log.logger("pgeo.manager.manager_test")

manager = Manager(settings)


# Publish a Shapefile
layer_def = {
        "title" : "ne_110m_dddgeography_regions3333222_poly",
        "abstract" : "ne_110m_geography_reeeeegions_polys33332",
        # "workspace" : "fenix",
        # "datastore" : "pgeo",
        "enabled" : True,
        "defaultStyle" : {
            "name" : "population"
        }
}
metadata_def = copy.deepcopy(layer_def)
manager.publish_shapefile("/home/vortex/Desktop/LAYERS/test_imports/shapefile/ne_110m_geography_regions_polys.zip", metadata_def, layer_def)



# Publish a Coveragestore
# randomName = random.random()
# name = "test" + str(randomName).replace(".", "")
# layer_coverage_def = {
#         "name" : name,
#         "title" : "aaasetta sto tile!",
#         "abstract" : "MODIS iuhadiuh",
#         "workspace" : "fenix",
#         "path" : "/home/vortex/Desktop/LAYERS/MODIS/AB_NDVI_4326.tif",
#         "defaultStyle": {
#             "name": "rain"
#         }
# }
# metadata_coverage_def = copy.deepcopy(layer_coverage_def)
# manager.publish_coverage("/home/vortex/Desktop/LAYERS/MODIS/AB_NDVI_4326.tif", metadata_coverage_def, layer_coverage_def)

