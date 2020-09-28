from flask import Flask, send_from_directory, url_for

application = Flask(__name__, static_folder='static')

@application.route("/")
def index():
    #return "hello"
    return send_from_directory(application.static_folder, 'index.html')

if __name__ == "__main__":
    application.run(host='0.0.0.0')
