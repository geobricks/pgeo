from flask import Blueprint
from flask import Response
from flask import jsonify
from flask.ext.cors import cross_origin
from utils import config as c
from ftplib import FTP
from error.custom_exceptions import PGeoException
import json

browse = Blueprint('browse', __name__)

@browse.route('/')
@cross_origin(origins='*')
def index():
    return 'Welcome to the Browse module!'

@browse.route('/<source_name>')
@browse.route('/<source_name>/')
@cross_origin(origins='*')
def list_products(source_name):
    try:
        config = c.Config(source_name.upper())
        if config.json['source']['type'] == 'FTP':
            ftp = FTP(config.json['source']['ftp']['base_url'])
            ftp.login()
            ftp.cwd(config.json['source']['ftp']['data_dir'])
            l = ftp.nlst()
            ftp.quit()
            return Response(json.dumps(l), content_type = 'application/json; charset=utf-8')
        else:
            m = 'Source type [' + config.json['source']['type'] + '] is not currently supported.'
            raise PGeoException(m, status_code=400)
    except Exception:
        m = 'Source [' + source_name + '] is not currently supported.'
        raise PGeoException(m, status_code=400)

# @browse.route('/list/<source_name>/<product_name>')
# @cross_origin(origins='*')
# def list_years(source_name, product_name):
#     config = c.Config(source_name.upper())
#     ftp = FTP(config.json['source']['ftp']['base_url'])
#     ftp.login()
#     ftp.cwd(config.json['source']['ftp']['data_dir'])
#     ftp.cwd(product_name)
#     l = ftp.nlst()
#     ftp.quit()
#     return Response(json.dumps(l), content_type = 'application/json; charset=utf-8')

