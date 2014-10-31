import numpy as np
from osgeo import gdal
from pgeo.gis.raster import get_nodata_value
import time
from pylab import hexbin,show
from scipy.ndimage import measurements
from scipy.stats import itemfreq
import rasterio
from pysal.esda import mapclassify
import brewer2mpl
from threading import Thread
# import Queue
from pgeo.utils.log import logger
from pgeo.error.custom_exceptions import PGeoException
from scipy.optimize import curve_fit
from itertools import izip
from multiprocessing import Process, Manager, Lock, Queue, Pool
import multiprocessing
import threading
from scipy.stats import linregress
from os import kill

log = logger("pgeo.gis.raster_scatter")


# print "here"
# cal= mapclassify.load_example()
# print cal
# ei=mapclassify.Equal_Interval(cal,k=5)
# print ei


def create_scatter(raster_path1, raster_path2, band1=1, band2=1, buckets=200, intervals=6,  workers=3, forced_min1=0, forced_min2=0, color='Reds', color_type='Sequential', reverse=False):

    log.info(workers)
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

    # min/max calulation
    (min1, max1) = band1.ComputeRasterMinMax(0)
    step1 = (max1 - min1) / buckets
    (min2, max2) = band2.ComputeRasterMinMax(0)
    step2 = (max2 - min2) / buckets

    # Calculation of the frequencies
    #freqs = couples_with_freq(array1, array2, step1, step2, min1, min2, max1, max2, forced_min1, forced_min2, nodata1, nodata2)
    #freqs = couples_with_freq_split(array1, array2, step1, step2, min1, min2, max1, max2, forced_min1, forced_min2, nodata1, nodata2)
    statistics = couples_with_freq_multiprocess(array1, array2, step1, step2, min1, min2, max1, max2, forced_min1, forced_min2, nodata1, nodata2, workers)
    #print len(freqs)
    series = get_series(statistics["scatter"].values(), intervals, color, color_type, reverse)

    #print series
    result = dict()
    # probably not useful for the chart itself
    # result['min1'] = min1,
    # result['min2'] = min2,
    # result['max2'] = max2,
    # result['step1'] = step1,
    # result['step2'] = step2
    result["series"] = series
    result["stats"] = statistics["stats"]

    # is it useful to remove them fro the memory?
    del ds1
    del ds2
    del array1
    del array2
    return result

# def worker(arr1, arr2, step1, step2, out_q):
#         d = dict()
#         for item_a, item_b in izip(arr1, arr2):
#             value1 = round(item_a / step1, 0)
#             value2 = round(item_b / step2, 0)
#             # print step1, step2
#             # print value1, value2
#             # key = str(value1) + "_" + str(value2)
#             # print key
#             # print item_a, item_b
#             #
#             #break
#             key = str(value1) + "_" + str(value2)
#             try:
#                 d[key]["freq"] += 1
#             except:
#                 d[key] = {
#                     "data": [item_a, item_b],
#                     "freq": 1
#                 }
#         print "worker end"
#         out_q.put(d)
#         out_q.close()


def worker(arr1, arr2, step1, step2, out_q):
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
        heatmap, xedges, yedges = np.histogram2d(arr1, arr2, bins=200)
        for x in range(0, len(xedges)-1):
            for y in range(0, len(yedges)-1):
                if heatmap[x][y] > 0:
                    d["scatter"][str(xedges[x]) + "_" + str(yedges[y])] = {
                        "data": [xedges[x], yedges[y]],
                        "freq": heatmap[x][y]
                    }

        log.info("worker end")
        out_q.put(d)
        out_q.close()
    except PGeoException, e:
        log.error(e.get_message())
        raise PGeoException(e.get_message(), e.get_status_code())


