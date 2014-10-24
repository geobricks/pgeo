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
import Queue
from pgeo.utils.log import logger
from pgeo.error.custom_exceptions import PGeoException

log = logger("pgeo.gis.raster_scatter")


# print "here"
# cal= mapclassify.load_example()
# print cal
# ei=mapclassify.Equal_Interval(cal,k=5)
# print ei


def create_scatter(raster_path1, raster_path2, band1=1, band2=1, buckets=200, intervals=6, forced_min1=0, forced_min2=0, color='Reds', color_type='Sequential', reverse=False):
    ds1 = gdal.Open(raster_path1)
    ds2 = gdal.Open(raster_path2)
    rows1 = ds1.RasterYSize
    cols1 = ds1.RasterXSize
    rows2 = ds2.RasterYSize
    cols2 = ds2.RasterXSize

    log.info("Scatter Processing")
    if cols1 != cols2 or rows1 != rows2:
        log.info("The rasters cannot be processed because they have different dimensions")
        raise PGeoException("The rasters cannot be processed because they have different dimensions", status_code=404)

    band1 = ds1.GetRasterBand(band1)
    array1 = np.array(band1.ReadAsArray()).flatten()

    nodata1 = band1.GetNoDataValue()

    band2 = ds2.GetRasterBand(band2)
    array2 = np.array(band2.ReadAsArray()).flatten()
    nodata2 = band2.GetNoDataValue()


    # min/max calulation
    (min1, max1) = band1.ComputeRasterMinMax(0)
    step1 = (max1 - min1) / buckets
    (min2, max2) = band2.ComputeRasterMinMax(0)
    step2 = (max2 - min2) / buckets

    # Calculation of the frequencies
    freqs = couples_with_freq(array1, array2, step1, step2, min1, min2, max1, max2, forced_min1, forced_min2, nodata1, nodata2)
    #print len(freqs)
    series = get_series(freqs.values(), intervals, color, color_type, reverse)

    #print series
    result = dict()
    # probably not useful for the chart itself
    # result['min1'] = min1,
    # result['min2'] = min2,
    # result['max2'] = max2,
    # result['step1'] = step1,
    # result['step2'] = step2
    result['series'] = series
    return result


def couples_with_freq_multithread(array1, array2, step1, step2, min1, min2, max1, max2, rows, cols, buckets, nodata=None):
    print "multithreaded"


    threads = 3
    array_length = int((len(array1)/threads))
    print "array_length", array_length
    base=0
    arrays1 = []
    for i in range(0, threads):
        arrays1.append(array1[base:array_length*(i+1)])
        base = array_length

    # arrays1 = array[:]
    print "arrays1", arrays1

    arrays2 = []
    base=0
    for i in range(0, threads):
        arrays2.append(array2[:array_length*(i+1)])
        base = array_length
    print "arrays2"

    print "starts"
    lock = ""
    ts = []
    q = Queue.Queue()
    for i in range(threads):
        t = Thread(target=thread_func, args=(arrays1[i], arrays2[i], min1, min2, step1, step2, q))
        ts.append(t)
        t.start()
        t.join()
        # ts.append(threading.Thread(target=thread_func, args=(arrays1[i], arrays2[i], min1, min2, step1, step2, lock)))


    for i in range(threads):
        for key, value in q.get().items() :
            print key, value

        #print "worker %d returned %d" % q.get()

   # print [q.get() for _ in xrange(len(threads))]


    return q.get()


def thread_func(array1, array2, min1, min2, step1, step2, queue):
    print "threads", len(array1)
    d = dict()
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

    queue.put(d)


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


def couples_with_freq(array1, array2, step1, step2, min1, min2, max1, max2, forced_min1, forced_min2, nodata1=None, nodata2=None, rounding=0):
    # TODO: the rounding should be calculated by the step interval probably
    log.info("Calculating frequencies")
    start_time = time.time()
    d = dict()
    for i in np.where((array1 > forced_min1) & (array1 <= max1) & (array1 != nodata1)):
        for j in np.where((array2 > forced_min2) & (array2 <= max2) & (array2 != nodata2)):
            #print len(numpy.intersect1d(i, j))
            for index in np.intersect1d(i, j):
                #value1 = str(round(float(array1[index] / step1), 0))
                #value2 = str(round(float(array2[index] / step2), 0))
                value1 = str(int(array1[index] / step1))
                value2 = str(int(array2[index] / step2))
                key = value1 + "_" + value2

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
                        "data": [array1[index], array2[index]],
                        "freq": 1
                       }
    # for v in d.values():
    #     print v
    log.info("Computation done in %s seconds ---" % str(time.time() - start_time))
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