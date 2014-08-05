class PGeoException(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self, message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status_code'] = self.status_code
        return rv

    def get_message(self):
        return self.message

    def get_status_code(self):
        return self.status_code


errors = {
    510:  'Error fetching available data providers.',
    511:  'Data provider is not currently supported.',
    512:  'Source type is not currently supported.',
    513:  'Error while parsing the payload of the request.',
    #geoserver
    520: "There is already a store named",
    521: "No coverage store named",
    522:  "Layer file doesn't exists"
}