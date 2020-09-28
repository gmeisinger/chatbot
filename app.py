from flask import Flask

application = Flask(__name__)

@application.route("/")
def default():
    return "Hello World!"

if __name__ == "__main__":
    application.run(host='0.0.0.0')