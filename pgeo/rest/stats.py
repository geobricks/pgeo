import json
from flask import Blueprint
from flask.ext.cors import cross_origin
from pgeo.error.custom_exceptions import PGeoException, errors
from pgeo.utils import log
from pgeo.config.settings import settings
from pgeo.stats.raster import Stats

app = Blueprint(__name__, __name__)

log = log.logger(__name__)

# Module to process statistics
stats = Stats(settings)

# default json_statistics

raster_statistics = {
    "raster": {
        "uid": None
    },
    "stats": {
        "force": True
    }
}


raster_histogram = {
    "raster": {
        "uid": None
    },
    "stats": {
        "force": True,
        "buckets": 256
    }
}

@app.route('/')
@cross_origin(origins='*')
def index():
    """
        Welcome message
        @return: welcome message
    """
    return 'Welcome to the stats module!'


@app.route('/raster/<layer>', methods=['GET'])
@app.route('/raster/<layer>/', methods=['GET'])
@cross_origin(origins='*')
def get_stats(layer):
    """
    Extracts all the statistics of a layer
    :param layer: workspace:layername
    :return: json with the raster statistics
    """
    try:
        if ":" not in layer:
            return PGeoException("Please Specify a workspace for " + str(layer), status_code=500)

        json_stats = raster_statistics
        json_stats["raster"]["uid"] = layer
        return json.dumps(stats.get_stats(json_stats))
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())



@app.route('/raster/<layer>/hist', methods=['GET'])
@app.route('/raster/<layer>/hist/', methods=['GET'])
@cross_origin(origins='*')
def get_histogram(layer):
    """
    Extracts histogram from a layer
    :param layer: workspace:layername
    :return: json with the raster statistics
    """
    try:
        if ":" not in layer:
            return PGeoException("Please Specify a workspace for " + str(layer), status_code=500)

        json_stats = raster_histogram
        json_stats["raster"]["uid"] = layer
        return json.dumps(stats.get_histogram(json_stats))
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())


@app.route('/raster/<layer>/hist/<buckets>', methods=['GET'])
@app.route('/raster/<layer>/hist/<buckets>/', methods=['GET'])
@cross_origin(origins='*')
def get_histogram_buckets(layer, buckets):
    """
    Extracts histogram from a layer
    TODO: add a boolean and buckets
    default: boolean = True, buckets = 256
    :param layer: workspace:layername
    :return: json with the raster statistics
    """
    try:
        if ":" not in layer:
            return PGeoException("Please Specify a workspace for " + str(layer), status_code=500)

        json_stats = raster_histogram
        json_stats["raster"]["uid"] = layer
        json_stats["stats"]["buckets"] = int(buckets)
        return json.dumps(stats.get_histogram(json_stats))
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())




