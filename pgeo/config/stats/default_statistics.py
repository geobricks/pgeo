

config = {

    # "raster" : {
    #     "name" : "MODISQ13",
    #
    #     # the stored UID in the GeoMetadata database (uses Geoserver Path (?) )
    #     "uid" : "trmm:3B42RT.2014010100.7.03hr",
    #
    #     # OR instead of the uid directly gives the path of the source layer without using the Default Path
    #     #"path" : "/hove/Desktop/GIS/layer.geojson",
    # },
    #
    # "vector" : {
    #
    #     # It's the name of the gaul spatial table
    #     "name" : "gaul0",
    #
    #     # Database
    #     "type" : "database",
    #     "options" : {
    #
    #         # used to query the db and retrieve the right codes
    #         "query_condition" : {
    #             "select": "adm0_code, adm0_name",
    #             "from": "{{SCHEMA}}.gaul0",
    #             "where": "adm0_code IN ('68', '69') GROUP BY adm0_code, adm0_name ",
    #             },
    #
    #         # used to subquery the db to get the geometry and process the raster
    #         "column_filter": "adm0_code",
    #
    #         # used to fill stats table (raster["name"].vector["name"])
    #         "stats_columns" : {
    #             "polygon_id" : "adm0_code",
    #             "label_en" : "adm0_name",
    #             }
    #     },
    #
    #     # TODO: GeoJson (Problem how to save the geojson fields? Just gives back the result without saving them)
    #     # "type" : "geojson",
    #     # "path" : "/hove/Desktop/GIS/layer.geojson",
    # },
    #
    # "stats" : {
    #     # default is false (return just the json with the statistics)
    #     "save_stats" : True,
    #
    #     # dynamically retrieved by the raster and vector names
    #     "table_name" : "raster.name_vector.name",
    #
    #     # table.sql contains Default CREATE TABLE
    #     "table_definition" : "$GEOMETADATA_DEFAULT_PATH/GAUL0/table.sql",
    #
    #     "table_insert": {
    #         # Table fiels to be used at runtime during the insertion
    #         # INSERT INTO table_name (polygon_id, label_en ..) VALUES (1, "Afghanistan, ..)
    #
    #         "polygon_id" :  "",
    #         "label_en" : "",
    #         "fromdate" : "",
    #         "todate"   : "",
    #         "dekad" : "",
    #         "hist" : "",
    #         "max" : "",
    #         "min" : "",
    #         "sd": ""
    #     },
    #
    #     # SQL containing INDEXES
    #     "table_indexes" : "$GEOMETADATA_DEFAULT_PATH/GAUL0/table_indexes.sql",
    #
    #     #  default option
    #     "delete_tmp_files" : True
    # }

}