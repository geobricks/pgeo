import os
import json
from pgeo.stats.db_stats import DBStats
from pgeo.utils import log
from pgeo.gis import raster

log = log.logger(__name__)

class Stats():

    # default settings
    settings = None
    db_stats = None
    db_spatial = None

    def __init__(self, settings=None):

        self.settings = settings

        # db_stats will connect to the database
        self.db_stats = self._get_default_db("stats", True)

        # db_stats will NOT connect to the database
        self.db_spatial = self._get_default_db("spatial", True)

    def zonal_stats(self, json_stats):
        stats = None
        # TODO: a common zonalstats
        '''
        :param json_stats: json with statistics definitions
        :return: json with response
        '''

        # Raster
        # if the raster is a raster store in the datadir
        if "uid" in json_stats["raster"]:
            json_stats["raster"]["path"] = self._get_raster_path(json_stats["raster"]["uid"])

        # Vector
        # TODO: make an ENUM somewhere (i.e. database, geojson, etc)
        #log.info(json_stats["vector"]["type"])
        if json_stats["vector"]["type"] == "database":
            stats = self._zonal_stats_by_vector_database(json_stats)
        elif json_stats["vector"]["type"] == "geojson":
            log.warn("TODO: Geojson statistics")

        # Stats
        # TODO: save stats in case is needed or return statistics
        return stats

    def get_stats(self, json_stats):
        if "uid" in json_stats["raster"]:
            json_stats["raster"]["path"] = self._get_raster_path(json_stats["raster"]["uid"])
        return raster.get_statistics(json_stats["raster"]["path"])

    def get_histogram(self, json_stats):
        if "uid" in json_stats["raster"]:
            json_stats["raster"]["path"] = self._get_raster_path(json_stats["raster"]["uid"])
        return raster.get_histogram(json_stats["raster"]["path"], json_stats["stats"])

    def _get_raster_path(self, uid):
        l = uid.split(":")
        return os.path.join(self.settings["folders"]["geoserver_datadir"], "data",  l[0], l[1], l[1] + ".geotiff");

    def _zonal_stats_by_vector_database(self, json_stats):
        # Stats result
        stats = []

        # raster statistics
        raster_statistics = None if "raster_stats" not in json_stats["stats"] else json_stats["stats"]["raster_stats"]

        # Raster path
        #log.info(json_stats["raster"])
        raster_path = json_stats["raster"]["path"]

        # Query Options
        vector_opt = json_stats["vector"]["options"]

        # Change SCHEMA If exists
        opt = json.dumps(vector_opt)
        # TODO: how to handle it more clearly
        # TODO: the "." (dot) should be in the schema name?
        opt = opt.replace("{{SCHEMA}}", self.db_spatial.schema)
        vector_opt = json.loads(opt)

        # retrieve query values
        select = vector_opt['query_condition']['select']
        from_query = vector_opt['query_condition']['from']
        where = None
        if "where" in vector_opt['query_condition']:
            where = vector_opt['query_condition']['where']

        # build query
        query = "SELECT " + select + " FROM "+ from_query
        if ( where is not None):
            query += " WHERE " + where

        #log.info(query)

        # query DB
        codes = self.db_spatial.query(query)

        # parsing results
        # the column filter is used to parse the
        column_filter = vector_opt['column_filter']

        # get column filter index
        # TODO: make it dynamic
        column_filter_code_index = 0
        column_filter_label_index = 1

        if codes:
            for r in codes:

                code = str(r[column_filter_code_index])
                label = str(r[column_filter_label_index])
                # TODO: problems with query Strings and Integers (or whatever)
                stats_query = "SELECT * FROM " + from_query + " WHERE " + column_filter + " IN (" + code + ")"

                #stats.append(self._get_stats_query(query, str(r[0]), str(r[1]), self.geostats['save_stats']))
                #log.info(code)
                db_connection_string = self.db_spatial.get_connection_string(True);
                filepath = raster.crop_by_vector_database(raster_path, stats_query,db_connection_string)

                #log.info(filepath)
                if filepath:
                    raster_stats = raster.get_statistics(filepath, raster_statistics)
                    if raster_stats:
                        obj = {"code": code, "label": label, "data": raster_stats}
                        stats.append(obj)
        return stats


    def _get_statistics(self):
        return None

    # get the default db from the settings
    def _get_default_db(self, dtype, connect=True):
        try:
            if self.settings["stats"]:
                if self.settings["db"]:
                    db_id = self.settings["stats"]["db"][dtype]
                    db = self.settings["db"][db_id]
                    if connect:
                        return DBStats(db)
                    else:
                        return db
        except:
            log.warn("No db found")
            pass



