# from pgeo.config.settings import read_template
import os
import json
from pgeo.utils.json import dict_merge_and_convert_dates
from pgeo.metadata.db_metadata import DBMetadata
from pgeo.metadata.search import MongoSearch
from pgeo.utils import log

log = log.logger(__name__)

# REMOVE EXAMPLE
#db.layer.remove({'meContent.seCoverage.coverageSector.codes.code': {'$in': ['EARTHSTAT']}})
#db.layer.remove({'meContent.seCoverage.coverageSector.codes.code': {'$in': ['TRMM']}})
# db.layer.remove({'meContent.seCoverage.coverageSector.codes.code': {'$in': ['MODIS']}})
# db.layer.find({'meContent.seCoverage.coverageSector.codes.code': {'$in': ['MODIS']}})


#db.layer.remove({'meContent.seCoverage.coverageSector.codes.code': {'$in': ['MODIS-SADC']}})


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

    def read_template(self, filename):
        try:
            directory = os.path.dirname(os.path.dirname(__file__))
            filename = filename.lower()
            path = os.path.join(directory, self.settings['folders']['metadata_templates'])
            extension = '' if '.json' in filename else '.json'
            return json.loads(open(path + filename + extension).read())
        except Exception, e:
            print e

    def merge_layer_metadata(self, template_name, data):
        """
            Merge user's data with the core metadata and the selected template
            @param template_name: Name of the template, e.g. 'modis'
            @param data: User data, in JSON format
            @return: Merged JSON
        """

        core_template = self.read_template('core')
        template = self.read_template(template_name)
        out = dict_merge_and_convert_dates(core_template, data)
        #log.info(out)
        out = dict_merge_and_convert_dates(out, template)
        #log.info(out)
        return out


