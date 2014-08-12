import unittest
import json
import glob
from pymongo import MongoClient
from pgeo.metadata.metadata import merge_layer_metadata
from pgeo.metadata.db_metadata import DBMetadata
#from pgeo.db.mongo.metadata.db import insert_metadata


class DBSetupTestClass(unittest.TestCase):

    config = {
        "connection": "mongodb://localhost:27017/",
        "database": "test_metadata",
        "document": {
            "layer": "layer"
        }
    }

    def __init__(self, *args, **kwargs):
        super(DBSetupTestClass, self).__init__(*args, **kwargs)
        self.db_metadata = DBMetadata(self.config)

    def setUp(self):
        files = glob.glob('../resources/metadata/modis/*.json')
        for file in files:
            user_json=open(file).read()
            data = json.loads(user_json)
            merged = merge_layer_metadata('modis', data)
            mongo_id = str(self.db_metadata.insert_metadata(merged))

    def tearDown(self):
        client = MongoClient(self.config["connection"])
        client[self.config["database"]].drop_collection(self.config["document"]["layer"])

    def test_01(self):
        self.assertTrue(True)