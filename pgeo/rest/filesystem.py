from ftplib import FTP
import json
import os
from flask import Blueprint
from flask import Response
from flask.ext.cors import cross_origin
from pgeo.config.settings import read_config_file_json
from pgeo.error.custom_exceptions import PGeoException
from pgeo.error.custom_exceptions import errors
from pgeo.utils.filesystem import create_filesystem


filesystem = Blueprint('filesystem', __name__)


@filesystem.route('/')
@cross_origin(origins='*')
def index():
    return 'Welcome to the Filesystem module!'


@filesystem.route('/<source>')
@filesystem.route('/<source>/')
@cross_origin(origins='*')
def create_filesystem_service(source):
    conf = read_config_file_json(source, 'data_providers')['target']
    create_filesystem(source, {'product': 'PRODOTTO', 'year': 'ANNO', 'day': 'GIORNO'})
    return Response(json.dumps(conf), content_type='application/json; charset=utf-8')