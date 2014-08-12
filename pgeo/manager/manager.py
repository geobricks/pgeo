from pgeo.geoserver.geoserver import Geoserver
from pgeo.metadata.metadata import Metadata


class Layer():


    def __init__(self, config):

        #
        self.metadata = Metadata(config["db"]["metadata"])
        self.geoserver = Geoserver(config["geoserver"])
        self.spatial_db = Geoserver(config["geoserver"])


    def publish(self):
        return None

    def publish_shapefile(self):
        # TODO: import shapefile on db
        # TODO: publish metadata
        # TODO: publish geoserver
        return None

    def publish_coverage(self):
        return None

    def delete(self):
        return None

    def rollback(self):
        # TODO: implement something if metadata or geoserver fails to publish or delete
        return None


from pgeo.config.settings import settings
metadata = Layer(settings)

print metadata
