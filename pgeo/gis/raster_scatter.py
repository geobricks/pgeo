import numpy as np
from osgeo import gdal
import time
from pysal.esda import mapclassify
from brewer2mpl import get_map as brewer2mpl_get_map
from pgeo.utils.log import logger
from pgeo.error.custom_exceptions import PGeoException, errors
from scipy.stats import linregress

log = logger("pgeo.gis.raster_scatter")

def create_scatter(raster_path1, raster_path2, bins=200, intervals=6, min1=None, max1=None, min2=None, max2=None, forced_min1=None, forced_min2=None, color='Reds', color_type='Sequential', reverse=False, band1=1, band2=1):
    log.info("Correlation Processing")

    ds1 = gdal.Open(raster_path1); rows1 = ds1.RasterYSize; cols1 = ds1.RasterXSize
    ds2 = gdal.Open(raster_path2); rows2 = ds2.RasterYSize; cols2 = ds2.RasterXSize

    if cols1 != cols2 or rows1 != rows2:
        log.error("The rasters cannot be processed because they have different dimensions")
        log.error("%sx%s %sx%s" % (rows1, cols1, rows2, cols2))
        raise PGeoException("The rasters cannot be processed because they have different dimensions", status_code=550)

    band1 = ds1.GetRasterBand(band1)
    array1 = np.array(band1.ReadAsArray()).flatten()
    nodata1 = band1.GetNoDataValue()

    band2 = ds2.GetRasterBand(band2)
    array2 = np.array(band2.ReadAsArray()).flatten()
    nodata2 = band2.GetNoDataValue()

    # min/max calulation
    # TODO: check if min and max are not passed and they have to be computed or not
    (min1_computed, max1_computed) = band1.ComputeRasterMinMax(0)
    (min2_computed, max2_computed) = band2.ComputeRasterMinMax(0)
    if min1 is None: min1 = min1_computed
    if max1 is None: max1 = max1_computed
    if min2 is None: min2 = min2_computed
    if max2 is None: max2 = max2_computed

    # this is useful? In theory should be enough the min1 and min2
    if forced_min1 is None: forced_min1 = min1
    if forced_min2 is None: forced_min2 = min2

    # Calculation of the frequencies
    statistics = compute_frequencies(array1, array2, min1, min2, max1, max2, forced_min1, forced_min2, nodata1, nodata2, bins)
    series = get_series(statistics["scatter"].values(), intervals, color, color_type, reverse)

    result = dict()
    # probably not useful for the chart itself
    # result['min1'] = min1,
    # result['max1'] = max1,
    # result['min2'] = min2,
    # result['max2'] = max2,
    result["series"] = series
    result["stats"] = statistics["stats"]

    # is it useful to remove them from the memory?
    del ds1, ds2, array1, array2
    return result


def process_data(arr1, arr2, bins=200):
    d = dict()
    try:
         # TODO: move it from here: calculation of the regression coeffient
         # TODO: add a boolean to check if it's need the computation of the coeffifcients
        slope, intercept, r_value, p_value, std_err = linregress(arr1, arr2)
        d["stats"] = {
            "slope": slope,
            "intercept": intercept,
            "r_value": r_value,
            "p_value": p_value,
            "std_err": std_err
        }

        d["scatter"] = {}
        heatmap, xedges, yedges = np.histogram2d(arr1, arr2, bins)
        for x in range(0, len(xedges)-1):
            for y in range(0, len(yedges)-1):
                if heatmap[x][y] > 0:
                    d["scatter"][str(xedges[x]) + "_" + str(yedges[y])] = {
                        "data": [xedges[x], yedges[y]],
                        "freq": heatmap[x][y]
                    }
        log.info("Correlation computation End")
        return d
    except PGeoException, e:
        log.error(e.get_message())
        raise PGeoException(e.get_message(), e.get_status_code())


def compute_frequencies(array1, array2, min1, min2, max1, max2, forced_min1=None, forced_min2=None, nodata1=None, nodata2=None, bins=200):

    index1 = (array1 > min1) & (array1 > forced_min1) & (array1 <= max1) & (array1 != nodata1)
    index2 = (array1 > min2) & (array2 > forced_min2) & (array2 <= max2) & (array2 != nodata2)

    # merge array indexes
    compound_index = index1 & index2
    del index1, index2

    # it creates two arrays from the two original arrays
    arr1 = array1[compound_index]
    arr2 = array2[compound_index]
    del array1, array2

    # processing data
    d = process_data(arr1, arr2, bins)

    # is it useful?
    del arr1, arr2
    return d


# TODO: move it
def classify_values(values, k=5, classification_type="Jenks_Caspall"):
    # TODO use a "switch" between the variuos classification types (move to a classification file python file instead of here)
    start_time = time.time()
    #result = mapclassify.quantile(values, k)

    #print values
    #start_time = time.time()
    array = np.array(values)
    result = mapclassify.Jenks_Caspall_Forced(array, k)
    log.info("Classification done in %s seconds ---" % str(time.time() - start_time))
    #return result
    return result.bins


def get_series(values, intervals, color, color_type, reverse=False):
    classification_values = []
    for v in values:
        classification_values.append(float(v['freq']))

    classes = classify_values(classification_values, intervals)
    #bmap = brewer2mpl.get_map('RdYlGn', 'Diverging', 9, reverse=True)
    bmap = brewer2mpl_get_map(color, color_type, intervals+1, reverse=reverse)
    colors = bmap.hex_colors

    # creating series
    series = []
    for color in colors:
        #print color
        series.append({
            "color": color,
            "data" : []
        })

    #classes
    for v in values:
        freq = v['freq']
        for i in range(len(classes)):
            if freq <= classes[i]:
                series[i]['data'].append([float(v['data'][0]), float(v['data'][1])])
                break
    return series