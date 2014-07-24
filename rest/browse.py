from flask import Blueprint

browse = Blueprint('browse', __name__)

@browse.route('/')
def index():
    return 'Welcome to the Browse module!'

@browse.route('/<user_name>')
def name(user_name):
    return 'Welcome to the Browse module, ' + user_name + '!'