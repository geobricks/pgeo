from osgeo import gdal, osr, ogr
import os
import subprocess
import glob
import math
import json
from pgeo.utils import log
from pgeo.utils import filesystem
from pgeo.error.custom_exceptions import PGeoException, errors

log = log.logger("processing")

key_function = ["extract_bands", "get_pixel_size"]


def process(obj):
    p = Process()

    output_path = obj["output_path"]
    output_file_name = obj["output_file_name"]
    source_path = obj["source_path"]
    band = obj["band"]

    process = obj["process"]

    # deal with pixel size
    pixel_size = None
    #pixel_size = "0.0020833325"

    # defualt init is the source_path
    output_processed_files = source_path

    # looping throught processes
    for process_values in process:
        for key in process_values:
            print output_processed_files
            # print key_function
            # for key, value in my_dict.iteritems():
            if key in key_function:
                # explicit functions
                if "extract_bands" in key:
                    output_processed_files = p.extract_bands(output_processed_files, band, output_path)
                # get the pixel size
                elif "get_pixel_size" in key:
                    print "get_pixel_size"
                    pixel_size = p.get_pixel_size(output_processed_files[0], process_values[key])
                    log.info(pixel_size)

            else:
                # STANDARD GDAL FUNCTIONS
                print "not function"
                print "parameters"
                print key
                print process_values[key]
                process_values[key] = change_values(process_values[key], pixel_size)

                # reflection calls
                output_processed_files = getattr(p, key)(process_values[key], output_processed_files, output_path)


    return output_processed_files


def change_values(obj, pixel_size):
    s = json.dumps(obj)
    log.info(pixel_size)
    log.info(s)
    s = s.replace("{{PIXEL_SIZE}}", str(pixel_size))

    log.info(s)
    return json.loads(s)


# Class to process using reflection
class Process:

    def __init__(self):
        return None

    def extract_bands(self, input_files, band, output_path):
        print "extract_files_and_band_names"
        print input_files
        print band
        bands = []
        ext = None
        files = glob.glob(input_files[0])
        for f in files:
            gtif = gdal.Open(f)
            sds = gtif.GetSubDatasets()
            bands.append(sds[int(band) - 1][0])
            if ext is None:
                filename, ext = os.path.splitext(f)

        # TODO: get extension
        return self.extract_band_files(bands, output_path, ext)

    def extract_band_files(self, input_files, output_path, ext=None):
        output_files = []
        i = 0;
        for f in input_files:
            output_file_path = os.path.join(output_path, str(i) + ext)
            cmd = "gdal_translate '" + f + "' " + output_file_path
            log.info(cmd)
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output, error = process.communicate()
            #TODO catch the error
            log.info(output)
            log.warn(error)
            output_files.append(output_file_path)
            i += 1
        return output_files

    def get_pixel_size(self, input_file, formula=None):
        log.info("get_pixel_size")
        log.info(input_file)
        log.info(formula)
        pixel_size = None

        # creating the cmd
        cmd = "gdalinfo "
        cmd += input_file

        # gdalinfo 'HDF4_EOS:EOS_GRID:"/home/vortex/Desktop/LAYERS/MODIS/033/MOD13Q1.A2014033.h23v09.005.2014050114129.hdf":MODIS_Grid_16DAY_250m_500m_VI:250m 16 days NDVI' | grep size

        cmd += " | grep Pixel"

        log.info(cmd)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()
        log.info(output)
        log.warn(error)
        if "Pixel Size" in output:
            pixel_size = output[output.find("(")+1:output.find(",")]
            log.info(pixel_size)
            formula = formula.replace("{{PIXEL_SIZE}}", str(pixel_size))
            log.info(formula)
            return eval(formula)
        return None

    def gdal_merge(self, parameters, input_files, output_path):
        print "gdal_merge"
        output_files = []

        output_file = os.path.join(output_path, "gdal_merge.hdf")
        output_files.append(output_file)

        # creating the cmd
        cmd = "gdal_merge.py "
        for key in parameters.keys():
            cmd += " " + key + " " + str(parameters[key])

        for input_file in input_files:
            cmd += " " + input_file

        cmd += " -o " + output_file

        log.info(cmd)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()
        log.info(output)
        log.warn(error)
        log.info(output_files)
        return output_files

    def gdalwarp(self, parameters, input_files, output_path):
        print "gdalwarp input_files"
        print input_files
        output_files = []
        output_file = os.path.join(output_path, "warp")
        output_files.append(output_file)

        cmd = "gdalwarp "
        for key in parameters["opt"].keys():
            cmd += " " + key + " " + str(parameters["opt"][key])

        for input_file in input_files:
            cmd += " " + input_file

        cmd += " " + output_file

        log.info(cmd)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()
        log.info(output)
        log.warn(error)
        log.info(output_files)
        return output_files

    def gdaladdo(self, parameters, input_files, output_path=None):
        log.info(parameters)
        log.info(input_files)
        output_files = []
        cmd = "gdaladdo "
        for key in parameters["parameters"].keys():
            cmd += " " + key + " " + str(parameters["parameters"][key])

        for input_file in input_files:
            cmd += " " + input_file
            output_files.append(input_file)


        cmd += " " + parameters["overviews_levels"]

        log.info(cmd)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()
        log.info(output)
        log.warn(error)
        return output_files


def callMethod(o, name, options, input_files):
    getattr(o, name)(options, input_files)
