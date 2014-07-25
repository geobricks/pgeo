import json
import os


class Config:

    def __init__(self, filename):

        """
        Initialize the class with the filename of a JSON stored in the config directory.
        @param filename: Name of the JSON file stored in the config lib to be read
        """

        self.filename = filename
        path = os.path.join('../config/datasources/')

        json_data = open(path + self.filename + '.json').read()
        self.config = json.loads(json_data)
        self.json = json.loads(json_data)

    def __init__(self, filename, path_to_file=""):

        """
        Initialize the class with the filename of a JSON stored in the config directory.
        @param filename: Name of the JSON file stored in the config lib to be read
        """
        dir = os.path.dirname(os.path.dirname(__file__))
        self.filename = filename
        file_path = dir + '/config/datasources/' + path_to_file
        json_data = open(file_path + "/" + self.filename + '.json').read()
        self.config = json.loads(json_data)
        self.json = json.loads(json_data)

    def get(self, property):

        """
        Read a property of the JSON file stored in the config directory and set in the constructor.
        @param property: Name of the JSON key to access the property
        @return: Value corresponding to the given key
        """
        return self.config[property]