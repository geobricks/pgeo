from pgeo.config.settings import read_template
from copy import deepcopy


def merge_layer_metadata(template_name, data):
    template = read_template('core')
    out = dict(template, **data)
    test = dict_merge(template, data)
    return test


def dict_merge(a, b):
    '''
    Source: https://www.xormedia.com/recursively-merge-dictionaries-in-python/
    '''
    if not isinstance(b, dict):
        return b
    result = deepcopy(a)
    for k, v in b.iteritems():
        if k in result and isinstance(result[k], dict):
            result[k] = dict_merge(result[k], v)
        else:
            result[k] = deepcopy(v)
    return result