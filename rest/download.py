from flask import Blueprint

download = Blueprint('download', __name__)

@download.route('/download')
def index():
    return 'Welcome to the Browse module!'

@download.route('/download/<user_name>')
def name(user_name):
    return 'Welcome to the Download module, ' + user_name + '!'