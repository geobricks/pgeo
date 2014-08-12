import os
import uuid
import zipfile
from pgeo.config.settings import settings
from pgeo.config.settings import read_config_file_json
from pgeo.utils import log
import shutil
from os.path import basename

log = log.logger("pgeo.utils.filesystem")

# temporary folder
folder_tmp = settings['folders']['tmp']


def create_tmp_filename(path='', extension=''):
    """
    Create the path for a tmp file and filename

    @type path: string
    @param path: path from the tmp folder
    @type extension: extension
    @param extension: i.e. .geotiff
    """
    if extension != '' and "." not in extension: extension = "." + extension
    return (os.path.join(folder_tmp, path) + str(uuid.uuid4()) + extension).encode('utf-8')

def create_tmp_folder(path=''):
    """
    Create the tmp folder from the folder_tmp

    @type path: string
    @param path: path from the tmp folder
    @return: the path to a tmp folder
    """
    return (os.path.join(folder_tmp, path) + str(uuid.uuid4())).encode('utf-8')

def create_tmp_file(string_value, path='', extension=''):
    """
    Create a tmp file with the passed string

    @type string_value: string
    @param string_value: string to fill the tmp file
    @type path: string
    @param path: path from the tmp folder
    @type extension: extension
    @param extension: i.e. .geotiff
    """
    filename = create_tmp_filename(path, extension)
    text_file = open(filename, "w")
    text_file.write(str(string_value))
    text_file.close()
    return filename


def unzip(filezip, path=create_tmp_folder()):
    """
    Unzip a file in the tmp folder

    @type filezip: string
    @param filezip: path to the zip file
    @type path: string
    @param path: path from the tmp folder
    @return: path to the unzipped folder
    """
    path = os.path.join(folder_tmp, path)
    log.info(path)
    with zipfile.ZipFile(filezip, "r") as z:
        z.extractall(path)
    return path


def remove(filepath):
    """
    Remove a file

    @type filepath: string
    @param filepath: path to the file
    @type path: string
    @param path: path from the tmp folder
    """
    try:
        os.remove(filepath)
    except:
        log.warn("file doesn't exists: " + str(filepath))


def remove_folder(path):
    """
    Remove a folder
    @param path: path to the folder
    @type path: string
    """
    try:
        shutil.rmtree(path, ignore_errors=True)
    except Exception, e:
        log.error(e)


def get_filename(filepath, extension=False):
    drive, path = os.path.splitdrive(filepath)
    path, filename = os.path.split(path)
    name = os.path.splitext(filename)[0]
    if extension is True:
        return path, filename, name
    else:
        return name


def zip_files(name, files, path=folder_tmp):
    zip_path = os.path.join(path, name +".zip")
    log.info("Zip: '%s' from zip_files %s - %s" % (zip_path, name, files))
    zf = zipfile.ZipFile(zip_path, "w")
    zip_subdir = path
    for fpath in files:
        fdir, fname = os.path.split(fpath)

        #Add file, at correct path
        log.info(fname)
        zf.write(fpath, fname)
    zf.close()
    return zip_path


def create_filesystem(source, parameters):
    """
    Create the filesystem structure according to the configuration file.

    @type source: string
    @param source: e.g. 'modis'
    @type parameters: dictionary
    @param parameters: e.g. {'product': 'MOD13Q1', 'year': '2014', 'day': '033'}
    """
    conf = read_config_file_json(source, 'data_providers')['target']
    if not os.path.exists(conf['target_dir']):
        os.makedirs(conf['target_dir'])
    if len(conf['folders']) > 0:
        for folder in conf['folders']:
            create_folder(conf, parameters, folder, conf['target_dir'])


def create_folder(conf, parameters, folder, root_folder):
    """
    Recursive function to create sub-folders.

    @type conf: dictionary
    @param conf: Data provider's configuration
    @type parameters: dictionary
    @param parameters: e.g. {'product': 'MOD13Q1', 'year': '2014', 'day': '033'}
    @type folder: dictionary
    @param folder: Dictionary describing the folder and its sub-folders, if any
    @type root_folder: string
    @param root_folder: Folders will be creating from this one
    """
    folder_name = folder['folder_name']
    if '{{' in folder_name and '}}' in folder_name:
        for key in parameters:
            if folder['folder_name'] == '{{' + key + '}}':
                folder_name = folder['folder_name'].replace('{{' + key + '}}', parameters[key])
    directory = os.path.join(root_folder, folder_name)
    if not os.path.exists(directory):
        os.makedirs(directory)
    if 'folders' in folder and len(folder['folders']) > 0:
        for sub_folder in folder['folders']:
            create_folder(conf, parameters, sub_folder, directory)