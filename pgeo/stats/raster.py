import os
import json
from osgeo import ogr
from pgeo.stats.db_stats import DBStats
from pgeo.utils import log
from pgeo.gis import raster
import io
import csv
import math

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
            json_stats["raster"]["path"] = self.get_raster_path(json_stats["raster"]["uid"])

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
            json_stats["raster"]["path"] = self.get_raster_path(json_stats["raster"]["uid"])
        return raster.get_statistics(json_stats["raster"]["path"])

    def get_histogram(self, json_stats):
        if "uid" in json_stats["raster"] and json_stats["raster"]["uid"] is not None:
            json_stats["raster"]["path"] = self.get_raster_path(json_stats["raster"]["uid"])
        return raster.get_histogram(json_stats["raster"]["path"], json_stats["stats"])

    def get_raster_path(self, uid):
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

        # parsing results
        # the column filter is used to parse the
        column_filter = vector_opt['column_filter']

        # get column filter index
        # TODO: make it dynamic
        column_filter_code_index = 0
        column_filter_label_index = 1

        srcnodatavalue = raster.get_nodata_value(raster_path)
        # log.info("SRC NODATA!: %s" % srcnodatavalue)

        # query DB
        codes = self.db_spatial.query(query)

        if codes:
            for r in codes:
                code = str(r[column_filter_code_index])
                label = str(r[column_filter_label_index])
                query_extent = "SELECT ST_AsGeoJSON(ST_Extent(geom)) FROM " + from_query + " WHERE " + column_filter + " IN (" + code + ")"
                query_layer = "SELECT * FROM " + from_query + " WHERE " + column_filter + " IN (" + code + ")"
                filepath = raster.crop_by_vector_database(raster_path, self.db_spatial, query_extent, query_layer)
                if filepath:
                    raster_stats = raster.get_statistics(filepath, raster_statistics)
                    if raster_stats:
                        obj = {"code": code, "label": label, "data": raster_stats}
                        stats.append(obj)
        return stats

    def get_location_values(self, input_layers, lat, lon, band=None):
        input_files = []
        for input_layer in input_layers:
            input_files.append(self.get_raster_path(input_layer))
        log.info(input_files)
        return raster.get_location_values(input_files, lat, lon, band)

    def _get_statistics(self):
        return None

    def create_csv_merge(self, output_file, stats1, stats2):
        # with open(output_file, 'wb') as csvfile:
            csv_file = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            json_string1 = json.dumps(stats1)
            json_string2 = json.dumps(stats2)
            # log.info(json_string1)
            # log.info(json_string2)
            json_data1 = json.loads(json_string1)
            json_data2 = json.loads(json_string2)
            # log.info(json_data1)
            # log.info(json_data2)
            csv_file.writerow(["code", "label", "valueX", "valueY"])
            for data1 in json_data1:
                #log.info(data1)
                for data2 in json_data2:
                    #log.info(data2)
                    try:
                        if data1["code"] == data2["code"]:
                            if "stats" in data1["data"]:
                                log.info(data2)
                                if not math.isnan(data1["data"]["stats"][0]["mean"]) and not math.isnan(data2["data"]["stats"][0]["mean"]):
                                    csv_file.writerow([data1["code"], data1["label"], data1["data"]["stats"][0]["mean"], data2["data"]["stats"][0]["mean"]])
                            pass
                    except Exception, e:
                        print e
            return output_file

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



