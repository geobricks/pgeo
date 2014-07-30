import json
import os

# To be used by Flask: DEVELOPMENT ONLY
debug = True

# Flask port: DEVELOPMENT ONLY
port = 5005

# Default folder root to store layers. Each data provider configuration file specifies the path AFTER this folder.
target_root = '/home/Desktop/GIS'

# Each folder cntains one layer only. This is the default file name for such layers.
default_layer_name = 'layer.geotiff'

# Folders
folders = {
    'config': 'config/',
    'tmp' : '/tmp/',
    'data_providers': 'data_providers/',
    'metadata': 'metadata/'
}


def read_config_file_json(filename, folder=""):
    dir = os.path.dirname(os.path.dirname(__file__))
    filename = filename.lower()
    path = dir + "/" + folders['config'] + folders[folder]
    return json.loads(open(path + filename + '.json').read())
