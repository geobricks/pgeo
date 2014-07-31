import json
import os


settings = {
    # To be used by Flask: DEVELOPMENT ONLY
    "debug" : True,

    # Flask port: DEVELOPMENT ONLY
    "port" : 5005,

    # Default folder root to store layers. Each data provider configuration file specifies the path AFTER this folder.
    "target_root" : "/home/Desktop/GIS",

    # Each folder cntains one layer only. This is the default file name for such layers.
    "default_layer_name" :  "layer.geotiff",

    # Folders
    "folders" : {
        "config": "config/",
        "tmp" : "/tmp/",
        "data_providers": "data_providers/",
        "metadata": "metadata/",
        "stats": "stats/",
        "geoserver": "geoserver/"
    },

    # Databases
    "db" : {
        "metadata": {
            "connection": "mongodb://exldvsdmxreg1.ext.fao.org:27017/",
            "database": "metadata",
            "document": {
                "layer": "layer"
            }
        },

        # Spatial Database
        "spatial" : {
            # default_db will search in the dbs["database"] as default option
            "dbname": "fenix",
            "host": "localhost",
            "port": "5432",
            "username": "user",
            "password": "password",
            "schema": "spatial"
        },

        "stats" : {
            "dbname": "fenix",
            "host": "localhost",
            "port": "5432",
            "username": "fenix",
            "password": "Qwaszx",
            "schema": "stats"
        }
    },

    # Geoserver
    "geoserver" : {
        "geoserver_master": "http://168.202.28.214:9090/geoserver/rest",
        "geoserver_slaves": [],
        "username": "admin",
        "password": "geoserver",
        "default_workspace": "fenix",
        # this is used as default datasource to this is a reference to the spatial_db
        # da vedere!
        "default_db": "spatial"
    },

    # Stats
    "stats" : {
        "db": {
            "spatial_default_db": "fenix",
            "stats_default_db": "fenix"
        }
    },

    # Metadata
    "metadata" : {

    }
}


def read_config_file_json(filename, folder=''):
    dir = os.path.dirname(os.path.dirname(__file__))
    filename = filename.lower()
    path = dir + '/' + settings['folders']['config'] + settings['folders'][folder]
    return json.loads(open(path + filename).read()) if '.json' in filename else json.loads(open(path + filename + '.json').read())
