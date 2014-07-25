from rest import app
from rest import config
from flask import jsonify
from error.custom_exceptions import PGeoException

@app.errorhandler(PGeoException)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route('/')
def root():
    return 'Welcome to p-geo!'

if __name__ == '__main__':
    app.run(port=config.PORT, debug=config.DEBUG)