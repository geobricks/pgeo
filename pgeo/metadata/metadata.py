from pgeo.config.settings import read_template
from pgeo.utils.json import dict_merge_and_convert_dates
from pgeo.metadata.db_metadata import DBMetadata
from pgeo.metadata.search import MongoSearch
from pgeo.utils import log

log = log.logger(__name__)

# REMOVE EXAMPLE
#db.layer.remove({'meContent.seCoverage.coverageSector.codes.code': {'$in': ['EARTHSTAT']}})


class Metadata:

    db_metadata = None
    seach = None

    def __init__(self, config):
        self.config = config
        self.db_metadata = DBMetadata(config)
        self.search = MongoSearch(config['connection'], config["database"], config['document']['layer'])
        log.info("---Metadata initialization---")
        log.info(self.db_metadata)
        log.info(self.search)



def merge_layer_metadata(template_name, data):
    """
        Merge user's data with the core metadata and the selected template
        @param template_name: Name of the template, e.g. 'modis'
        @param data: User data, in JSON format
        @return: Merged JSON
    """
    core_template = read_template('core')
    template = read_template(template_name)
    out = dict_merge_and_convert_dates(core_template, data)
    #log.info(out)
    out = dict_merge_and_convert_dates(out, template)
    #log.info(out)
    return out