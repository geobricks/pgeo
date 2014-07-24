from flask import Flask
from browse import browse
from download import download
from config import settings

app = Flask(__name__)
app.register_blueprint(browse, url_prefix='/browse')
app.register_blueprint(download, url_prefix='/download')

@app.route('/')
def root():
    return 'Welcome to p-geo!'

config = settings