import os
import uuid
import zipfile
from pgeo.config.settings import settings
from pgeo.config.settings import read_config_file_json

# temporary folder
folder_tmp = settings['folders']['tmp']


def create_tmp_filename(prefix='', extension=''):
    # the utf-8 encoding it's used to create a new .tif
    return (folder_tmp + '/' + prefix + str(uuid.uuid4()) + extension).encode('utf-8')

def create_tmp_file(string_value, prefix='', extension=''):
    filename = create_tmp_filename(prefix, extension)
    text_file = open(filename, "w")
    text_file.write(str(string_value))
    text_file.close()
    return filename

def unzip(filezip, prefix='', extension=''):
    path = folder_tmp
    with zipfile.ZipFile(filezip, "r") as z:
        z.extractall(path)
    return path

def remove(file):
    os.remove(file)


def create_filesystem(source, parameters):
    """
        :param source: e.g. 'modis'
        :param parameters: This is a map of keys to be changed in the configuration file with actual values,
         e.g. {'product': 'MOD13Q1', 'year': '2014', 'day': '033'}
        :return: None
    """
    conf = read_config_file_json(source, 'data_providers')['target']
    if not os.path.exists(conf['target_dir']):
        os.makedirs(conf['target_dir'])
    if len(conf['folders']) > 0:
        for folder in conf['folders']:
            create_folder(conf, parameters, folder, conf['target_dir'])


def create_folder(conf, parameters, folder, root_folder):
    folder_name = folder['folder_name']
    if '{' in folder_name and '}' in folder_name:
        for key in parameters:
            if folder['folder_name'] == '{' + key + '}':
                folder_name = folder['folder_name'].replace('{' + key + '}', parameters[key])
    directory = os.path.join(root_folder, folder_name)
    if not os.path.exists(directory):
        os.makedirs(directory)
    if 'folders' in folder and len(folder['folders']) > 0:
        for sub_folder in folder['folders']:
            create_folder(conf, parameters, sub_folder, directory)
