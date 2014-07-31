from ftplib import FTP
import json
from flask import Blueprint
from flask import Response
from flask.ext.cors import cross_origin
from pgeo.config.settings import read_config_file_json
from pgeo.error.custom_exceptions import PGeoException
from pgeo.error.custom_exceptions import errors


browse_trmm = Blueprint('browse_trmm', __name__)
conf = read_config_file_json('trmm', 'data_providers')


@browse_trmm.route('/')
@cross_origin(origins='*')
def list_years():
    try:
        if conf['source']['type'] == 'FTP':
            ftp = FTP(conf['source']['ftp']['base_url'])
            ftp.login()
            ftp.cwd(conf['source']['ftp']['data_dir'])
            l = ftp.nlst()
            l.sort()
            out = []
            years_buffer = []
            for s in l:
                if '.' not in s:
                    try:
                        float(s)
                        year = s[:4]
                        if year not in years_buffer:
                            years_buffer.append(year)
                    except ValueError:
                        pass
            for year in years_buffer:
                out.append({'code': year, 'label': year})
            ftp.quit()
            return Response(json.dumps(out), content_type='application/json; charset=utf-8')
        else:
            raise PGeoException(errors[512], status_code=512)
    except:
        raise PGeoException(errors[511], status_code=511)


@browse_trmm.route('/<year>')
@browse_trmm.route('/<year>/')
@cross_origin(origins='*')
def list_months(year):
    try:
        if conf['source']['type'] == 'FTP':
            ftp = FTP(conf['source']['ftp']['base_url'])
            ftp.login()
            ftp.cwd(conf['source']['ftp']['data_dir'])
            l = ftp.nlst()
            l.sort()
            out = []
            months_buffer = []
            for s in l:
                if '.' not in s:
                    try:
                        float(s)
                        if s.startswith(year):
                            month = s[4:]
                            if month not in months_buffer:
                                months_buffer.append(month)
                    except ValueError:
                        pass
            for month in months_buffer:
                out.append({'code': month, 'label': month})
            ftp.quit()
            return Response(json.dumps(out), content_type='application/json; charset=utf-8')
        else:
            raise PGeoException(errors[512], status_code=512)
    except:
        raise PGeoException(errors[511], status_code=511)


@browse_trmm.route('/<year>/<month>')
@browse_trmm.route('/<year>/<month>/')
@cross_origin(origins='*')
def list_layers(year, month):
    try:
        if conf['source']['type'] == 'FTP':
            ftp = FTP(conf['source']['ftp']['base_url'])
            ftp.login()
            ftp.cwd(conf['source']['ftp']['data_dir'])
            data_dir = year + month
            ftp.cwd(year + month)
            l = ftp.nlst()
            l.sort()
            fao_layers = filter(lambda x: '00.7.1day.' in x, l)
            out = []
            for layer in fao_layers:
                try:
                    code = layer[:layer.index('.tfw')]
                    label = layer[layer.index('3B42RT.') + len('3B42RT.'):layer.index('.7')]
                    label = '3B42RT ' + label[0:4] + '-' + label[4:6] + '-' + label[6:8]
                    out.append({'code': code, 'label': label, 'extensions': ['.tif', '.tfw']})
                except:
                    pass
            ftp.quit()
            return Response(json.dumps(out), content_type='application/json; charset=utf-8')
        else:
            raise PGeoException(errors[512], status_code=512)
    except:
        raise PGeoException(errors[511], status_code=511)