from flask import Blueprint

download = Blueprint('download', __name__)

@download.route('/')
def index():
    return 'Welcome to the Browse module!'

@download.route('/<user_name>')
def name(user_name):
    return 'Welcome to the Download module, ' + user_name + '!'