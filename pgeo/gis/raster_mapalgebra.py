import numpy as np
from osgeo import gdal
import time
from pgeo.utils.log import logger
from pgeo.error.custom_exceptions import PGeoException
from pgeo.utils.filesystem import create_tmp_filename
import osr

log = logger("pgeo.gis.raster_mapalgebra")


def filter_layers(raster_path1, raster_path2, min1=0, max1=None, min2=0, max2=None, band1=1, band2=1):
    print raster_path1, raster_path2

    ds1 = gdal.Open(raster_path1)
    ds2 = gdal.Open(raster_path2)
    rows1 = ds1.RasterYSize
    cols1 = ds1.RasterXSize
    rows2 = ds2.RasterYSize
    cols2 = ds2.RasterXSize

    log.info("Scatter Processing")
    if cols1 != cols2 or rows1 != rows2:
        log.error("The rasters cannot be processed because they have different dimensions")
        log.error("%sx%s %sx%s" % (rows1, cols1, rows2, cols2))
        raise PGeoException("The rasters cannot be processed because they have different dimensions", status_code=404)

    band1 = ds1.GetRasterBand(band1)
    array1 = np.array(band1.ReadAsArray()).flatten()
    #array1 = np.array(band1.ReadAsArray())

    nodata1 = band1.GetNoDataValue()

    band2 = ds2.GetRasterBand(band2)
    array2 = np.array(band2.ReadAsArray()).flatten()
    #array2 = np.array(band2.ReadAsArray())
    nodata2 = band2.GetNoDataValue()

    # merge the layers
    path = merge_layers(cols1, rows1, ds1.GetGeoTransform(), ds1.GetProjection(), array1, array2, min1, max1, min2, max2, nodata1, nodata2)   # is it useful to remove them fro the memory?
    del ds1, ds2, array1, array2
    return path


def merge_layers(rows, cols, geotransform, spatialreference, array1, array2, min1, max1, min2, max2, nodata1=None, nodata2=None):
    path = create_tmp_filename('', ".tif")

    print min1, max1, min2, max2

    # find the indexes of the arrays
    index1 = (array1 > min1) & (array1 <= max1) & (array1 != nodata1)
    index2 = (array2 > min2) & (array2 <= max2) & (array2 != nodata2)

    # merge array indexes
    compound_index = index1 & index2

    del index1, index2

    # create a new raster
    output_raster = gdal.GetDriverByName('GTiff').Create(path, rows, cols, 1, gdal.GDT_Int16)  # Open the file
    output_raster.SetGeoTransform(geotransform)
    srs = osr.SpatialReference()
    srs=osr.SpatialReference(wkt=spatialreference)
    output_raster.SetProjection(srs.ExportToWkt())
    # create raster from the compound_index of the two rasters
    # TODO: the reshape slows the operation, use matrixes
    output_raster.GetRasterBand(1).WriteArray(compound_index.reshape(cols, rows))

    return path
