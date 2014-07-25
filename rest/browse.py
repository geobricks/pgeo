from flask import Blueprint
from flask import Response
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
            out = []
            for s in l:
                out.append({'code': s, 'label': s})
            ftp.quit()
            return Response(json.dumps(out), content_type='application/json; charset=utf-8')
        else:
            m = 'Source type [' + config.json['source']['type'] + '] is not currently supported.'
            raise PGeoException(m, status_code=400)
    except:
        m = 'Source [' + source_name + '] is not currently supported.'
        raise PGeoException(m, status_code=400)


@browse.route('/<source_name>/<product_name>')
@browse.route('/<source_name>/<product_name>/')
@cross_origin(origins='*')
def list_years(source_name, product_name):
    try:
        config = c.Config(source_name.upper())
        if config.json['source']['type'] == 'FTP':
            ftp = FTP(config.json['source']['ftp']['base_url'])
            ftp.login()
            ftp.cwd(config.json['source']['ftp']['data_dir'])
            ftp.cwd(product_name.upper())
            l = ftp.nlst()
            out = []
            for s in l:
                out.append({'code': s, 'label': s})
            ftp.quit()
            return Response(json.dumps(out), content_type='application/json; charset=utf-8')
        else:
            m = 'Source type [' + config.json['source']['type'] + '] is not currently supported.'
            raise PGeoException(m, status_code=400)
    except:
        m = 'Source [' + source_name + '] is not currently supported.'
        raise PGeoException(m, status_code=400)


@browse.route('/<source_name>/<product_name>/<year>')
@browse.route('/<source_name>/<product_name>/<year>/')
@cross_origin(origins='*')
def list_days(source_name, product_name, year):
    try:
        config = c.Config(source_name.upper())
        if config.json['source']['type'] == 'FTP':
            ftp = FTP(config.json['source']['ftp']['base_url'])
            ftp.login()
            ftp.cwd(config.json['source']['ftp']['data_dir'])
            ftp.cwd(product_name.upper())
            ftp.cwd(year)
            l = ftp.nlst()
            out = []
            for s in l:
                out.append({'code': s, 'label': s})
            ftp.quit()
            return Response(json.dumps(out), content_type='application/json; charset=utf-8')
        else:
            m = 'Source type [' + config.json['source']['type'] + '] is not currently supported.'
            raise PGeoException(m, status_code=400)
    except:
        m = 'Source [' + source_name + '] is not currently supported.'
        raise PGeoException(m, status_code=400)


@browse.route('/<source_name>/<product_name>/<year>/<day>')
@browse.route('/<source_name>/<product_name>/<year>/<day>/')
@cross_origin(origins='*')
def list_layers(source_name, product_name, year, day):
    try:
        config = c.Config(source_name.upper())
        if config.json['source']['type'] == 'FTP':
            ftp = FTP(config.json['source']['ftp']['base_url'])
            ftp.login()
            ftp.cwd(config.json['source']['ftp']['data_dir'])
            ftp.cwd(product_name.upper())
            ftp.cwd(year)
            ftp.cwd(day)
            ls = []
            ftp.retrlines('MLSD', ls.append)
            ftp.quit()
            out = []
            for line in ls:
                try:
                    start = line.index('Size=')
                    end = line.index(';', start)
                    size = line[start + len('Size='):end]
                    start = line.index(product_name.upper())
                    code = line[start:]
                    out.append({'code': code, 'label': code, 'size': size})
                except:
                    pass
            return Response(json.dumps(out), content_type='application/json; charset=utf-8')
        else:
            m = 'Source type [' + config.json['source']['type'] + '] is not currently supported.'
            raise PGeoException(m, status_code=400)
    except:
        m = 'Source [' + source_name + '] is not currently supported.'
        raise PGeoException(m, status_code=400)