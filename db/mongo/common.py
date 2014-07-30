import sys
from bson import json_util

try:
    from utils import log, config
except Exception, e:
    sys.path.append('../')
    from utils import log, config

"""
Insert json data to the mongo db
@param client client used to connect to mongo
@param database
@param collection
@param data json to be inserted
@return: id
"""
def insert(client, database, collection, data):
    try:
        id =  client[database][collection].insert(data)
        return id
    except Exception, e:
        print "Insert ERROR ", e
        return None


"""
DElete json data to the mongo db
@param client client used to connect to mongo
@param database
@param collection
@param data json to be inserted
@return: id
"""
def remove(client, database, collection, data):
    try:
        id =  client[database][collection].remove(data)
        return id
    except Exception, e:
        print "Delete ERROR ", e
        return None


"""
Query mongo
@param client client used to connect to mongo
@param database
@param collection
@param query: default query will return the entire collection
@return: id
"""
def find(client, database, collection, query=None):
    if ( query != None ): cursor = client[database][collection].find(query)
    else: cursor = client[database][collection].find()
    return json_util.dumps(cursor)


'''

aggregation query builder

'''


"""
Query mongo query_builder_groupby rule
@param fields: fields to return in the select (i.e ['vendorcode', 'vendorname', 'varietycode'])
@param rule: aggregation rule if needed (i.e. avg, sum) TODO: make it optional
@param rule_field: filed to apply the rule TODO: make it optional
@return: json with groupby rule
"""
def query_builder_groupby(fields, rule, rule_field):
    fs = {}
    for  f in fields:
        fs[f] = '$' + f
    return { '$group' : { '_id': fs, rule_field : { '$'+ rule +'' : '$'+rule_field+'' } } }

