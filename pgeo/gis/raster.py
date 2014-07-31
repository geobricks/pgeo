from osgeo import gdal
import os
import subprocess
from pgeo.utils import log
from pgeo.utils import filesystem

log = log.logger(__name__)

# example of statistics
stats_config = {
    "descriptive_statistics": {
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
    output_file =  filesystem.create_tmp_filename('output_', '.geotiff')
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
        "-crop_to_cutline",
        input_file,
        output_file
    ]
    try:
        #TODO: handle subprocess Error (like that is not taken)
        proc = subprocess.call(args, stdout=subprocess.PIPE, stderr=None)
    except:
        stdout_value = proc.communicate()[0]
        log.error(stdout_value)
    if os.path.isfile(output_file):
        return output_file
    return None


def get_statistics(input_file, config=stats_config):
    """
    :param input_file: file to be processed
    :param config: json config file to be passed
    :return: computed statistics
    """

    # datasource
    ds = gdal.Open(input_file)

    stats = []
    if "descriptive_statistics" in config:
        stats.append(_get_statistics(ds, config["descriptive_statistics"]))
    if "histogram" in config:
        stats.append(_get_histogram(ds, config["histogram"]))
    return stats


def get_histogram( input_file, config ):
    ds = gdal.Open( input_file )
    return _get_histogram(ds, config)


def _get_statistics(ds, config):
    # variables
    force = True if "force" not in config else config["force"]

    # stats
    stats = []
    for band in range(ds.RasterCount):
        band += 1
        srcband = ds.GetRasterBand(band)
        if srcband is None:
            continue
        '''if force:
            s = srcband.ComputeStatistics(0)
        else:
            s = srcband.GetStatistics(False, force)
        '''
        s = srcband.GetStatistics(False, force)
        if stats is None:
            continue
        stats.append({"stats": {"min": s[0], "max": s[1], "mean": s[2], "sd": s[3]}})
    return stats


def _get_histogram(ds, config):
    # variables
    force = True if "force" not in config else config["force"]
    buckets = 256 if "buckets" not in config else config["buckets"]
    include_out_of_range = 0  if "include_out_of_range" not in config else config["include_out_of_range"]

    # stats
    stats = []
    for band in range(ds.RasterCount):
        band += 1
        if (force == True ):
            (min, max)= ds.GetRasterBand(band).ComputeRasterMinMax(0)
        else:
            min = ds.GetRasterBand(band).GetMinimum()
            max = ds.GetRasterBand(band).GetMaximum()

        hist = ds.GetRasterBand(band).GetHistogram( buckets=buckets, min=min, max=max, include_out_of_range = include_out_of_range )
        stats.append({"hist": {"buckets": buckets, "min": min, "max": max, "values": hist}})
    return stats
