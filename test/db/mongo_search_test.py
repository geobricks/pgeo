import unittest
from pgeo.config.settings import settings
from pgeo.db.mongo.search import MongoSearch
from bson import json_util


class MongoSearchTestClass(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(MongoSearchTestClass, self).__init__(*args, **kwargs)
        self.connection = settings['db']['metadata']['connection']
        self.db = settings['db']['metadata']['database']
        self.doc = settings['db']['metadata']['document']['layer']
        self.mongo_search = MongoSearch(self.connection, self.db, self.doc)

    def test_search_by_id(self):
        id = '53e2049cf8cd6721163e0bdb'
        layers = self.mongo_search.find_layer_by_id(id)
        self.failUnless(layers is not None)

    def test_search_by_product(self):
        product = 'MOD13Q1'
        layers = self.mongo_search.find_layers_by_product(product)
        self.failUnlessEqual(3, layers.count())

    def test_search_by_dekad(self):
        dekad = '08-1'
        layers = self.mongo_search.find_layers_by_product(None, dekad)
        self.failUnlessEqual(1, layers.count())

    def test_search_by_type(self):
        type = 'avg'
        layers = self.mongo_search.find_layers_by_product(None, None, type)
        self.failUnlessEqual(3, layers.count())

if __name__ == '__main__':
    unittest.main()