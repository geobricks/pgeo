from flask import Flask
from browse import browse
from download import download
from config import settings

app = Flask(__name__)
app.register_blueprint(browse)
app.register_blueprint(download)

config = settings