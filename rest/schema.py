from flask import Blueprint
from flask import Response
from flask.ext.cors import cross_origin
from utils import config as c
from error.custom_exceptions import PGeoException
from error.custom_exceptions import errors
import json
import os

schema = Blueprint('schema', __name__)


@schema.route('/')
@cross_origin(origins='*')
def index():
    return 'Welcome to the Schema module!'


@schema.route('/sources', methods=['GET'])
@schema.route('/sources/', methods=['GET'])
@cross_origin(origins='*')
def list_sources():
    try:
        path = os.path.join('../config/data_providers/')
        out = []
        files = os.listdir(path)
        files.sort()
        for filename in files:
            out.append({'code': filename, 'label': filename[:filename.index('.json')]})
        return Response(json.dumps(out), content_type='application/json; charset=utf-8')
    except Exception, err:
        print err
        raise PGeoException(errors[510], status_code=510)


@schema.route('/sources/<source_name>', methods=['GET'])
@schema.route('/sources/<source_name>/', methods=['GET'])
@cross_origin(origins='*')
def list_services(source_name):
    try:
        config = c.Config(source_name.upper())
        out = {
            'base_url': config.json['services_base_url'],
            'services': config.json['services']
        }
        return Response(json.dumps(out), content_type='application/json; charset=utf-8')
    except Exception, err:
        raise PGeoException(errors[511], status_code=511)