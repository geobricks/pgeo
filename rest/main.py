from rest import app, config

@app.route('/')
def root():
    return 'Welcome to p-geo!'

if __name__ == '__main__':
    app.run(port=config.PORT, debug=config.DEBUG)