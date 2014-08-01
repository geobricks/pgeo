import httplib2
from urlparse import urlparse
from pgeo.geoserver.gsutils import url, prepare_upload_bundle
from pgeo.db.postgresql.postgis_utils import shapefile
from pgeo.utils import log
from pgeo.error.custom_exceptions import PGeoException, errors

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



    '''def publish_raster(self, input_raster, name, layertype='GEOTIFF', workspace='fenix', metadata=''):
        self.logger.info('raster: ' + input_raster)
        #cmd = "curl -u '"+ self.config['username') +":" + self.config['password') + "' -XPUT -H 'Content-type:image/tiff' -T "+ input_raster + " " + self.config['geoserver_master') +"/workspaces/"+ workspace +"/coveragestores/"+ name +"/file.geotiff"
        return "published"
    '''
    #  TODO: check if the world image works!
    def publish_coveragestore(self, data, overwrite=False):

        name = data["name"]
        workspace = self.get_default_workspace() if "workspace" not in data else data["workspace"]
        path = data["path"]

        if not overwrite:
            if self.check_if_coveragestore_exist(name, workspace):
                raise PGeoException(errors[520]+": %s" % name)

        # default geotiff headers and extension
        headers = {
            "Content-type": "image/tiff",
            "Accept": "application/xml"
        }
        archive = None
        ext = "geotiff"

        # check if the layer is a tfw (a zipfile)
        if isinstance(path, dict):
            # handle 'tfw' (worldimage)
            archive = prepare_upload_bundle(name, path)
            print archive
            message = open(archive, 'rb')
            if "tfw" in path:
                headers['Content-type'] = 'application/archive'
                ext = "worldimage"
        elif isinstance(path, basestring):
            message = open(path, 'rb')
        else:
            message = path

        log.info(message)



        # # ADDING THE LAYER
        # cs_url = url(self.service_url, ["workspaces", workspace, "coveragestores", name, "file." + ext])
        #
        # self._publish_coveragestore(cs_url, "PUT", message, headers)
        #
        #
        #
        # log.info("----------")
        # # ADDING THE METADATA
        # headers = {
        #     "Content-type": "application/xml",
        #     "Accept": "application/xml"
        # }
        #
        # cs_url = url(self.service_url, ["workspaces", workspace, "coveragestores", name])
        # xml = "<coverageStore>" \
        #             "<name>"+ str(name) +"</name>" \
        #             "<workspace>"+ str(workspace) +"</workspace>" \
        #             "<enabled>true</enabled>" \
        #             "<type>GeoTIFF</type>" \
        #             "<title>oiajsdoijaosdijoisdaj</title>" \
        #             "<abstract>oiajsdoijaosdijoisdaj</abstract>" \
        #             "</coverageStore>"
        #
        # log.info(headers)
        # log.info(name)
        # self._publish_coveragestore(cs_url, "PUT", xml, headers)


        #  CREATE COVERAGESTORE
        headers = {
            "Content-type": "application/xml",
            "Accept": "application/xml"
        }

        cs_url = url(self.service_url, ["workspaces", workspace, "coveragestores"])
        xml = "<coverageStore>" \
                    "<name>"+ str(name) +"</name>" \
                    "<workspace>"+ str(workspace) +"</workspace>" \
                    "<enabled>true</enabled>" \
                    "<type>GeoTIFF</type>" \
                    "<title>oiajsdoijaosdijoisdaj</title>" \
                    "<abstract>oiajsdoijaosdijoisdaj</abstract>" \
            "</coverageStore>"

        log.info(headers)
        log.info(name)
        self._publish_coveragestore(cs_url, "POST", xml, headers)

        #  ADD LAYER TO COVERAGESTORE
        headers = {
            "Content-type": "image/tiff",
            "Accept": "application/xml"
        }
        cs_url = url(self.service_url, ["workspaces", workspace, "coveragestores", name, "file." + ext])
        # self._publish_coveragestore(cs_url, "PUT", message, headers)


    # # CREATE COVERAGESTORE
    # curl -u $user:$passwd -v -XPOST -H 'Content-Type: application/xml' -d '<coverageStore><name>'$store'</name><workspace>'$workspace'</workspace></coverageStore>' ${geoserver_uri}/rest/workspaces/$workspace/coveragestores
    #
    # # ADD LAYER TO COVERAGESTORE
    # curl -u $user:$passwd -v -XPUT -H 'Content-Type: text/plain' -d 'file:'${file} ${geoserver_uri}/rest/workspaces/$workspace/coveragestores/$store/external.geotiff?configure=first\&coverageName=$store
    #
    # # ENABLE LAYER BUT NOT ADVERTISING IT
    # # it's not possible to set SRS from REST, so enable the layer is wasteful without that. At least, with the layer I've tested, which geoserver didn't recognize the SRS.
    # curl -u $user:$passwd -v -XPUT -H 'Content-Type: text/xml' -d '<layer><metadata><entry key="advertised">false</entry></metadata><enabled>true</enabled></layer>' ${geoserver_uri}/rest/layers/$layer
    #
    # # ENABLE COVERAGE
    # # after adding the layer, and if it has right SRS, it's possible to enable the store
    # curl -u $user:$passwd -v -XPUT -d '<coverageStore><name>'$store'</name><enabled>true</enabled></coverageStore>' -H "Content-Type: text/xml" ${geoserver_uri}/rest/workspaces/$workspace/coveragestores/$store.xml



        return True


    def _publish_coveragestore(self, cs_url, type, message, headers):
        log.info(cs_url)
        try:
            headers, response = self.http.request(cs_url, type, message, headers)
            self._cache.clear()
            if headers.status != 201:
            #raise UploadError(response)
                log.info(headers)
                log.info(response)
                raise PGeoException(response, headers.status)

        finally:
            # log.info("Layer %s uploaded" % name)
            if hasattr(message, "close"):
                # reload geoserver cluster
                self.reload_configuration_geoserver_slaves()
                message.close()
                return True
            # if archive is not None:
            #     log.warn('call nlink(archive) : ' + archive)
            #     # nlink(archive)


    def delete_coveragestore(self, layername, workspace=None, purge=True, recurse=True):
        if workspace is None:
            workspace = self.get_default_workspace()

        # TODO: it makes two, calls, so probably it's better just handle the delete code
        if self.check_if_coveragestore_exist(layername, workspace):
            cs_url = url(self.service_url, ["workspaces", workspace, "coveragestores", layername])
            log.info(cs_url);
            #headers, response = self.http.request(cs_url, "DELETE")

            return self.delete(cs_url, purge, recurse)
        else:
            return "NO COVERAGE STORE AVAILABLE"

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

        headers = {
            "Content-type": "application/xml",
            "Accept": "application/xml"
        }
        response, content = self.http.request(rest_url, "DELETE", headers=headers)
        self._cache.clear()

        log.info(response)

        if response.status == 200:
            #return (response, content)
            # reload geoserver cluster
            self.reload_configuration_geoserver_slaves()
            return 'coverage uploaded'
        else:
            log.error("Tried to make a DELETE request to %s but got a %d status code: \n%s" % (rest_url, response.status, content))
            #raise FailedRequestError("Tried to make a DELETE request to %s but got a %d status code: \n%s" % (rest_url, response.status, content))
            return ("Tried to make a DELETE request to %s but got a %d status code: \n%s" % (rest_url, response.status, content))

    def check_if_coveragestore_exist(self, name, workspace=None):
        if workspace is None:
            workspace = self.get_default_workspace()
        cs_url = url(self.service_url, ["workspaces", workspace, "coveragestores", name])
        response, content = self.http.request(cs_url, "GET")
        if response.status == 200:
            return True
        elif response.status == 404:
            return False
        return False


    def set_default_style(self, stylename, layername, enabled=True):
        """
        Method used to change the default style of a layer
        :param stylename: the name of the style to set ad default one
        :param layername: the name of the layer
        :param enabled: enable/disable the style
        :return:
        """
        # curl -v -u $GEOSERVER_PASSWORD -XPUT -H "Content-type: text/xml" -d "<layer><defaultStyle><name>$DEFAULT_STYLE</name></defaultStyle><enabled>$ENABLED</enabled></layer>" $GEOSERVER_URL/rest/layers/$GEOSERVER_WORKSPACE:$NAME
        headers = {
            "Content-type": "application/xml",
            "Accept": "application/xml"
        }
        print layername
        xml = "<layer><defaultStyle><name>{0}</name></defaultStyle><enabled>{1}</enabled></layer>".format(unicode(stylename).lower(),  unicode(str(enabled).upper()))
        cs_url = url(self.service_url, ["layers", layername])
        headers, response = self.http.request(cs_url, "PUT", xml, headers)
        print cs_url
        if headers.status == 200:
            # reload geoserver cluster
            self.reload_configuration_geoserver_slaves()
            return True
        else:
            print headers.status, " ", response
            return False

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
        shapefile.import_shapefile(datasource, input_shapefile, name )

        # publish shapefile
        self.publish_postgis_table(datasource, name)
        return "published"

    def publish_postgis_table(self, datasource, name):
        """
        :param datasource: datasource stored in geoserver
        :param name: name of the table in postgis
        :return:
        """
        #curl -v -u admin:geoserver -XPOST -H "Content-type: text/xml" -d "<featureType><name>buildings</name></featureType>"
        #http://localhost:8080/geoserver/rest/workspaces/acme/datasources/nyc/featuretypes
        headers = {
            "Content-type": "application/xml",
            "Accept": "application/xml"
        }
        xml = "<featureType><name>{0}</name></featureType>".format(unicode(name).lower())
        cs_url = url(self.service_url, ["workspaces", datasource['workspace'], "datasources", datasource['datasource'], 'featuretypes'])
        headers, response = self.http.request(cs_url, "POST", xml, headers)
        log.info(headers)
        if headers.status == 201:
            # reload geoserver cluster
            self.reload_configuration_geoserver_slaves()
            return True
        else:
            return False

    def checkIFdatasourceExist(self, name):
        print 'TODO'

    def get_default_workspace(self):
        return self.get('default_workspace')

    def get_default_datasource(self):
        default_datasource = self.config['default_datasource']
        print default_datasource
        datasource = self.config['datasources']
        for d in datasource:
            if (default_datasource in d['datasource']):
                return d
        return False

    def reload_configuration_geoserver_slaves(self, force_master_reload=False):
        geoserver_cluster = self.config["geoserver_slaves"]
        if (force_master_reload is True): geoserver_cluster.append(self.config["geoserver_master"])
        for geoserver in geoserver_cluster:
            cs_url =  url(geoserver, ["reload?recurse=true"])
            headers, response = self.http.request(cs_url, "POST")
            log.info(headers)
            if headers.status == 200:
                return True
            else:
                return False
