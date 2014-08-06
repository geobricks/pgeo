from pymongo import MongoClient
from bson.objectid import ObjectId


client = MongoClient('localhost', 27017)


def find_layer_by_id(layer_id):
    return client['metadata']['layer'].find({'_id': ObjectId(layer_id)})