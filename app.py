from flask import Flask, send_from_directory, url_for, render_template, request

application = Flask(__name__, static_folder='templates/static')

chat_history = []

# returns chat history as a string of html
def get_chat_history():
    ret = ""
    for entry in chat_history:
        html_str = '<div class="row"> <div class="col"><b>' + 'user' + ': </b>' + entry + '</div> </div>'
        ret += html_str
    return ret

@application.route("/")
def index():
    #return "hello"
    return render_template("index.html")

@application.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        msg = request.form["usermsg"]
        chat_history.append(msg)
        chat = get_chat_history()
        return render_template("index.html", msg=chat)
    else:
        return render_template("index.html")

if __name__ == "__main__":
    application.run(host='0.0.0.0')
