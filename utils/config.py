import json
import os


class Config:

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
        self.config = json.loads(json_data)
        self.json = json.loads(json_data)

    def get(self, property):

        """
        Read a property of the JSON file stored in the config directory and set in the constructor.
        @param property: Name of the JSON key to access the property
        @return: Value corresponding to the given key
        """
        return self.config[property]