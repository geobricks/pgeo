from rest import app, config

if __name__ == '__main__':
    app.run(port=config.PORT, debug=config.DEBUG)