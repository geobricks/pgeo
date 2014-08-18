from ftplib import FTP
from pgeo.config.settings import read_config_file_json
from pgeo.error.custom_exceptions import PGeoException
from pgeo.error.custom_exceptions import errors


conf = read_config_file_json('modis', 'data_providers')


def list_products():
    """
    List all the available MODIS products.
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
            for s in l:
                out.append({'code': s, 'label': s})
            ftp.quit()
            return out
        else:
            raise PGeoException(errors[512], status_code=512)
    except:
        raise PGeoException(errors[511], status_code=511)


def list_years(product_name):
    """
    List all the available years for a given MODIS product.
    @param product_name: Code of MODIS product, e.g. 'MOD13Q1'
    @return: An array of code/label objects.
    """
    try:
        if conf['source']['type'] == 'FTP':
            ftp = FTP(conf['source']['ftp']['base_url'])
            ftp.login()
            ftp.cwd(conf['source']['ftp']['data_dir'])
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
            return out
        else:
            raise PGeoException(errors[512], status_code=512)
    except:
        raise PGeoException(errors[511], status_code=511)


def list_days(product_name, year):
    """
    List all the available days for a given MODIS product and year.
    @param product_name: Code of MODIS product, e.g. 'MOD13Q1'
    @param year: e.g. '2010'
    @return: An array of code/label objects.
    """
    try:
        if conf['source']['type'] == 'FTP':
            ftp = FTP(conf['source']['ftp']['base_url'])
            ftp.login()
            ftp.cwd(conf['source']['ftp']['data_dir'])
            ftp.cwd(product_name.upper())
            ftp.cwd(year)
            l = ftp.nlst()
            l.sort()
            out = []
            for s in l:
                out.append({'code': s, 'label': s})
            ftp.quit()
            return out
        else:
            raise PGeoException(errors[512], status_code=512)
    except:
        raise PGeoException(errors[511], status_code=511)


def list_layers(product_name, year, day):
    """
    List all the available layers for a given MODIS product, year and day.
    @param product_name: Code of MODIS product, e.g. 'MOD13Q1'
    @param year: e.g. '2010'
    @param day: Day of the year, three digits, e.g. '017'
    @return: An array of code/label/size objects.
    """
    try:
        if conf['source']['type'] == 'FTP':
            ftp = FTP(conf['source']['ftp']['base_url'])
            ftp.login()
            ftp.cwd(conf['source']['ftp']['data_dir'])
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
            return out
        else:
            raise PGeoException(errors[512], status_code=512)
    except:
        raise PGeoException(errors[511], status_code=511)