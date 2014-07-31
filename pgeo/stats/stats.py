import os
from pgeo.stats.db_stats import DBStats
from pgeo.utils import log

# Logger
log = log.logger(__name__)

log.info("No db found")
log.warn("No db found")

class Stats():

    # default settings
    settings = None
    db_stats = None
    db_spatial = None

    def __init__(self, settings=None):

        self.settings = settings

        # db_stats will connect to the database
        self.db_stats = self.get_default_db("stats", True)

        # db_stats will NOT connect to the database
        self.db_spatial = self.get_default_db("spatial", False)

    def zonalstats(self, json_stats):
        # TODO: a common zonalstats
        '''
        :param json_stats: json with statistics definitions
        :return:
        '''

        # Raster
        # if the raster is a raster store in the datadir
        if json_stats["raster"]["uid"]:
            l = json_stats["raster"]["uid"].split(":")
            json_stats["raster"] = os.path.join(self.settings["folders"]["geoserver_datadir"],"data",  l[0], l[1], l[1] + ".geotiff");

        # Vector
        # TODO: make an ENUM somewhere (i.e. database, geojson, etc)
        if json_stats["vector"]["type"] == "database":
            self._zonalstats_raster_database(json_stats)


        return None

    def _zonalstats_raster_database(self, json_stats):
        log.info("_zonalstats_raster_database")

        raster = json_stats["raster"]
        vector = json_stats["vector"]
        stats = json_stats["stats"]



        return None


    # get the default db from the settings
    def get_default_db(self, type, connect=True):
        try:
            if self.settings["stats"]:
                if self.settings["db"]:
                    db_id = self.settings["stats"]["db"][type]
                    db = self.settings["db"][db_id]
                    if connect:
                        return DBStats(db)
                    else:
                        return db
        except:
            log.warn("No db found")
            pass



