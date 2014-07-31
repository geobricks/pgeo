'''
thanks to https://github.com/boundlessgeo/gsconfig/tree/master/src/geoserver for the inspiration
'''

import urllib
import urlparse
from tempfile import mkstemp
import urllib
from zipfile import ZipFile
import os

# TODO: remove the tmp directory to use a default filesystem path
# and clean it

def url(base, seg, query=None):
    """
    Create a URL from a list of path segments and an optional dict of query
    parameters.
    """
    def clean_segment(segment):
        """
        Cleans the segment and encodes to UTF-8 if the segment is unicode.
        """
        segment = segment.strip('/')
        if isinstance(segment, unicode):
            segment = segment.encode('utf-8')
        return segment

    seg = (urllib.quote(clean_segment(s)) for s in seg)
    if query is None or len(query) == 0:
        query_string = ''
    else:
        query_string = "?" + urllib.urlencode(query)
    path = '/'.join(seg) + query_string
    adjusted_base = base.rstrip('/') + '/'
    return urlparse.urljoin(adjusted_base, path)

def prepare_upload_bundle(name, data):
    """GeoServer's REST API uses ZIP archives as containers for file formats such
    as Shapefile and WorldImage which include several 'boxcar' files alongside
    the main data.  In such archives, GeoServer assumes that all of the relevant
    files will have the same base name and appropriate extensions, and live in
    the root of the ZIP archive.  This method produces a zip file that matches
    these expectations, based on a basename, and a dict of extensions to paths or
    file-like objects. The client code is responsible for deleting the zip
    archive when it's done."""
    fd, path = mkstemp()
    zip_file = ZipFile(path, 'w')
    print zip_file
    for ext, stream in data.iteritems():
        fname = "%s.%s" % (name, ext)
        print fname
        if (isinstance(stream, basestring)):
            zip_file.write(stream, fname)
        else:
            zip_file.writestr(fname, stream.read())
    zip_file.close()
    os.close(fd)
    return path