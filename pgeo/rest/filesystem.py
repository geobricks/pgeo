import json
from flask import Blueprint
from flask import Response
from flask.ext.cors import cross_origin
from pgeo.error.custom_exceptions import PGeoException
from pgeo.utils.filesystem import create_filesystem


filesystem = Blueprint('filesystem', __name__)


@filesystem.route('/')
@cross_origin(origins='*')
def index():
    """
        Welcome message
        @return: welcome message
    """
    return 'Welcome to the Filesystem module!'


@filesystem.route('/<source>')
@filesystem.route('/<source>/')
@cross_origin(origins='*')
def create_filesystem_service(source):
    """
        This service create the filesystem structure as specified in the configuration file.
        @param source: e.g. 'modis'
        @return: Result of the operation
    """
    try:
        create_filesystem(source, {'product': 'Simone', 'year': '2014', 'day': '1'})
        response = {'status_code': 200, 'status_message': 'OK'}
        return Response(json.dumps(response), content_type='application/json; charset=utf-8')
    except:
        raise PGeoException('Error', status_code=500)