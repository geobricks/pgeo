from pymongo import MongoClient
from bson.objectid import ObjectId
from pgeo.config.settings import settings


client = MongoClient(settings['db']['metadata']['connection'])
db = settings['db']['metadata']['database']
doc = settings['db']['metadata']['document']['layer']


def find_layer_by_id(layer_id):
    return client[db][doc].find_one({'_id': ObjectId(layer_id)})


def find_layers_by_dekad(dekad):
    return client[db][doc].find({'meContent.seReferencePopulation.referencePeriod.codes.code': {'$in': [dekad]}})


def find_layers_by_product(product):
    return client[db][doc].find({'meContent.seCoverage.coverageSector.codes.code': {'$in': [product]}})


def find_layers_by_product_and_dekad(product, dekad):
    return client[db][doc].find({'$and':[
                                    {'meContent.seCoverage.coverageSector.codes.code': {'$in': [product]}},
                                    {'meContent.seReferencePopulation.referencePeriod.codes.code': {'$in': [dekad]}}
                                ]})


def find_layers_by_product_and_dekad_and_type(product, dekad, type):
    return client[db][doc].find({'$and':[
                                    {'meContent.seCoverage.coverageSector.codes.code': {'$in': [product]}},
                                    {'meContent.seReferencePopulation.referencePeriod.codes.code': {'$in': [dekad]}},
                                    {'meStatisticalProcessing.seDatasource.seDataCompilation.aggregationProcessing': type}
                                ]})