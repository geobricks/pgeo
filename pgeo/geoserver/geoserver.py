import httplib2
import os
import json
from copy import deepcopy
from urlparse import urlparse
from pgeo.geoserver.gsutils import url, prepare_upload_bundle
from pgeo.db.postgresql.postgis_utils import shapefile
from pgeo.utils import log
from pgeo.error.custom_exceptions import PGeoException, errors
from pgeo.utils.filesystem import get_filename, zip_files, unzip

log = log.logger(__name__)


class Geoserver():

    config = None

    # TODO: as converntion all the layers/styles should be in lowercase?

    def __init__(self, config, disable_ssl_certificate_validation=False):
        """
        Initialize and configure the GeoServer.
        The GeoServer properties are passed in the config file
        """
        self.config = config

        # use as parameters
        self.service_url = self.config['geoserver_master']
        self.username = self.config['username']
        self.password = self.config['password']

        if self.service_url.endswith("/"):
            self.service_url = self.service_url.strip("/")
        self.http = httplib2.Http(
            disable_ssl_certificate_validation=disable_ssl_certificate_validation)
        self.http.add_credentials(self.username, self.password)
        netloc = urlparse(self.service_url).netloc
        self.http.authorizations.append(
            httplib2.BasicAuthentication(
                (self.username, self.password),
                netloc,
                self.service_url,
                {},
                None,
                None,
                self.http
            ))
        self._cache = dict()
        self._version = None
        return None


    def publish_coveragestore(self, data, overwrite=False):

        # data = data["coverageStore"]
        log.info(data)
        name = data["name"]
        workspace = self.get_default_workspace() if "workspace" not in data else data["workspace"]
        path = data["path"]

        if not overwrite:
            if self.check_if_layer_exist(name, workspace):
                raise PGeoException(errors[520]+": %s" % name)

        # default geotiff headers and extension
        headers = get_headers("tiff")
        ext = "geotiff"

        # check if the layer is a tfw (a zipfile)
        #TODO: make it work with tif+tfw
        path_folder_tif, filename_tif, name_tif  = get_filename(path, True)
        file_tfw = os.path.join(path_folder_tif, name_tif + ".tfw")
        if os.path.isfile(file_tfw):
            # handle 'tfw' (worldimage)
            bundle = [path, file_tfw]
            log.info(bundle)
            archive = zip_files(name, bundle, path_folder_tif)
            log.info(archive)
            #message = open(archive, 'rb')
            message = archive
            headers = get_headers("zip")
            ext = "worldimage"
        elif isinstance(path, basestring):
            message = open(path, 'rb')
        else:
            message = path

        log.info(message)

        try:
            # Add layer to coveragestore
            cs_url = url(self.service_url, ["workspaces", workspace, "coveragestores", name, "file." + ext])
            self._publish_layer(cs_url, "PUT", message, headers, 201)

            #  Update metadata of the layer
            headers = get_headers("json")
            json_data = deepcopy(data)
            del json_data['name']
            # set has default enabled the layer
            if "enabled" not in json_data:
                json_data["enabled"] = True
            # json to send to geoserver
            update_layer = {
                "coverage" : json_data
            }
            cs_url = url(self.service_url, ["workspaces", workspace, "coveragestores", name, "coverages", name  + ".json"])
            log.info(cs_url)
            self._publish_layer(cs_url, "PUT", json.dumps(update_layer), headers, 200)

            # TODO: check why doesn't update the default style
            if 'defaultStyle' in json_data:
                if 'name' in json_data['defaultStyle']:
                    self.set_default_style(name, json_data['defaultStyle']['name'])
        except PGeoException, e:
            log.error(e.get_message())
            raise PGeoException(e.get_message(), e.get_status_code())
        except Exception, e:
            log.error(e)
            raise PGeoException(e)
        finally:
            # check if it always called
            self.reload_configuration_geoserver_slaves()
        return True


    def publish_postgis_table(self, data, overwrite=False):
        """
        :param datasource: datasource stored in geoserver
        :param name: name of the table in postgis
        :return:
        """
        #curl -v -u admin:geoserver -XPOST -H "Content-type: text/xml" -d "<featureType><name>buildings</name></featureType>"
        #http://localhost:8080/geoserver/rest/workspaces/acme/datasources/nyc/featuretypes

        #data = data["featureType"]

        name = data["name"]
        log.info(name)
        workspace = self.get_default_workspace() if "workspace" not in data else data["workspace"]
        datastore = self.get_default_datastore() if "datastore" not in data else data["datastore"]


        if not overwrite:
            log.warn("TODO: shapefile")
            #if self.check_if_layer_exist(name, workspace):
            #  raise PGeoException(errors[520]+": %s" % name)

        try:
            # TODO this can be done with just one request

            # Add layer to coveragestore
            headers = get_headers("xml")
            xml = "<featureType><name>{0}</name></featureType>".format(unicode(name).lower())
            cs_url = url(self.service_url, ["workspaces", workspace, "datastores", datastore, 'featuretypes'])
            self._publish_layer(cs_url, "POST", xml, headers)

            #  Update metadata of the layer
            headers = get_headers("json")
            json_data = deepcopy(data)
            del json_data['name']
            # set has default enabled the layer
            if "enabled" not in json_data:
                json_data["enabled"] = True
            # json to send to geoserver
            update_layer = {
                "featureType" : json_data
            }
            cs_url = url(self.service_url, ["workspaces", workspace, "datastores", datastore, "featuretypes", name + ".json"] )
            log.info(cs_url)
            self._publish_layer(cs_url, "PUT", json.dumps(update_layer), headers, 200)

            # TODO: check why doesn't update the default style
            if 'defaultStyle' in json_data:
                if 'name' in json_data['defaultStyle']:
                    log.info("change default style style")
                    self.set_default_style(name, json_data['defaultStyle']['name'])
        except PGeoException, e:
            log.error(e.get_message())
            raise PGeoException(e.get_message(), e.get_status_code())
        except Exception, e:
            log.error(e)
            raise PGeoException(e)
        finally:
            # check if it always called
            self.reload_configuration_geoserver_slaves()
        return True



    def _publish_layer(self, cs_url, c_type, message, headers, expected_code=201):
        try:
            log.info("%s %s" % (cs_url, headers))
            headers, response = self.http.request(cs_url, c_type, message, headers)
            self._cache.clear()
            log.info("%s %s %s" % (message, headers, response))

            if headers.status != expected_code:
            #raise UploadError(response)
                log.info(headers)
                log.info(response)
                raise PGeoException(response, headers.status)
        except PGeoException, e:
            log.error(e)
            raise PGeoException(e.get_message(), e.get_status_code())
        except Exception, e:
            log.error(e)
            raise PGeoException(e)
        finally:
            if hasattr(message, "close"):
                # reload geoserver cluster
                self.reload_configuration_geoserver_slaves()
                message.close()
                return True
            # if archive is not None:
            #     log.warn('call nlink(archive) : ' + archive)
            #     # nlink(archive)

    def update_layer_metadata(self, name, data, c_type="json"):
        """
        Update the layer by json or xml
        @param name: name of the layer
        @type name: string
        @param data: json
        @type name: string cointaining the data to update i.e. json '{"layer":{"title":"title of the layer"}}' or xml <layer><title>title of the layer</title></layer>
        @param type: string that can be "json" or "xml"
        @type name: string
        @return: True if updated
        """
        try:
            headers = get_headers(c_type)
            cs_url = url(self.service_url, ["layers", name + "." + c_type])
            log.info(cs_url)
            self._publish_layer(cs_url, "PUT", data, headers, 200)
        except Exception, e:
            log.error(e)
            raise PGeoException(e)
        finally:
            # check if it always called
            self.reload_configuration_geoserver_slaves()
            return True

    def delete_coveragestore(self, name, workspace=None, purge=True, recurse=True):
        if workspace is None:
            workspace = self.get_default_workspace()

        # TODO: it makes two, calls, so probably it's better just handle the delete code
        if self.check_if_layer_exist(name, workspace):
            cs_url = url(self.service_url, ["workspaces", workspace, "coveragestores", name])
            return self.delete(cs_url, purge, recurse)

    def delete(self, rest_url, purge=False, recurse=False):
        """
        send a delete request
        """

        #params aren't supported fully in httplib2 yet, so:
        params = []

        # purge deletes the SLD from disk when a style is deleted
        if purge:
            params.append("purge=true")

        # recurse deletes the resource when a layer is deleted.
        if recurse:
            params.append("recurse=true")

        if params:
            rest_url = rest_url + "?" + "&".join(params)

        headers = get_headers("xml")
        response, content = self.http.request(rest_url, "DELETE", headers=headers)
        self._cache.clear()

        if response.status == 200:
            # reload geoservers slaves configurations
            self.reload_configuration_geoserver_slaves()
            return True
        else:
           raise PGeoException(content, headers.status)

    def check_if_layer_exist(self, name, workspace=None):
        if workspace is None:
            workspace = self.get_default_workspace()
        layername = workspace +":" + name
        cs_url = url(self.service_url, ["layers", layername + ".json"])
        log.info("checking coverage exists: %s (%s)" % (name, cs_url))
        response, content = self.http.request(cs_url, "GET")
        if response.status == 200:
            return True
        elif response.status == 404:
            return False
        return False


    def set_default_style(self, name, stylename, enabled=True):
        """
        Method used to change the default style of a layer
        :param stylename: the name of the style to set ad default one
        :param layername: the name of the layer
        :param enabled: enable/disable the style
        :return:
        """
        # curl -v -u $GEOSERVER_PASSWORD -XPUT -H "Content-type: text/xml" -d "<layer><defaultStyle><name>$DEFAULT_STYLE</name></defaultStyle><enabled>$ENABLED</enabled></layer>" $GEOSERVER_URL/rest/layers/$GEOSERVER_WORKSPACE:$NAME
        headers = get_headers("xml")
        xml = "<layer><defaultStyle><name>{0}</name></defaultStyle><enabled>{1}</enabled></layer>".format(unicode(stylename).lower(),  unicode(str(enabled).upper()))
        cs_url = url(self.service_url, ["layers", name])
        log.info("Change Layer: %s  default style in %s" % (name, stylename))
        headers, response = self.http.request(cs_url, "PUT", xml, headers)
        print cs_url
        if headers.status == 200:
            # reload geoserver cluster
            self.reload_configuration_geoserver_slaves()
        else:
            raise PGeoException(response, headers.status)
        return True

    # TODO: DELETE, should not be used! use pgeo.manager.manager
    def publish_shapefile(self, input_shapefile, name, overwrite=False, workspace=None, projection=None, default_style=None, layertype=None, metadata=None):
        """
        :param input_shapefile:
        :param name:
        :param overwrite:
        :param workspace:
        :param projection:
        :param default_style:
        :param layertype:
        :param metadata:
        :return:
        """

        # TODO: check if it's a shp or zip
        '''
        if zip:
            unzip "in tmp to be removed"
        '''
        datasource = self.get_default_datasource()
        shapefile.import_shapefile(datasource, input_shapefile, name)

        # publish shapefile
        self.publish_postgis_table(datasource, name)
        return "published"




    def checkIFdatasourceExist(self, name):
        print 'TODO'

    def get_default_workspace(self):
        return self.config['default_workspace']

    def get_default_datastore(self):
        return self.config['default_datastore']

    def reload_configuration_geoserver_slaves(self, force_master_reload=False):
        geoserver_cluster = self.config["geoserver_slaves"]

        if force_master_reload is True:
            geoserver_cluster.append(self.config["geoserver_master"])

        for geoserver in geoserver_cluster:
            cs_url =  url(geoserver, ["reload?recurse=true"])
            headers, response = self.http.request(cs_url, "POST")
            log.info(headers)
            if headers.status == 200:
                return True
            else:
                return False


def get_headers(c_type):
    c_type = c_type.lower()
    headers = {
        "Accept": "application/xml"
    }
    if c_type == "geotiff":
        headers["Content-type"] = "image/tiff"
    elif c_type == "tiff":
        headers["Content-type"] = "image/tiff"
    elif c_type == "xml":
        headers["Content-type"] = "application/xml"
    elif c_type == "json":
        headers["Content-type"] = "application/json"
    elif c_type == "archive":
        headers["Content-type"] = "application/archive"
    elif c_type == "zip":
        headers["Content-type"] = "application/zip"
    else:
        raise PGeoException('Headers type "%s" not supported' % type)

    return headers