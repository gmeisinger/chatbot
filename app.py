from flask import Flask, send_from_directory, url_for, render_template, request, session

application = Flask(__name__, static_folder='templates/static')
application.config['SECRET_KEY'] = "its a secret!"

chat_history = []
username = "User"

def generate_response(msg=None):
    author = "Chatbot"
    text = "What?"
    return [author, text]

@application.before_request
def before_request():
    if "chat_history" not in session:
        session["chat_history"] = []

@application.route("/")
def index():
    #return render_template("index.html", chat=session["chat_history"])
    return render_template("index.html", chat=chat_history)

@application.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        msg = [username, request.form["usermsg"]]
        #session["chat_history"].append(msg)
        chat_history.append(msg)
        response = generate_response(msg)
        chat_history.append(response)
    #return render_template("index.html", chat=session["chat_history"])
    return render_template("index.html", chat=chat_history)

if __name__ == "__main__":
    application.run(host='0.0.0.0')
