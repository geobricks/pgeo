import os
import json
from pgeo.utils.json import dict_merge_and_convert_dates
from pgeo.metadata.db_metadata import DBMetadata
from pgeo.metadata.search import MongoSearch
from pgeo.utils import log
from pgeo.config.metadata.core import template as core_template
from pgeo.config.metadata.raster import template as raster_template

log = log.logger(__name__)

# REMOVE EXAMPLE
#db.layer.remove({'meContent.seCoverage.coverageSector.codes.code': {'$in': ['EARTHSTAT']}})
#db.layer.remove({'meContent.seCoverage.coverageSector.codes.code': {'$in': ['TRMM']}})
# db.layer.remove({'meContent.seCoverage.coverageSector.codes.code': {'$in': ['MODIS']}})
# db.layer.find({'meContent.seCoverage.coverageSector.codes.code': {'$in': ['MODIS']}})
#db.layer.remove({'meContent.seCoverage.coverageSector.codes.code': {'$in': ['MODIS-SADC']}})
#db.layer.remove({'meContent.seCoverage.coverageSector.codes.code': {'$in': ['MODIS_TEST']}})
#db.layer.remove({'meContent.seCoverage.coverageSector.codes.code': {'$in': ['Doukkala-Seasonal-wheat']}})
#db.layer.remove({'meContent.seCoverage.coverageSector.codes.code': {'$in': ['Doukkala - actual evapotransipiration']}})

# with Regular expression
#db.layer.remove({'meContent.seCoverage.coverageSector.codes.code': {$regex: /^MOROCCO/}})

#db.layer.remove({'meContent.seCoverage.coverageSector.codes.code': {$regex: /^JRC/}})

#db.layer.find({'meContent.seCoverage.coverageSector.codes.code': {$regex: /^UMD/}})

#db.layer.find({'uid': {$regex: /^UMD/}})




class Metadata:

    db_metadata = None
    search = None

    def __init__(self, settings):
        self.settings = settings
        print settings
        self.db_metadata = DBMetadata(settings["db"]["metadata"])
        self.search = MongoSearch(settings["db"]["metadata"]['connection'], settings["db"]["metadata"]["database"], settings["db"]["metadata"]['document']['layer'])
        log.info("---Metadata initialization---")
        log.info(self.db_metadata)
        log.info(self.search)

    def merge_layer_metadata(self, template_name, data):
        """
            Merge user's data with the core metadata and the selected template
            @param template_name: Name of the template, e.g. 'modis'
            @param data: User data, in JSON format
            @return: Merged JSON
        """

        if template_name == "raster":
            out = dict_merge_and_convert_dates(core_template, raster_template)
        elif template_name == "vector":
            log.error("TODO: vector template")

        out = dict_merge_and_convert_dates(out, data)
        #log.info(out)
        return out