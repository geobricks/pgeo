from flask import Blueprint
from flask import Response
from flask.ext.cors import cross_origin
from utils import config as c
from ftplib import FTP
from error.custom_exceptions import PGeoException
from error.custom_exceptions import errors
import json

browse_modis = Blueprint('browse_modis', __name__)
config = c.Config('MODIS')


@browse_modis.route('/')
@cross_origin(origins='*')
def list_products():
    try:
        if config.json['source']['type'] == 'FTP':
            ftp = FTP(config.json['source']['ftp']['base_url'])
            ftp.login()
            ftp.cwd(config.json['source']['ftp']['data_dir'])
            l = ftp.nlst()
            l.sort()
            out = []
            for s in l:
                out.append({'code': s, 'label': s})
            ftp.quit()
            return Response(json.dumps(out), content_type='application/json; charset=utf-8')
        else:
            raise PGeoException(errors[512], status_code=512)
    except:
        raise PGeoException(errors[511], status_code=511)


@browse_modis.route('/<product_name>')
@browse_modis.route('/<product_name>/')
@cross_origin(origins='*')
def list_years(product_name):
    try:
        if config.json['source']['type'] == 'FTP':
            ftp = FTP(config.json['source']['ftp']['base_url'])
            ftp.login()
            ftp.cwd(config.json['source']['ftp']['data_dir'])
            ftp.cwd(product_name.upper())
            l = ftp.nlst()
            l.sort(reverse=True)
            out = []
            for s in l:
                try:
                    float(s)
                    out.append({'code': s, 'label': s})
                except ValueError:
                    pass
            ftp.quit()
            return Response(json.dumps(out), content_type='application/json; charset=utf-8')
        else:
            raise PGeoException(errors[512], status_code=512)
    except:
        raise PGeoException(errors[511], status_code=511)


@browse_modis.route('/<product_name>/<year>')
@browse_modis.route('/<product_name>/<year>/')
@cross_origin(origins='*')
def list_days(product_name, year):
    try:
        if config.json['source']['type'] == 'FTP':
            ftp = FTP(config.json['source']['ftp']['base_url'])
            ftp.login()
            ftp.cwd(config.json['source']['ftp']['data_dir'])
            ftp.cwd(product_name.upper())
            ftp.cwd(year)
            l = ftp.nlst()
            l.sort()
            out = []
            for s in l:
                out.append({'code': s, 'label': s})
            ftp.quit()
            return Response(json.dumps(out), content_type='application/json; charset=utf-8')
        else:
            raise PGeoException(errors[512], status_code=512)
    except:
        raise PGeoException(errors[511], status_code=511)


@browse_modis.route('/<product_name>/<year>/<day>')
@browse_modis.route('/<product_name>/<year>/<day>/')
@cross_origin(origins='*')
def list_layers(product_name, year, day):
    try:
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
                    h = code[2 + code.index('.h'):4 + code.index('.h')]
                    v = code[1 + code.index('v'):3 + code.index('v')]
                    label = 'H ' + h + ', V ' + v + ' (' + str(round((float(size) / 1000000), 2)) + ' MB)'
                    out.append({'code': code, 'label': label, 'size': size})
                except:
                    pass
            return Response(json.dumps(out), content_type='application/json; charset=utf-8')
        else:
            raise PGeoException(errors[512], status_code=512)
    except:
        raise PGeoException(errors[511], status_code=511)