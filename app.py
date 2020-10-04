from flask import Flask, send_from_directory, url_for, render_template, request, session
#from flask_session import Session
from flask_socketio import SocketIO, emit

from random import random
from time import sleep
from threading import Thread, Event


application = Flask(__name__, static_folder='templates/static')
application.config['DEBUG'] = True
application.config['SECRET_KEY'] = 'secret!'

#Session(application)

#chat_history = []
#username = "User"

socketio = SocketIO(application, cors_allowed_origins="*", async_mode=None, logger=True, engineio_logger=True)

def generate_response(msg, author):
    response = {
        'question': '',
        'name': 'Chatbot',
        'code': '',
        'images': [],
        'relation': ''
    }
    response['question'] = hello(msg)
    return response

def hello(msg):
  if "hello" in msg:
    return "Hello, how can I help you?"
  else:
    return "What?"

@application.route("/")
def index():
    return render_template("index.html")

@socketio.on('sendout')
def inputoutput(json):
    print('User input received!', flush=True)
    text = json['question']
    author = json['name']
    response = generate_response(text, author)
    emit('response', response)

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


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', flush=True)

if __name__ == '__main__':
    socketio.run(app)
