from flask import Blueprint
from flask import Response
from flask import jsonify
from flask.ext.cors import cross_origin
from utils import config as c
from ftplib import FTP
from error.custom_exceptions import PGeoException
import json

schema = Blueprint('schema', __name__)

@schema.route('/')
@cross_origin(origins='*')
def index():
    return 'Welcome to the Schema module!'

@schema.route('/<source_name>')
@schema.route('/<source_name>/')
@cross_origin(origins='*')
def list_products(source_name):
    try:
        config = c.Config(source_name.upper())
        out = {
            'base_url': config.json['services_base_url'],
            'services': config.json['services']
        }
        return Response(json.dumps(out), content_type = 'application/json; charset=utf-8')
    except Exception, err:
        m = 'Source [' + source_name + '] is not currently supported.'
        raise PGeoException(m, status_code=400)

