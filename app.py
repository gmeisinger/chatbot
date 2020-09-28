from flask import Flask, send_from_directory, url_for, render_template

application = Flask(__name__, static_folder='static')

@application.route("/")
def index():
    #return "hello"
    return render_template("index.html")

if __name__ == "__main__":
    application.run(host='0.0.0.0')
