from osgeo import gdal
import os
import subprocess
from pgeo.utils import log
from pgeo.utils import filesystem

log = log.logger(__name__)

def crop_by_vector_database(input_file, query=None, db_connection_string=None, dstnodata='nodata'):
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


def get_statistics(input_file, histogram=True, force=True):
    ds = gdal.Open(input_file)
    stats = []
    stats.append(_get_statistics(ds, force))
    if histogram:
        stats.append(_get_histogram(ds, force))
    return stats


def get_histogram( input_file, force=False, buckets=256, include_out_of_range=0 ):
    ds = gdal.Open( input_file )
    return _get_histogram(ds, force, buckets, include_out_of_range)


def _get_statistics(ds, force=True):
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


def _get_histogram( ds, force=False, buckets=256, include_out_of_range=0):
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
