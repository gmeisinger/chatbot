from flask import Flask, send_from_directory, url_for, render_template, request, session

application = Flask(__name__, static_folder='templates/static')
app.config['SECRET_KEY'] = "its a secret!"

username = "User"
session["chat_history"] = []

@application.route("/")
def index():
    return render_template("index.html", chat=session["chat_history"])

@application.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        msg = [username, request.form["usermsg"]]
        session["chat_history"].append(msg)
    return render_template("index.html", chat=session["chat_history"])

if __name__ == "__main__":
    application.run(host='0.0.0.0')
