from pgeo.utils.log import logger

log = logger("pgeo.metadata.metadata_bridge")


def translate_from_metadata_to_geoserver(metadata_json, file_path=None):
    geoserver_json = {
        #"name" : ""
        "title" : "",
        "abstract" : "",
        "enabled" : True,
        # "workspace" : "fenix",
        # "datastore" : "pgeo",
        "defaultStyle":{
        }
    }
    try:
        log.info(metadata_json)
        l = metadata_json["uid"].split(":")
        if len(l) > 1:
            geoserver_json["name"] = l[1]
            geoserver_json["workspace"] = l[0]
        else:
            log.error("there isn't a workspace associated to the uid of the layer %s" % l[0])
            geoserver_json["name"] = l[0]
    except Exception:
        pass
    try:
        geoserver_json["title"] = metadata_json["title"]["EN"]
    except Exception:
        pass
    try:
        geoserver_json["abstract"] = metadata_json["meContent"]["description"]["EN"]
    except Exception:
        pass
    try:
        print metadata_json["meSpatialRepresentation"]["seDefaultStyle"]["name"]
        geoserver_json["defaultStyle"] = {}
        geoserver_json["defaultStyle"]["name"] = metadata_json["meSpatialRepresentation"]["seDefaultStyle"]["name"]
    except Exception:
        pass

    if file_path is not None:
        geoserver_json["path"] = file_path

    return geoserver_json


def translate_from_geoserver_to_metadata(metadata_json):
    return "TODO:"