def couples_with_freq_multiprocess(array1, array2, step1, step2, min1, min2, max1, max2, forced_min1, forced_min2, nodata1=None, nodata2=None, workers=3, rounding=0):
    print "couples_with_freq_multiprocess"
    start_time = time.time()

    index1 = (array1 > forced_min1) & (array1 <= max1) & (array1 != nodata1)
    index2 = (array2 > forced_min2) & (array2 <= max2) & (array2 != nodata2)

    # merge array indexes
    compound_index = index1 & index2

    del index1
    del index2

    # it creates two arrays from the two original arrays
    arr1 = array1[compound_index]
    arr2 = array2[compound_index]

    print "creates two arrays from the two original arrays"

    del array1
    del array2

    length_interval = len(arr1)/workers
    length_end = length_interval
    length_start = 0

    out_q = Queue()
    procs = []

    for x in range(0, len(arr1), length_interval):
        a1 = arr1[length_start:length_end]
        a2 = arr2[length_start:length_end]
        p = multiprocessing.Process(target=worker, args=(a1, a2, step1, step2, out_q))
        procs.append(p)
        p.start()

        length_start = x + length_interval
        length_end = length_end + length_interval

    # is it useful?
    del arr1
    del arr2

    resultdict = []
    for i in range(workers):
        resultdict.append(out_q.get())

    # check if the process was mono core
    log.info("Workers %s ", workers)
    if workers <= 1:
        log.info("Computation done in %s seconds ---" % str(time.time() - start_time))
        for p in procs:
             p.join()
        log.info("Computation done in %s seconds ---" % str(time.time() - start_time))
        return resultdict[0]
    else:
        log.info("Merging dictionaries")
        # merge ditionaries
        final_dict = dict()
        for d in resultdict:
            for key, value in d.iteritems():
                try:
                    final_dict[key]["freq"] += d[key]["freq"]
                except:
                    final_dict[key] = d[key]


        #log.info(final_dict)
        log.info("Computation done in %s seconds ---" % str(time.time() - start_time))

        for p in procs:
            print "-----------"
            p.terminate()
            try:
                # TODO: check the side effects of that workaround
                kill(p.pid, 9)
            except:
                pass

            print p, p.is_alive()
        log.info("Computation done in %s seconds ---" % str(time.time() - start_time))
        return final_dict

class SummingThread(threading.Thread):
    def __init__(self, array1, array2, step1, step2):
        super(SummingThread, self).__init__()
        self.array1=array1
        self.array2=array2
        self.step1=step1
        self.step2=step2


    def run(self):
        self.d = dict()
        log.info("lenght of: %s" , len(self.array1))
        for item_a, item_b in izip(self.array1, self.array2):
            value1 = round(item_a / self.step1, 2)
            value2 = round(item_b / self.step2, 2)
            key = str(value1) + "_" + str(value2)
            try:
                self.d[key]["freq"] += 1
            except:
                self.d[key] = {
                    "data": [item_a, item_b],
                    "freq": 1
                }



def couples_with_freq_slow(array1, array2, step1, step2, min1, min2, max1, max2, rows, cols, buckets, nodata=None):
    d = dict()
    print "couples_with_freq"
    for i in range(0, len(array1)):
        if array1[i] > min1 and array2[i] > min2:
            value1 = str(int(array1[i] / step1))
            value2 = str(int(array2[i] / step2))

            # key value
            key = str(value1 + "_" + value2)

            # TODO this should be a rounding, otherwise the last one wins
            value = [array1[i], array2[i]]

            freq = 1
            if key in d:
                freq = d[key]["freq"] + 1

            d[key] = {
                "data": value,
                "freq": freq
            }

    return d


