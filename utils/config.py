import json
import os


class Config:

    json=None
    filename=None
    path_to_file=None
    base_folder="../config/"

    def __init__(self, filename):
        """
        Initialize the class with the filename of a JSON stored in the config directory.
        @param filename: Name of the JSON file stored in the config lib to be read
        """
        if '.JSON' in filename.upper():
            self.filename = filename.replace('.JSON', '.json')
        else:
            self.filename = filename + '.json'
        path = os.path.join('../config/data_providers/')
        json_data = open(path + self.filename).read()
        self.json = json.loads(json_data)


    def __init__(self, filename, path_to_file=""):
        """
        Initialize the class with the filename of a JSON stored in the config directory.
        @param filename: Name of the JSON file stored in the config lib to be read
        """
        dir = os.path.dirname(os.path.dirname(__file__))
        self.filename = filename
        file_path = dir +'/config/' + path_to_file
        json_data = open(file_path + "/" + self.filename + '.json').read()
        self.json = json.loads(json_data)


    def init(self, filename, path_to_file=""):
        if '.JSON' in filename.upper():
            self.filename = filename.replace('.JSON', '.json')
        else:
            self.filename = filename + '.json'
        path = os.path.join('../config/data_providers/')
        json_data = open(path + self.filename).read()
        self.json = json.loads(json_data)


