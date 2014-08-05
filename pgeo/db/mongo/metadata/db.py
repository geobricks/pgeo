import pymongo
from pgeo.db.mongo import common
from pgeo.config.settings import settings
from pgeo.config.settings import read_config_file_json


print settings['db']['metadata']['document']['layer']
client = pymongo.MongoClient(settings['db']['metadata']['connection'])
database = settings['db']['metadata']['database']
document_layer = settings['db']['metadata']['document']['layer']


def insert_metadata(json):
    """
    Insert Layer Metadata in mongodb
    @param json: json data
    @return: id
    """
    return common.insert(client, database, document_layer, json)


def remove_metadata(json):
    """
    Delete Layer Metadata in mongodb
    @param json: json data
    @return: id
    """
    return common.remove(client, database, document_layer, json)


def find(collection):
    """
    Return entire collection
    @param collection: collection
    @return: collection
    """
    return common.find(client, database, collection, { "$query": {}, "$orderby": [{ "layertitle": 1 }, {"date": 1}]})


def find_query(collection, query):
    """
    Return entire collection
    @param collection: collection
    @param query: mongodb query
    @return: collection
    """
    return common.find(client, database, collection, query)


def find_by_layer_name(collection, layer_name):
    """
    Return the document containing the layername
    @param collection: collection (i.e. layer)
    @param layer_name: layername stored in the db
    @return: collection
    """
    return common.find(client, database, collection, {"$query": {"layername": layer_name}, "$orderby": [{"layertitle" : 1}]})


def find_by_code(collection, code, sort_date):
    return common.find(client, database, collection, {"$query": {"code": code}, "$orderby": [{"coverageTime.from": sort_date}]})
