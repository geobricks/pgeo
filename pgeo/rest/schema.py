import json
import os
from flask import Blueprint
from flask import Response
from flask.ext.cors import cross_origin
from pgeo.error.custom_exceptions import PGeoException
from pgeo.error.custom_exceptions import errors
from pgeo.config.settings import read_config_file_json
from pgeo.config.settings import settings


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
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)) + '/' + settings['folders']['config'] + settings['folders']['data_providers'])
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
        config = read_config_file_json(source_name, 'data_providers')
        out = {
            'base_url': config['services_base_url'],
            'services': config['services']
        }
        return Response(json.dumps(out), content_type='application/json; charset=utf-8')
    except Exception, err:
        raise PGeoException(errors[511], status_code=511)