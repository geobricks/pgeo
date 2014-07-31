import os.path
import psycopg2
import os.path
import subprocess
import osr
from urllib import urlencode
from urllib2 import urlopen
import json

from pgeo.db.postgresql.postgis_utils import util


"""
This is mostly a Python wrapper for the shp2pgsql command line utility.
"""
IMPORT_MODE_CREATE = "c"
IMPORT_MODE_APPEND = "a"
IMPORT_MODE_STRUCTURE = "p"
IMPORT_MODE_DATA = ""
IMPORT_MODE_SPATIAL_INDEX = ""


def import_shapefile(datasource, shapefile, table, overwrite=False, encoding='latin1'):
    _import_shapefile(datasource['host'], datasource['port'], datasource['dbname'], datasource['username'], datasource['password'], shapefile, table, overwrite, encoding)
    return True

def _import_shapefile(host, port, dbname, user, password, shapefile, table, overwrite, encoding):
    conn = psycopg2.connect("host=%s  port='%s' dbname=%s user=%s password=%s" % (host, port, dbname, user, password))
    _shape_to_postgresql(conn, shapefile, table, IMPORT_MODE_CREATE + IMPORT_MODE_DATA + IMPORT_MODE_SPATIAL_INDEX, encoding)
    _vacuum_analyze(conn, table)


#TODO: how to handle the encoding?
def _shape_to_postgresql(conn, shape_path, table, mode, encoding='latin1', srid="4326", log_file=None, batch_size=1000):

    dbf_file = shape_path[0:-4] + '.dbf'
    prj_file = shape_path[0:-4] + '.prj'

    #Try detecting the SRID, by default we set to 4326 and hope the best
    srid = get_prj_srid(prj_file)

    args = [
        'shp2pgsql',  #TODO: pass the command dynamically in the config file of the server
        "-%s" % mode,
        "-W", encoding,
        "-s", srid,
        shape_path,
        table]
    print args
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=log_file)

    cursor = conn.cursor()
    try:
        with p.stdout as stdout:
            for commands in util.groupsgen(util.read_until(stdout, ';'), batch_size):
                command = ''.join(commands).strip()
                if len(command) > 0:
                    cursor.execute(command)
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        cursor.close()


# TODO: enable it to recognize Mercator used by ESRI (3857)
def get_prj_srid(prj_file, srid="4326"):
    """
    if it doesn't find the SRID uses 4326 as default one
    :param prj_file:
    :param srid:
    :return:
    """
    if os.path.isfile(prj_file):
        prj_filef = open(prj_file, 'r')
        prj_txt = prj_filef.read()
        prj_filef.close()
        srs = osr.SpatialReference()
        srs.ImportFromESRI([prj_txt])
        srs.AutoIdentifyEPSG()
        # this is used to check if the prj is 'WGS_1984_Web_Mercator_Auxiliary_Sphere' (the one used by ESRI)
        mercator_ESRI = _check_if_esri_mercator(srs.GetAttrValue('PROJCS'))
        if ( mercator_ESRI != None ):
            return mercator_ESRI
        else:
            code = srs.GetAuthorityCode(None)
            if code:
                srid = code
            else:
                #Ok, no luck, lets try with the OpenGeo service
                check_srid = _check_prj_from_webservice(prj_txt)
                if check_srid != None:
                    srid = check_srid
                '''
                query = urlencode({
                    'exact' : True,
                    'error' : True,
                    'mode' : 'wkt',
                    'terms' : prj_txt})
                print query
                webres = urlopen('http://prj2epsg.org/search.json', query)
                jres = json.loads(webres.read())
                print jres
                if jres['codes']:
                    srid = int(jres['codes'][0]['code'])  '''
    else:
        print "TODO: .prj doesn't exist try to get from the shp? or send error"
    print srid
    return srid


# TODO: this is a quick fix for ArcGIS projection error
def _check_if_esri_mercator(projcs):
    print projcs
    if projcs == 'WGS_1984_Web_Mercator_Auxiliary_Sphere':
        return 3857
    return None

def _check_prj_from_webservice(prj_txt):
    query = urlencode({
        'exact' : True,
        'error' : True,
        'mode' : 'wkt',
        'terms' : prj_txt})
    webres = urlopen('http://prj2epsg.org/search.json', query)
    jres = json.loads(webres.read())
    print jres
    if jres['codes']:
        return int(jres['codes'][0]['code']) #srid
    return None


def _vacuum_analyze(conn, table):
    isolation_level = conn.isolation_level
    conn.set_isolation_level(0)
    cursor = conn.cursor()
    try:
        cursor.execute('vacuum analyze %s;' % table)
    finally:
        cursor.close()
        conn.set_isolation_level(isolation_level)