def couples_with_freq_split(array1, array2, step1, step2, min1, min2, max1, max2, forced_min1, forced_min2, nodata1=None, nodata2=None, rounding=0):
    # TODO: the rounding should be calculated by the step interval probably
    log.info("Calculating frequencies")
    start_time = time.time()
    d = dict()

    index1 = (array1 > forced_min1) & (array1 <= max1) & (array1 != nodata1)
    index2 = (array2 > forced_min2) & (array2 <= max2) & (array2 != nodata2)

    # merge array indexes
    compound_index = index1 & index2

    # it creates two arrays from the two original arrays
    arr1 = array1[compound_index]
    arr2 = array2[compound_index]



    for item_a, item_b in izip(arr1, arr2):
        value1 = round(item_a / step1, 0)
        value2 = round(item_b / step2, 0)
        key = str(value1) + "_" + str(value2)
        try:
            d[key]["freq"] += 1
        except:
            d[key] = {
                "data": [item_a, item_b],
                "freq": 1
            }
    log.info("Computation done in %s seconds ---" % str(time.time() - start_time))
    print len(d)
    return d




def couples_with_freq(array1, array2, step1, step2, min1, min2, max1, max2, forced_min1, forced_min2, nodata1=None, nodata2=None, rounding=0):
    '''
        It uses instead of the other one a boolean filter that is slightly faster than the where condition
    :param array1:
    :param array2:
    :param step1:
    :param step2:
    :param min1:
    :param min2:
    :param max1:
    :param max2:
    :param forced_min1:
    :param forced_min2:
    :param nodata1:
    :param nodata2:
    :param rounding:
    :return:
    '''
    # TODO: the rounding should be calculated by the step interval probably
    log.info("Calculating frequencies")
    start_time = time.time()
    d = dict()

    index1 = (array1 > forced_min1) & (array1 <= max1) & (array1 != nodata1)
    index2 = (array2 > forced_min2) & (array2 <= max2) & (array2 != nodata2)

     # merge array indexes
    compound_index = index1 & index2

    # it creates two arrays from the two original arrays
    arr1 = array1[compound_index]
    arr2 = array2[compound_index]

    for item_a, item_b in izip(arr1, arr2):
        value1 = round(item_a / step1, 0)
        value2 = round(item_b / step2, 0)
        key = str(value1) + "_" + str(value2)
        try:
            d[key]["freq"] += 1
        except:
            d[key] = {
                "data": [item_a, item_b],
                "freq": 1
            }
    log.info("Computation done in %s seconds ---" % str(time.time() - start_time))
    print len(d)
    return d

def couples_with_freq_old(array1, array2, step1, step2, min1, min2, max1, max2, forced_min1, forced_min2, nodata1=None, nodata2=None, rounding=0):
    # TODO: the rounding should be calculated by the step interval probably
    log.info("Calculating frequencies")
    start_time = time.time()
    d = dict()
    for i in np.where((array1 > forced_min1) & (array1 <= max1) & (array1 != nodata1)):
        for j in np.where((array2 > forced_min2) & (array2 <= max2) & (array2 != nodata2)):
            #print len(numpy.intersect1d(i, j))
            for index in np.intersect1d(i, j):
                val1 = array1[index]
                val2 = array2[index]
                #value1 = str(round(float(array1[index] / step1), 0))
                #value2 = str(round(float(array2[index] / step2), 0))
                value1 = int(val1 / step1)
                value2 = int(val2 / step2)
                key = str(value1) + "_" + str(value2)

                # if key in d:
                #     d[key]["freq"] += 1
                # else:
                #     d[key] = {
                #             "data": [value1, value2],
                #             "freq": 1
                #        }
                try:
                    d[key]["freq"] += 1
                except:
                    d[key] = {
                        "data": [val1, val2],
                        "freq": 1
                       }
    # for v in d.values():
    #     print v
    log.info("Computation done in %s seconds ---" % str(time.time() - start_time))
    print len(d)
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
    bmap = brewer2mpl.get_map(color, color_type, intervals+1, reverse=reverse)
    colors = bmap.hex_colors

    # creating series
    series = []
    for color in colors:
        #print color
        series.append({
            "color": color,
            "data" : []
        })

    #print classes
    for v in values:
        freq = v['freq']
        for i in range(len(classes)):
            if freq <= classes[i]:
                series[i]['data'].append([float(v['data'][0]), float(v['data'][1])])
                break
    return series