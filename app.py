from flask import Flask, send_from_directory, url_for, render_template, request, session

application = Flask(__name__, static_folder='templates/static')
application.config['SECRET_KEY'] = "its a secret!"

Session(application)

chat_history = []
username = "User"

def generate_response(msg=None):
    author = "Chatbot"
    text = "What?"
    return [author, text]

@application.route("/")
def index():
    if session["chat"] is None:
        session["chat"] = []
    #return render_template("index.html", chat=session["chat_history"])
    return render_template("index.html", chat=session["chat"])

@application.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        msg = [username, request.form["usermsg"]]
        #session["chat_history"].append(msg)
        session["chat"].append(msg)
        response = generate_response(msg)
        session["chat"].append(response)
    #return render_template("index.html", chat=session["chat_history"])
    return render_template("index.html", chat=session["chat"])

if __name__ == "__main__":
    application.run(host='0.0.0.0')
