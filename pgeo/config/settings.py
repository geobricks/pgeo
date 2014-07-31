import json
import os
import logging

settings = {

    # To be used by Flask: DEVELOPMENT ONLY
    "debug": True,

    # Flask port: DEVELOPMENT ONLY
    "port": 5005,

    # Default folder root to store layers. Each data provider configuration file specifies the path AFTER this folder.
    "target_root": "/home/Desktop/GIS",

    # Each folder cntains one layer only. This is the default file name for such layers.
    "default_layer_name":  "layer.geotiff",

    # Logging configurations
    "logging": {
        "level": logging.INFO,
        "format": "%(asctime)s | %(levelname)-8s | %(name)-20s | Line: %(lineno)-5d | %(message)s",
        "datefmt": "%d-%m-%Y | %H:%M:%s"
    },

    # Folders
    "folders": {
        "config": "config/",
        "tmp": "/tmp/",
        "data_providers": "data_providers/",
        "metadata": "metadata/",
        "stats": "stats/",
        "geoserver": "geoserver/",

        # used on runtime statistics (for Published layers this is the Geoservers Cluster "datadir")
        "geoserver_datadir": "/home/vortex/Desktop/LAYERS/TRMM",
    },

    # Databases
    "db": {
        "metadata": {
            "connection": "mongodb://exldvsdmxreg1.ext.fao.org:27017/",
            "database": "metadata",
            "document": {
                "layer": "layer"
            }
        },

        # Spatial Database
        "spatial": {
            # default_db will search in the dbs["database"] as default option
            "dbname": "fenix",
            "host": "localhost",
            "port": "5432",
            "username": "fenix",
            "password": "Qwaszx",
            "schema": "spatial"
        },

        "stats": {
            "dbname": "fenix",
            "host": "localhost",
            "port": "5432",
            "username": "fenix",
            "password": "Qwaszx",
            "schema": "stats"
        }
    },

    # Geoserver
    "geoserver": {
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
    "stats": {
        "db": {
            "spatial": "spatial",
            "stats": "stats"
        }
    },


    # Metadata
    "metadata": {

    }

}


def read_config_file_json(filename, folder=''):
    directory = os.path.dirname(os.path.dirname(__file__))
    filename = filename.lower()
    path = directory + '/' + settings['folders']['config'] + settings['folders'][folder]
    extension = '' if '.json' in filename else '.json'
    return json.loads(open(path + filename + extension).read())