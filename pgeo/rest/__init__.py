from flask import Flask

from pgeo.rest.browse_modis import browse_modis
from pgeo.rest.download import download
from pgeo.rest.browse_trmm import browse_trmm
from pgeo.rest.schema import schema
from pgeo.rest.filesystem import filesystem


app = Flask(__name__)
app.register_blueprint(browse_modis, url_prefix='/browse/modis')
app.register_blueprint(browse_trmm, url_prefix='/browse/trmm')
app.register_blueprint(download, url_prefix='/download')
app.register_blueprint(schema, url_prefix='/schema')
app.register_blueprint(filesystem, url_prefix='/filesystem')