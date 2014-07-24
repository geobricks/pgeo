from flask import Flask
from browse import browse
from config import settings

app = Flask(__name__)
app.register_blueprint(browse)

config = settings