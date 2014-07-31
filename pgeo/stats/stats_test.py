from pgeo.stats.stats import Stats
from pgeo.config.settings import settings


layer = {
    # the stored UID in the GeoMetadata database
    "uid" : "modis:test_bella_guide3",
    }




#
# geostats = {
#     "code" : "226",
#     "query": "SELECT * FROM gaul0_3857 WHERE adm0_code IN ('226') ",
#     "statistics" : "all",
#     "save_stats" : True
#
# }
#

# geostats = {
#     "name" : "gaul0",
#     "query_condition" : {
#         "column_filter" : "adm0_code",
#         "select" : "distinct(adm0_code)",
#         "from"   : "gaul0_3857"
#     },
#     "save_stats" : True
# }

# geostats = {
#     "query_condition" : {
#         "column_filter" : "adm1_code",
#         "select" : "distinct(adm1_code)",
#         "from"   : "gaul1_3857",
#         "where"  : "adm0_code IN ('226')"
#     },
#     "save_stats" : True
# }
#
# geostats = {
#     "name" : "gaul1_new",
#     "query_condition" : {
#         "column_filter" : "adm1_code",
#         "select" : "adm1_code, adm1_name ",
#         "from"   : "gaul1_3857",
#         "where"  : "adm0_code IN ('150') GROUP BY adm1_code, adm1_name "
#     },
#     "save_stats" : True
# }


# REST
geostats = {
    "statlayercode" : "gaul1",
    "query_condition" : {
        "column_filter" : "adm1_code",
        "select" : "adm1_code, adm1_name ",
        "from"   : "gaul1_3857",
        "where"  : "adm0_code IN ('68') GROUP BY adm1_code, adm1_name "
    },
    "save_stats" : True
}


#New Geometadata Processing
json_stats = {
    "raster" : {
        "name" : "MODISQ13",

        # the stored UID in the GeoMetadata database (uses Geoserver Path (?) )
        "uid" : "trmm:3B42RT.2014010100.7.03hr",

        # OR instead of the uid directly gives the path of the source layer without using the Default Path
        "path" : "/hove/Desktop/GIS/layer.geojson",
        },

    "vector" : {
        "name" : "gaul0",

        # Database
        "type" : "database",
        "options" : {
            "query_condition" : {
                "column_filter" : "adm1_code",
                "select": "adm0_code, adm0_name",
                "from": "{{SCHEMA}}g2008_0",
                "where": "adm0_code IN ('68') GROUP BY adm0_code, adm0_name "
            },
            "stats_columns" : {
                "polygon_id" : "adm1_code",
                "label_en" : "adm1_name",
            }
        },

        # TODO: GeoJson (Problem how to save the geojson fields? Just gives back the result without saving them)
        "type" : "geojson",
        "path" : "/hove/Desktop/GIS/layer.geojson",
        },

    "stats" : {
        # default is false (return just the json with the statistics)
        "save_stats" : True,

        # dynamically retrieved by the raster and vector names
        "table_name" : "raster.name_vector.name",

        # table.sql contains Default CREATE TABLE
        "table_definition" : "$GEOMETADATA_DEFAULT_PATH/GAUL0/table.sql",

        "table_insert": {
            # Table fiels to be used at runtime during the insertion
            # INSERT INTO table_name (polygon_id, label_en ..) VALUES (1, "Afghanistan, ..)

            "polygon_id" :  "",
            "label_en" : "",
            "fromdate" : "",
            "todate"   : "",
            "dekad" : "",
            "hist" : "",
            "max" : "",
            "min" : "",
            "sd": ""
        },

        # SQL containing INDEXES
        "table_indexes" : "$GEOMETADATA_DEFAULT_PATH/GAUL0/table_indexes.sql",

        #  default option
        "delete_tmp_files" : True
    }
}




# geostats = {
#     "name" : "gaul2",
#     "geojson" : {"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[43.0224609375,2.3943223575350774],[43.0224609375,3.623071326235699],[44.60449218749999,3.623071326235699],[44.60449218749999,2.3943223575350774],[43.0224609375,2.3943223575350774]]]}},{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[46.07666015625,5.397273407690917],[46.38427734375,8.711358875426512],[50.25146484375,8.798225459016358],[46.73583984375,4.937724274302492],[46.07666015625,5.397273407690917]]]}},{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[42.9345703125,5.878332109674327],[44.12109374999999,8.928487062665504],[44.89013671875,7.079088026071731],[43.70361328125,4.806364708499998],[42.9345703125,5.878332109674327]]]}}]},
#     "save_stats" : False
# }

geostats = Stats(settings)
geostats.zonalstats(json_stats)
