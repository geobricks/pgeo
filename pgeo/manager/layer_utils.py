import glob
import os
import json
from pgeo.config.settings import settings, read_config_file_json
from pgeo.manager.manager import Manager, sanitize_name
from pgeo.utils.log import logger
from pgeo.utils import filesystem
from pgeo.metadata.metadata import merge_layer_metadata

log = logger("pgeo.manager.layer_utils")

raster_template = "raster"

metadata_json = {}

def harvest_folder(path):
    """
    Harvest files in a path
    :param path:
    :return:
    """
    manager = Manager(settings)
    types = ('*.tiff', '*.geotiff', "*.gtiff", "*.tif")
    # for each tiff, geotiff, tif, gtiff
    files_grabbed = []
    for file_type in types:
        files_grabbed.extend(glob.glob(os.path.join(path, file_type)))

    for file in files_grabbed:
        path, filename, name = filesystem.get_filename(file, True)
        #log.info("%s %s %s " % (path, filename, name))
        if manager.geoserver.check_if_coveragestore_exist(name) is False:
            metadata_file = os.path.join(path, name + ".json")
            log.info("Check Metadata File: %s" % metadata_file)
            if os.path.isfile(metadata_file):
                metadata_json = json.loads(open(metadata_file).read())
                log.info(metadata_json)

                # exists a metadata file
                # merge with raster_metadata
            # TODO: create a default metadata if the file doesn't exists it doesn't exists
            metadata = merge_layer_metadata(raster_template, metadata_json)

            # process metadata with the default workspace if uid is not set in the medata
            if "uid" not in metadata:
                metadata["uid"] = manager.geoserver.get_default_workspace() + ":" + sanitize_name(name)

            # TODO: read EPSG from file

            manager.publish_coverage(file, metadata)

        else:
            log.warn("Coverage '%s' already exists " % name)


def remove_uploded():
    return None

harvest_folder("/home/vortex/Desktop/LAYERS/bulk_import_test/")




