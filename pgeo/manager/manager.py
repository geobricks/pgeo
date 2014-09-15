import os
from pgeo.geoserver.geoserver import Geoserver
from pgeo.metadata.metadata import Metadata
from pgeo.stats.raster import Stats
from pgeo.utils import filesystem
from pgeo.db.postgresql.postgis_utils import shapefile
from pgeo.error.custom_exceptions import PGeoException
from pgeo.utils import log
from pgeo.metadata.metadata_bridge import add_metadata_from_vector, add_metadata_from_raster, translate_from_metadata_to_geoserver


log = log.logger(__name__)


class Manager():

    metadata = None
    geoserver = None
    stats = None
    spatial_db = None

    def __init__(self, config):
        # self.metadata = Metadata(config["db"]["metadata"])
        self.metadata = Metadata(config)
        self.geoserver = Geoserver(config["geoserver"])
        self.spatial_db = config["db"]["spatial"]
        self.stats = Stats(config)


    def publish_shapefile(self, file_path, metadata_def=None, overwrite=False):
        """
        @param file_path:
        @param metadata_def:
        @param overwrite:
        @return:
        """
        try:
            # add additional layer info to the metadata i.e. bbox and EPSG code
            add_metadata_from_vector(file_path, metadata_def)
            # add additional layer info to the metadata i.e. bbox and EPSG code
            self._publish_coverage(file_path, metadata_def, translate_from_metadata_to_geoserver(metadata_def, file_path), overwrite)
        except PGeoException, e:
            raise PGeoException(e.get_message(), e.get_status_code())

    def _publish_shapefile(self, file_path, metadata_def=None, geoserver_def=None, overwrite=False):
        """
        @param file_path:
        @param layer_def:
        @param overwrite:
        @return:
        """
        try:
            # layer_def = layer_def["featureType"]

            # Unzip the shapefile
            shp_folder = filesystem.unzip(file_path)
            shp_name = filesystem.get_filename(file_path)

            # creating shp path
            shp_folder_and_name = os.path.join(shp_folder, shp_name) + ".shp"
            log.info(shp_folder_and_name)

            # sanitize the layer_name
            # name = sanitize_name(shp_name)
            name = sanitize_name(metadata_def["title"]["EN"])

            # getting the default workspace
            default_workspace = self.geoserver.get_default_workspace()
            if "workspace" in metadata_def["meSpatialRepresentation"]:
                default_workspace = metadata_def["meSpatialRepresentation"]["workspace"]

            # setting up the uid
            metadata_def["uid"] = default_workspace + ":" + name

            # publish shapefile on geoserver
            # TODO: merge the metadata with the default vector metadata
            if "name" not in geoserver_def:
                geoserver_def["name"] = name
            if "title" not in geoserver_def:
                geoserver_def["title"] = name
            if "workspace" not in geoserver_def:
                geoserver_def["workspace"] = self.geoserver.get_default_workspace()
            if "datastore" not in geoserver_def:
                geoserver_def["datastore"] = self.geoserver.get_default_datastore()

            # clean layer name
            geoserver_def["name"] = sanitize_name(geoserver_def["name"])

            # import the shapefile on postgis
            shapefile.import_shapefile(self.spatial_db, shp_folder_and_name, shp_name, True)

            # publish on metadata
            self.metadata.db_metadata.insert_metadata(metadata_def)

            # publish table on geoserver cluster
            self.geoserver.publish_postgis_table(geoserver_def, True)

            # remove files in input_shapefile
            filesystem.remove_folder(shp_folder)

        except PGeoException, e:
            log.error(e)
            self.rollback_shapefile()

    def publish_coverage(self, file_path, metadata_def=None, overwrite=False):
        """
        @param file_path:
        @param metadata_def:
        @param overwrite:
        @return:
        """
        try:
            # add additional layer info to the metadata i.e. bbox and EPSG code
            add_metadata_from_raster(file_path, metadata_def)
            # add additional layer info to the metadata i.e. bbox and EPSG code
            self._publish_coverage(file_path, metadata_def, translate_from_metadata_to_geoserver(metadata_def, file_path), overwrite)
        except PGeoException, e:
            raise PGeoException(e.get_message(), e.get_status_code())


    def _publish_coverage(self, file_path, metadata_def=None, geoserver_def=None, overwrite=False):
        """
        @param file_path:
        @param layer_def:
        @param overwrite:
        @return:
        """
        try:
            log.info(geoserver_def)
            # layer_def = layer_def["coverageStore"]

            # sanitize the layer_name
            #name = sanitize_name(filesystem.get_filename(file_path))
            name = sanitize_name(metadata_def["title"]["EN"])

            # getting the default workspace
            default_workspace = self.geoserver.get_default_workspace()
            if "workspace" in metadata_def["meSpatialRepresentation"]:
                default_workspace = metadata_def["meSpatialRepresentation"]["workspace"]

            # setting up the uid
            metadata_def["uid"] = default_workspace + ":" + name

            # publish coveragestore on geoserver
            # TODO: merge the metadata with the default vector metadata
            if "name" not in geoserver_def:
                geoserver_def["name"] = name
            if "title" not in geoserver_def:
                geoserver_def["title"] = name
            if "workspace" not in geoserver_def:
                geoserver_def["workspace"] = default_workspace

            # clean layer name
            #geoserver_def["name"] = sanitize_name(geoserver_def["name"])

            # publish on metadata
            self.metadata.db_metadata.insert_metadata(metadata_def)

            # publish table on geoserver cluster
            self.geoserver.publish_coveragestore(geoserver_def, True)

            # remove files and folder of the shapefile
            filesystem.remove_folder(file_path)

        except PGeoException, e:
            log.error(e)
            self.rollback_raster()


    def delete(self):
        return "TODO"

    def delete_raster(self):
        return "TODO"

    def delete_vector(self):
        return "TODO"

    def rollback_shapefile(self):
        # TODO: implement something if metadata or geoserver fails to publish or delete
        log.error("!!!!!!!!!!!!! TODO: Rollback of the imported table, metadata and geoserver layer")
        return None

    def rollback_raster(self):
        # TODO: implement something if metadata or geoserver fails to publish or delete
        log.error("!!!!!!!!!!!!! TODO: Rollback of the imported coveragestore and metadata")
        return None


def sanitize_name(name):
    """
    This method clean the name of a layer, should be avoided to use dots as names
    :param name: name of the layer
    :return: sanitized layer name
    """
    name = name.replace(".", "")
    name = name.replace(" ", "_")
    name = name.lower()
    return name
