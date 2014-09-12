from ftplib import FTP
from pgeo.config.settings import read_config_file_json
from pgeo.error.custom_exceptions import PGeoException
from pgeo.error.custom_exceptions import errors
from pgeo.utils.date import day_of_the_year_to_date
from bs4 import BeautifulSoup
import urllib


conf = read_config_file_json('modis', 'data_providers')


def get_modis_product_table():

    sock = urllib.urlopen('https://lpdaac.usgs.gov/products/modis_products_table')
    html = sock.read()
    sock.close()
    soup = BeautifulSoup(html)

    tables = soup.findAll('table')
    table = tables[len(tables) - 1]
    tbody = table.find('tbody')
    trs = tbody.findAll('tr')

    products = []
    keys = ['code', 'platform', 'modis_data_product', 'raster_type', 'spatial_resolution', 'temporal_resolution']

    for tr in trs:
        p = {}
        counter = 0
        tds = tr.findAll('td')
        for td in tds:
            text = ''.join(td.find(text=True)).strip().replace('\n', '')
            if counter == 0:
                text = td.find('a').find(text=True)
            p[keys[counter]] = text
            counter += 1
        products.append(p)

    return products


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
                date = day_of_the_year_to_date(s, year).strftime('%d %B')
                out.append({'code': s, 'label': date})
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
            buffer = []
            for line in ls:
                try:
                    start = line.index('Size=')
                    end = line.index(';', start)
                    size = line[start + len('Size='):end]
                    start = line.index(product_name.upper())
                    file_name = line[start:]
                    if file_name not in buffer:
                        buffer.append(file_name)
                        file_path = 'ftp://' + conf['source']['ftp']['base_url'] + conf['source']['ftp']['data_dir']
                        file_path += product_name.upper() + '/' + year + '/' + day + '/'
                        file_path += line[start:]
                        h = file_name[2 + file_name.index('.h'):4 + file_name.index('.h')]
                        v = file_name[1 + file_name.index('v'):3 + file_name.index('v')]
                        label = 'H ' + h + ', V ' + v + ' (' + str(round((float(size) / 1000000), 2)) + ' MB)'
                        out.append({
                            'file_name': file_name,
                            'file_path': file_path,
                            'label': label,
                            'size': size
                        })
                except:
                    pass
            return out
        else:
            raise PGeoException(errors[512], status_code=512)
    except:
        raise PGeoException(errors[511], status_code=511)


def list_layers_subset(product_name, year, day, from_h, to_h, from_v, to_v):
    """
    List all the available layers for a given MODIS product, year and day.
    @param product_name: Code of MODIS product, e.g. 'MOD13Q1'
    @param year: e.g. '2010'
    @param day: Day of the year, three digits, e.g. '017'
    @param from_h: e.g. '05'
    @param to_h: e.g. '05'
    @param from_v: e.g. '05'
    @param to_v: e.g. '05'
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
            buffer = []
            for line in ls:
                try:
                    start = line.index('Size=')
                    end = line.index(';', start)
                    size = line[start + len('Size='):end]
                    start = line.index(product_name.upper())
                    file_name = line[start:]
                    if file_name not in buffer:
                        buffer.append(file_name)
                        if is_layer_in_the_range(file_name, from_h, to_h, from_v, to_v):
                            file_path = 'ftp://' + conf['source']['ftp']['base_url'] + conf['source']['ftp']['data_dir']
                            file_path += product_name.upper() + '/' + year + '/' + day + '/'
                            file_path += line[start:]
                            h = file_name[2 + file_name.index('.h'):4 + file_name.index('.h')]
                            v = file_name[1 + file_name.index('v'):3 + file_name.index('v')]
                            label = 'H ' + h + ', V ' + v + ' (' + str(round((float(size) / 1000000), 2)) + ' MB)'
                            out.append({
                                'file_name': file_name,
                                'file_path': file_path,
                                'label': label,
                                'size': size
                            })
                except:
                    pass
            return out
        else:
            raise PGeoException(errors[512], status_code=512)
    except Exception, e:
        raise PGeoException(str(e), status_code=500)


def is_layer_in_the_range(file_name, from_h, to_h, from_v, to_v):
    h_idx = len('.h') + file_name.index('.h')
    h = int(file_name[h_idx:(2 + h_idx)])
    v_idx = len(str(h) + 'v') + file_name.index(str(h) + 'v')
    v = int(file_name[v_idx:(2 + v_idx)])
    if int(from_h) <= h <= int(to_h) and int(from_v) <= v <= int(to_v):
        return True
    return False


def list_countries():
    try:
        countries = read_config_file_json('__gaul2modis', 'data_providers')
        return countries
    except:
        raise PGeoException(errors[511], status_code=511)


def list_layers_countries_subset(product_name, year, day, countries):
    """
    List all the available layers for a given MODIS product, year and day.
    @param product_name: Code of MODIS product, e.g. 'MOD13Q1'
    @param year: e.g. '2010'
    @param day: Day of the year, three digits, e.g. '017'
    @param countries: GAUL codes, comma separated e.g. '18,25,34'
    @type countries: String, comma separated
    @return: An array of code/label/size objects.
    """
    countries_list = countries.split(',')
    out = []
    clean_out = []
    file_names_buffer = []
    try:
        gaul_2_modis = read_config_file_json('__gaul2modis', 'data_providers')
        for g2m in gaul_2_modis:
            if g2m['gaul_code'] in countries_list:
                from_h = g2m['from_h']
                to_h = g2m['to_h']
                from_v = g2m['from_v']
                to_v = g2m['to_v']
                tmp = list_layers_subset(product_name, year, day, from_h, to_h, from_v, to_v)
                out += tmp
        for tmp in out:
            if tmp['file_name'] not in file_names_buffer:
                file_names_buffer.append(tmp['file_name'])
                clean_out.append(tmp)
        return clean_out
    except Exception, e:
        raise PGeoException(e.get_message(), e.get_status_code())