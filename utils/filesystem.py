import os
import uuid
import zipfile
from config import settings

# temporary folder
folder_tmp = settings.folders['tmp']


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



