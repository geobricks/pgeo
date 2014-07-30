from flask import Flask
from browse_modis import browse_modis
from browse_trmm import browse_trmm
from download import download
from schema import schema

app = Flask(__name__)
app.register_blueprint(browse_modis, url_prefix='/browse/modis')
app.register_blueprint(browse_trmm, url_prefix='/browse/trmm')
app.register_blueprint(download, url_prefix='/download')
app.register_blueprint(schema, url_prefix='/schema')