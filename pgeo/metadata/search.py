from pymongo import MongoClient
from bson.objectid import ObjectId
from pgeo.utils.date import dekad_to_day_from
from pgeo.utils.date import dekad_to_day_to
from pgeo.utils.log import logger

log = logger(__name__)


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
        #q['$and'] = conditions
        q["$query"] = {'$and' : conditions}
        #q["$project"] = {'$title' : 1}
        q["$orderby"] = {'meContent.seCoverage.coverageTime.to': 1, 'title': 1, }
        log.info(q)
        return self.client[self.db_name][self.table_name].find(q)

    def find_layers_by_dekad_range(self, dekad_from, dekad_to, product=None):
        """
        Find all the layers in the specified range.
        @param dekad_from: Starting dekad of the interval
        @type dekad_from: string
        @param dekad_to: Ending dekad of the interval
        @type dekad_to: string
        @param product: Product code, e.g. 'MOD13Q1'
        @type product: string
        @return: Array of layers in the dekads range
        """
        q = []
        p = {}
        p['url'] = '$meAccessibility.seDistribution.onlineResource'
        p['year'] = {'$year': '$meContent.seCoverage.coverageTime.from'}
        p['month_from'] = {'$month': '$meContent.seCoverage.coverageTime.from'}
        p['month_to'] = {'$month': '$meContent.seCoverage.coverageTime.to'}
        p['day_from'] = {'$dayOfMonth': '$meContent.seCoverage.coverageTime.from'}
        p['day_to'] = {'$dayOfMonth': '$meContent.seCoverage.coverageTime.to'}
        if product is not None:
            p['product'] = '$meContent.seCoverage.coverageSector.codes.code'
        a = {'$project': p}
        m = {}
        m['month_from'] = {'$gte': int(dekad_from[0:2])}
        m['month_to'] = {'$lte': int(dekad_to[0:2])}
        m['day_from'] = {'$gte': dekad_to_day_from(dekad_from)}
        m['day_to'] = {'$gte': dekad_to_day_to(dekad_to)}
        if product is not None:
            m['product'] = {'$in': [product]}
        b = {'$match': m}
        q.append(a)
        q.append(b)
        return self.client[self.db_name][self.table_name].aggregate(q)['result']


    def find_all(self, field):
        """
        Find all distinct values of a specific field
        @field field: field to search
        @type field: string
         """
        q = "meContent.seCoverage.coverageSector.codes.code"

        return self.client[self.db_name][self.table_name].distinct(q)