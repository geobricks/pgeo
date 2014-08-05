from pgeo.config.settings import read_template
from pgeo.utils.json import dict_merge


def merge_layer_metadata(template_name, data):
    core_template = read_template('core')
    template = read_template(template_name)
    out = dict_merge(core_template, data)
    out = dict_merge(out, template)
    return out