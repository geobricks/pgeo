import unittest
import json
import glob
from pymongo import MongoClient
from pgeo.db.mongo.metadata.db import insert_metadata
from pgeo.metadata.metadata import merge_layer_metadata


class DBSetupTestClass(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(DBSetupTestClass, self).__init__(*args, **kwargs)
        self.connection = 'mongodb://localhost:27017/'
        self.db = 'metadata_test'
        self.doc = 'layer'

    def setUp(self):
        files = glob.glob('../resources/metadata/modis/*.json')
        for file in files:
            user_json=open(file).read()
            data = json.loads(user_json)
            merged = merge_layer_metadata('modis', data)
            mongo_id = str(insert_metadata(merged))

    def tearDown(self):
        client = MongoClient(self.connection)
        client[self.db].drop_collection(self.doc)

    def test_01(self):
        self.assertTrue(True)