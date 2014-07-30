from config import settings
from geoserver.geoserver import Geoserver
from metadata.metadata import Metadata
from stats import stats

class Publish():

    metadata = Metadata(settings.metadata)
    geoserver = Geoserver(settings.geoserver)
    spatial_db = Geoserver(settings.geoserver)

    def __init__(self):
        return None

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
