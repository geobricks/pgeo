from osgeo import gdal, osr
import os
import subprocess
from pgeo.utils import log
from pgeo.utils import filesystem
from pgeo.error.custom_exceptions import PGeoException, errors

log = log.logger(__name__)

# example of statistics
stats_config = {
    "descriptive_stats": {
        "force": True
    },
    "histogram": {
        "buckets": 256,
        "include_out_of_range": 0,
        "force": True
    }
}


def crop_by_vector_database(input_file, query=None, db_connection_string=None, dstnodata='nodata'):
    """
    :param input_file: file to be cropped
    :param query: query that has to be passed to the db
    :param db_connection_string: connection string to the db
    :param dstnodata: set nodata on the nodata value
    :return: the output file path that has been processed, or None if there is any problem on the processing
    """
    output_file = filesystem.create_tmp_filename('output_', '.geotiff')
    args = [
        'gdalwarp',
        "-q",
        "-multi",
        "-of",
        "GTiff",
        "-cutline",
        db_connection_string,
        "-csql",
        query,
        "-dstnodata",
        dstnodata,
        # -crop_to_cutline is needed otherwise the layer is not cropped
        # TODO: resolve shifting problem
        "-crop_to_cutline",
        #"-dstalpha",
        input_file,
        output_file
    ]
    try:
        #TODO: handle subprocess Error (like that is not taken)
        proc = subprocess.call(args, stdout=subprocess.PIPE, stderr=None)
    except:
        stdout_value = proc.communicate()[0]
        raise PGeoException(stdout_value, 500)

    if os.path.isfile(output_file):
        return output_file
    return None


def get_statistics(input_file, config=stats_config):
    """
    :param input_file: file to be processed
    :param config: json config file to be passed
    :return: computed statistics
    """
    log.info("get_statistics: %s" % input_file)

    if config is None:
        config = stats_config

    stats = {}
    try:
        if os.path.isfile(input_file):
            ds = gdal.Open(input_file)
            if "descriptive_stats" in config:
                stats["stats"] = _get_descriptive_statistics(ds, config["descriptive_stats"])
            if "histogram" in config:
                stats["hist"] = _get_histogram(ds, config["histogram"])
        else:
            raise PGeoException(errors[522], 404)
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())
    return stats


def get_descriptive_statistics(input_file, config):
    """
    :param input_file: file to be processed
    :param config: json config file to be passed
    :return: return and array with the min, max, mean, sd statistics per band i.e. [{"band": 1, "max": 549.0, "mean": 2.8398871527778, "sd": 17.103028971129, "min": 0.0}]
    """
    try:
        if os.path.isfile(input_file):
            ds = gdal.Open(input_file)
            return _get_descriptive_statistics(ds, config)
        else:
            raise PGeoException(errors[522], 404)
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())


def get_histogram(input_file, config):
    """
    :param input_file: file to be processed
    :type string
    :param config: json config file to be passed
    :type json
    :return: return and array with the min, max, mean, sd statistics per band i.e. [{"band": 1, "buckets": 256, "values": [43256, 357, ...], "max": 998.0, "min": 0.0}]
    """
    try:
        if os.path.isfile(input_file):
            ds = gdal.Open(input_file)
            return _get_histogram(ds, config)
        else:
            raise PGeoException(errors[522], 404)
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())



def location_values(input_files, x, y, band=None):
    """
    Get the value of a (x, y) location

    # TODO:
    1) pass a json, instead of [files] pass file and id
    2) pass as well the projection used i.e. EPSG:4326
    3) for now it's used x, y as lat lon (it's not used the projection)

    :param input_files: files to be processed
    :type array
    :param x: x value (for now it's used LatLon)
    :type float
    :param y: y value (for now it's used LatLon)
    :type float
    :param band: band default=None (not yet used)
    :return: and array with the values of the (x, y) location
    """
    values = []
    for input_file in input_files:
        values.append(_location_value(input_file, x, y, band))
    return values


def _location_value(input_file, x, y, band=None):
    """
    Get the value of a (x, y) location
    :param input_file: file to be processed
    :type string
    :param x: x value
    :type float
    :param y: y value
    :type float
    :param band: band default=None (not yet used)
    :return: the value of the (x, y) location
    """
    # TODO: check with -wgs84 values instead of -geoloc that is the reference system of the image
    #cmd = "gdallocationinfo -valonly " + input_file + " -l_srs EPSG:3857 -geoloc " + str(x) + " " + str(y)
    #cmd = "gdallocationinfo -valonly " + input_file + " -geoloc " + str(x) + " " + str(y)
    cmd = "gdallocationinfo -valonly " + input_file + " -wgs84 " + str(x) + " " + str(y)

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return output.strip()


def _get_descriptive_statistics(ds, config):
    # variables
    force = True if "force" not in config else bool(config["force"])

    # stats
    stats = []
    for band in range(ds.RasterCount):
        band += 1
        srcband = ds.GetRasterBand(band)
        if srcband is None:
            continue
        # TODO: check why the "force" doesn't work on GetStatistics but the ComputeStatistics works
        if force:
            s = srcband.ComputeStatistics(0)
            #s = srcband.ComputeRasterMinMax(False)
        else:
            s = srcband.GetStatistics(False, force)
        if stats is None:
            continue
        #srcband.SetStatistics(float(s[0]), float(s[1]), float(s[2]), float(s[3]))
        stats.append({"band": band, "min": s[0], "max": s[1], "mean": s[2], "sd": s[3]})
    return stats


def _get_histogram(ds, config):
    #log.info("config %s " % config)
    # variables
    # TODO boolean of config value
    force = True if "force" not in config else bool(config["force"])
    buckets = 256 if "buckets" not in config else int(config["buckets"])
    include_out_of_range = 0 if "include_out_of_range" not in config else int(config["include_out_of_range"])

    # stats
    stats = []
    for band in range(ds.RasterCount):
        band += 1
        if force:
            (min, max) = ds.GetRasterBand(band).ComputeRasterMinMax(0)
        else:
            min = ds.GetRasterBand(band).GetMinimum()
            max = ds.GetRasterBand(band).GetMaximum()

        hist = ds.GetRasterBand(band).GetHistogram(buckets=buckets, min=min, max=max, include_out_of_range=include_out_of_range)
        stats.append({"band": band, "buckets": buckets, "min": min, "max": max, "values": hist})
    return stats


def get_authority(file_path):
    """
    @param file_path: path to the file
    @type file_path: string
    @return: AuthorityName, AuthorityCode
    """
    ds = gdal.Open( file_path )
    prj = ds.GetProjection()
    srs=osr.SpatialReference(wkt=prj)
    return srs.GetAttrValue("AUTHORITY", 0),  srs.GetAttrValue("AUTHORITY", 1)