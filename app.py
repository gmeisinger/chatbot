from flask import Flask, send_from_directory, url_for, render_template, request, session
#from flask_session import Session
from flask_socketio import SocketIO, emit

import string

application = Flask(__name__, static_folder='templates/static')
application.config['DEBUG'] = True
application.config['SECRET_KEY'] = 'secret!'

#Session(application)

#chat_history = []
#username = "User"

socketio = SocketIO(application, cors_allowed_origins="*", async_mode=None, logger=True, engineio_logger=True)

### Chatbot helper functions ###

# given a message from the user, generates and returns a response from Chatbot
def generate_response(msg, author):
    # clean the text
    cleaned_text = clean_text(msg)
    # response template
    response = {
        'question': '',
        'name': 'Chatbot',
        'code': '',
        'images': [],
        'relation': ''
    }
    # find intent
    # generate response
    response['question'] = hello(msg)
    return response

# tokenizes and cleans text. returns a list of words
def clean_text(text):
    words = text.lower().split()
    table = str.maketrans('', '', string.punctuation)
    stripped = [w.translate(table) for w in words]
    print(stripped, flush=True)
    return stripped


def hello(msg):
  if "hello" in msg:
    return "Hello, how can I help you?"
  else:
    return "What?"

### Graphs and plots ###

# going to use the same code from the old repo, using pygal

### Flask and SocketIO routes below ###

# default route
@application.route("/")
def index():
    return render_template("index.html")

# receiving input from user in the form of an utterance
@socketio.on('sendout')
def inputoutput(json):
    print('User input received!', flush=True)
    text = json['question']
    author = json['name']
    response = generate_response(text, author)
    emit('response', response)

# user connects, greet them
@socketio.on('connect')
def test_connect():
    print('Client connected', flush=True)
    response = {
        'question': "Hello, I'm Chatbot! Ask me about COVID data.",
        'name': 'Chatbot',
        'code': '',
        'images': [],
        'relation': ''
    }
    emit('init_convo', [response])

# user disconnects
@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', flush=True)

if __name__ == '__main__':
    socketio.run(app)
