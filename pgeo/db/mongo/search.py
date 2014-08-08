from pymongo import MongoClient
from bson.objectid import ObjectId


class MongoSearch():

    def __init__(self, connection, db_name, table_name):
        """

        @param connection: Connection string for MongoDB
        @param db_name: Schema name for MongoDB
        @param table_name: Document name for MongoDB
        """
        self.connection = connection
        self.db_name = db_name
        self.table_name = table_name
        self.client = MongoClient(self.connection)

    def find_layer_by_id(self, layer_id):
        """
        Find a layer's metadata by Mongo uid
        @param layer_id: MongoDB uid
        @return: Metadata document in JSON format.
        """
        return self.client[self.db_name][self.table_name].find_one({'_id': ObjectId(layer_id)})

    def find_layers_by_product(self, product=None, dekad=None, agg_type=None, confidentiality=None):
        """
        Find layers according to user's selections.
        @param product: Product ID, e.g. 'MOD13Q1'
        @param dekad: Dekad, e.g. 08-1 for August 1st dekad
        @param agg_type: Aggregation type: none, avg or da
        @return: Array of metadata document in JSON format.
        """
        q = {}
        conditions = []
        if product is not None:
            conditions.append({'meContent.seCoverage.coverageSector.codes.code': {'$in': [product]}})
        if dekad is not None:
            conditions.append({'meContent.seReferencePopulation.referencePeriod.codes.code': {'$in': [dekad]}})
        if agg_type is not None:
            conditions.append({'meStatisticalProcessing.seDatasource.seDataCompilation.aggregationProcessing': agg_type})
        if confidentiality is not None:
            conditions.append({'meAccessibility.seConfidentiality.codes.code': {'$in': [confidentiality]}})
        q['$and'] = conditions
        return self.client[self.db_name][self.table_name].find(q)