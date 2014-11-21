from osgeo import gdal
import os
import subprocess
import glob
import json
from pgeo.utils import log
from pgeo.error.custom_exceptions import PGeoException

log = log.logger("processing")
key_function = ["extract_bands", "get_pixel_size"]


def process_data(obj):

    output_path = obj["output_path"]
    output_file_name = None
    output_file_extension = None
    try:
        output_file_name = obj["output_file_name"]
    except:
        pass

    source_path = obj["source_path"]
    band = obj["band"]

    p = Process(output_file_name)

    process = obj["process"]

    # deal with pixel size
    pixel_size = None
    #pixel_size = "0.0020833325"

    # defualt init is the source_path
    output_processed_files = source_path

    # looping throught processes
    for process_values in process:
        for key in process_values:
            log.info(output_processed_files)
            if key in key_function:

                # explicit functions
                if "extract_bands" in key:
                    output_processed_files = p.extract_bands(output_processed_files, band, output_path)
                # get the pixel size
                elif "get_pixel_size" in key:
                    log.info("get_pixel_size")
                    pixel_size = p.get_pixel_size(output_processed_files[0], process_values[key])
                    log.info(pixel_size)

            else:
                # STANDARD GDAL FUNCTIONS
                log.info("not function")
                log.info("parameters")
                log.info(key)
                log.info(process_values[key])
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

    def __init__(self, output_file_name=None, output_file_extension=None):
        if output_file_name is not None:
            self.output_file_name = output_file_name

    def extract_bands(self, input_files, band, output_path):
        log.info("extract_files_and_band_names")
        log.info(input_files)
        log.info("band: " + str(band))
        bands = []
        ext = None
        try:
            files = glob.glob(input_files[0])
            for f in files:
                gtif = gdal.Open(f)
                sds = gtif.GetSubDatasets()
                bands.append(sds[int(band) - 1][0])
                if ext is None:
                    filename, ext = os.path.splitext(f)
            return self.extract_band_files(bands, output_path, ext)
        except Exception, e:
            log.error(e)
            raise PGeoException(e.message, 500)

    def extract_band_files(self, input_files, output_path, ext=None):
        output_files = []
        i = 0
        try:
            for f in input_files:
                print get_filename(f, True)
                output_file_path = os.path.join(output_path, str(i) + ext)
                cmd = "gdal_translate '" + f + "' " + output_file_path
                log.info(cmd)
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                output, error = process.communicate()
                log.info(output)
                output_files.append(output_file_path)
                i += 1
            return output_files
        except Exception, e:
            log.error(e)
            raise PGeoException(e.message, 500)

    def get_pixel_size(self, input_file, formula=None):
        cmd = "gdalinfo "
        cmd += input_file
        cmd += " | grep Pixel"
        log.info(cmd)
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output, error = process.communicate()
            log.info(output)
            if "Pixel Size" in output:
                pixel_size = output[output.find("(")+1:output.find(",")]
                log.info(pixel_size)
                formula = formula.replace("{{PIXEL_SIZE}}", str(pixel_size))
                log.info(formula)
                return eval(formula)
            return None
        except Exception, e:
            log.error(e)
            raise PGeoException(e.message, 500)

    def gdal_merge(self, parameters, input_files, output_path):
        output_files = []
        output_file = os.path.join(output_path, self.output_file_name)
        log.info(output_file)
        output_files.append(output_file)
        cmd = "gdal_merge.py "
        log.info(cmd)
        if "opt" in parameters:
            for key in parameters["opt"].keys():
                log.info(key)
                cmd += " " + key + " " + str(parameters["opt"][key])
        for input_file in input_files:
            cmd += " " + input_file
        cmd += " -o " + output_file
        log.info(cmd)
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output, error = process.communicate()
            log.info(output)
            return output_files
        except Exception, e:
            log.error(e)
            raise PGeoException(e.message, 500)

    def gdalwarp(self, parameters, input_files, output_path):
        log.info(input_files)
        output_files = []
        output_file = os.path.join(output_path, self.output_file_name)
        output_files.append(output_file)
        cmd = "gdalwarp "
        if "opt" in parameters:
            for key in parameters["opt"].keys():
                cmd += " " + key + " " + str(parameters["opt"][key])
        for input_file in input_files:
            cmd += " " + input_file
        cmd += " " + output_file
        log.info(cmd)
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output, error = process.communicate()
            log.info(output)
            return output_files
        except Exception, e:
            log.error(e)
            raise PGeoException(e.message, 500)

    def gdal_translate(self, parameters, input_files, output_path):
        output_files = []
        output_file = os.path.join(output_path, self.output_file_name)
        output_files.append(output_file)
        cmd = "gdal_translate "
        if "opt" in parameters:
            for key in parameters["opt"].keys():
                cmd += " " + key + " " + str(parameters["opt"][key])
        for input_file in input_files:
            cmd += " " + input_file
        cmd += " " + output_file
        log.info(cmd)
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output, error = process.communicate()
            log.info(output)
            return output_files
        except Exception, e:
            log.error(e)
            raise PGeoException(e.message, 500)


    def gdaladdo(self, parameters, input_files, output_path=None):
        output_files = []
        cmd = "gdaladdo "
        for key in parameters["parameters"].keys():
            cmd += " " + key + " " + str(parameters["parameters"][key])
        for input_file in input_files:
            cmd += " " + input_file
            output_files.append(input_file)
        cmd += " " + parameters["overviews_levels"]
        log.info(cmd)
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output, error = process.communicate()
            log.info(output)
            return output_files
        except Exception, e:
            log.error(e)
            raise PGeoException(e.message, 500)


def callMethod(o, name, options, input_files):
    getattr(o, name)(options, input_files)

def get_filename(filepath, extension=False):
    drive, path = os.path.splitdrive(filepath)
    path, filename = os.path.split(path)
    name = os.path.splitext(filename)[0]
    if extension is True:
        return path, filename, name
    else:
        return name