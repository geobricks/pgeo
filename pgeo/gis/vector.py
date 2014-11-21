import subprocess
from pgeo.utils.filesystem import create_tmp_filename, create_folder_in_tmp
from pgeo.error.custom_exceptions import PGeoException


def create_shapefiles_from_postgis_tables(datasource, tables, filenames, tmpfolder=None):
    if tmpfolder is None: tmpfolder = create_folder_in_tmp()
    print tables
    print filenames
    for table, filename in zip(tables, filenames):
        print "------------"
        print table, filename
        create_shapefile_from_postgis_table(datasource, table, filename, tmpfolder)
    return tmpfolder


def create_shapefile_from_postgis_table(datasource, table, filename, tmpfolder=None):
    if tmpfolder is None: tmpfolder = create_folder_in_tmp()
    print "///, ", filename
    filepath = create_tmp_filename(filename, ".shp", tmpfolder, False)

    print filepath
    args = [
        'pgsql2shp',
        '-f',
        filepath,
        "-h",
        datasource["host"],
        "-p",
        datasource["port"],
        "-u",
        datasource["username"],
        "-P",
        datasource["password"],
        datasource["dbname"],
        table
    ]
    print args
    try:
        #TODO: handle subprocess Error (like that is not taken)
        proc = subprocess.call(args, stdout=subprocess.PIPE, stderr=None)
        return tmpfolder
    except Exception as e:
        stdout_value = proc.communicate()[0]
        print stdout_value
        raise PGeoException(stdout_value, 500)
