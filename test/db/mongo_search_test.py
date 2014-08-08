import unittest
from pgeo.config.settings import settings
from pgeo.db.mongo.search import MongoSearch
from pgeo.db.mongo.metadata.db import remove_metadata_by_id


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
        self.failUnlessEqual(6, layers.count())

    def test_search_by_dekad(self):
        dekad = '08-1'
        layers = self.mongo_search.find_layers_by_product(None, dekad)
        self.failUnlessEqual(1, layers.count())

    def test_search_by_type(self):
        type = 'avg'
        layers = self.mongo_search.find_layers_by_product(None, None, type)
        self.failUnlessEqual(6, layers.count())

    def test_search_by_confidentiality(self):
        confidentiality = 'private'
        layers = self.mongo_search.find_layers_by_product(None, None, None, confidentiality)
        self.failUnlessEqual(1, layers.count())

    def test_search_by_dekad_range(self):
        layers = self.mongo_search.find_layers_by_dekad_range('08-3', '08-3')
        self.failUnlessEqual(4, len(layers))

    def test_search_by_dekad_range_and_product(self):
        layers = self.mongo_search.find_layers_by_dekad_range('08-3', '08-3', 'MOD13Q1')
        self.failUnlessEqual(1, len(layers))

    def test_delete_by_id(self):
        id = '53e495e4f8cd6719385f81a0'
        layer = self.mongo_search.find_layer_by_id(id)
        self.failUnless(layer is not None)
        remove_metadata_by_id(id)
        layer = self.mongo_search.find_layer_by_id(id)
        self.failUnless(layer is None)


if __name__ == '__main__':
    unittest.main()