from copy import deepcopy
from dateutil import parser


def dict_merge(a, b):
    """
    Source: https://www.xormedia.com/recursively-merge-dictionaries-in-python/
    """
    if not isinstance(b, dict):
        return b
    result = deepcopy(a)
    for k, v in b.iteritems():
        if k in result and isinstance(result[k], dict):
            result[k] = dict_merge(result[k], v)
        else:
            result[k] = deepcopy(v)
    return result


def dict_merge_and_convert_dates(a, b):
    """
    This function has been modified from the original one
    (https://www.xormedia.com/recursively-merge-dictionaries-in-python/) to convert dates
    for MongoDB insert.
    """
    if not isinstance(b, dict):
        return b
    result = deepcopy(a)
    for k, v in b.iteritems():
        if k in result and isinstance(result[k], dict):
            result[k] = dict_merge_and_convert_dates(result[k], v)
        else:
            result[k] = deepcopy(v)
            if 'version' not in k:
                try:
                    result[k] = parser.parse(result[k])
                except Exception:
                    pass
    return result