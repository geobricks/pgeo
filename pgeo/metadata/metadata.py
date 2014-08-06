from pgeo.config.settings import read_template
from pgeo.utils.json import dict_merge_and_convert_dates


def merge_layer_metadata(template_name, data):
    """
        Merge user's data with the core metadata and the selected template
        @param template_name: Name of the template, e.g. 'modis'
        @param data: User data, in JSON format
        @return: Merged JSON
    """
    core_template = read_template('core')
    template = read_template(template_name)
    out = dict_merge_and_convert_dates(core_template, data)
    out = dict_merge_and_convert_dates(out, template)
    return out