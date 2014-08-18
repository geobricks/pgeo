from ftplib import FTP
from pgeo.config.settings import read_config_file_json
from pgeo.error.custom_exceptions import PGeoException
from pgeo.error.custom_exceptions import errors


conf = read_config_file_json('trmm', 'data_providers')


def list_years():
    """
    List all the available years.
    @return: An array of code/label objects.
    """
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
            return out
        else:
            raise PGeoException(errors[512], status_code=512)
    except:
        raise PGeoException(errors[511], status_code=511)


def list_months(year):
    """
    List all the available months for the given year.
    @param year: e.g. '2010'
    @return: An array of code/label objects.
    """
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
            return out
        else:
            raise PGeoException(errors[512], status_code=512)
    except:
        raise PGeoException(errors[511], status_code=511)


def list_layers(year, month):
    """
    List all the available layers for a given year and month.
    @param year: e.g. '2010'
    @param month: e.g. '02'
    @return: An array of code/label/extensions objects.
    """
    try:
        if conf['source']['type'] == 'FTP':
            ftp = FTP(conf['source']['ftp']['base_url'])
            ftp.login()
            ftp.cwd(conf['source']['ftp']['data_dir'])
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
            return out
        else:
            raise PGeoException(errors[512], status_code=512)
    except:
        raise PGeoException(errors[511], status_code=511)