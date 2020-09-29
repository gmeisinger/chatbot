from flask import Flask, send_from_directory, url_for, render_template, request, session
from flask_session import Session

application = Flask(__name__, static_folder='templates/static')
application.config['SESSION_TYPE'] = 'filesystem'
application.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

Session(application)

chat_history = []
username = "User"

def generate_response(msg):
    author = "Chatbot"
    text = hello(msg)
    return [author, text]

@application.route("/")
def index():
    if "chat" not in session:
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
	
def hello(msg):
  if "hello" in msg:
    return "Hello, how can I help you?"
  else:
    return "What?"

if __name__ == "__main__":
    application.run(host='0.0.0.0')
