import pymongo
from pgeo.db.mongo import common
from pgeo.utils import log

log = log.logger(__name__)


class DBMetadata:

    # client = pymongo.MongoClient(settings['db']['metadata']['connection'])
    # database = settings['db']['metadata']['database']
    # document_layer = settings['db']['metadata']['document']['layer']

    def __init__(self, config):
        """
        @param config: config parameters to configure the metadata db
        @return:
        """

        self.config = config
        self.client = pymongo.MongoClient(config['connection'])
        self.database = config['database']
        self.document_layer = config['document']['layer']

    def insert_metadata(self, json):
        """
        Insert Layer Metadata in mongodb
        @param json: json data
        @return: id
        """
        log.info(json)
        return common.insert(self.client, self.database, self.document_layer, json)

    def remove_metadata(self, json):
        """
        Delete Layer Metadata in mongodb
        @param json: json data
        @return: id
        """
        return common.remove(self.client, self.database, self.document_layer, json)

    def remove_metadata_by_id(self, id):
        """
        Delete Layer Metadata in mongodb
        @param id: Metadata's id
        @return: id
        """
        return common.remove_by_id(self.client, self.database, self.document_layer, id)