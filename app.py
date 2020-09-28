from flask import Flask, send_from_directory, url_for, render_template, request

application = Flask(__name__, static_folder='templates/static')

chat_history = []
username = "User"

@application.route("/")
def index():
    #return "hello"
    return render_template("index.html")

@application.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        msg = [username, request.form["usermsg"]]
        chat_history.append(msg)
        return render_template("index.html", chat=chat_history)
    else:
        return render_template("index.html")

if __name__ == "__main__":
    application.run(host='0.0.0.0')
