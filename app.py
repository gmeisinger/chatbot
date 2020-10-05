from flask import Flask, send_from_directory, url_for, render_template, request, session
#from flask_session import Session
from flask_socketio import SocketIO, emit

# for handling data and using api
import requests as req
import pandas as pd
# for plots
import pygal

import string

# using for tests
import random

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
    return stripped


def hello(msg):
  if "hello" in msg:
    return "Hello, how can I help you?"
  else:
    return "What?"

### COVID API ###

# returns a list of dictionaries, each with data about a country
def get_countries():
    r = req.get("https://api.covid19api.com/summary")
    data = r.json()
    return data['Countries']

# gets data about a specific country
def get_country(country_name):
    countries = get_countries()
    data = next((item for item in countries if item["Country"] == country_name), None)
    return data

### Graphs and plots ###

# going to use the same code from the old repo, using pygal
# data format Category1,1,2,3,4,5:Category2,2,3,4,6,6,7,3,4,2:Category3,2,3,4,5,2,3,4
def Linechart(id, title, data):
    line_chart = pygal.Line()
    line_chart.title = title

    data_cols = data.split(':')
    for x in range(0, len(data_cols)):
        data_num = []
        data_cols_split = data_cols[x].split(',')

        for y in range(1, len(data_cols_split)):
            print(data_cols_split[y])
            data_num.append(int(data_cols_split[y]))

            print(data_num)
        line_chart.add(str(data_cols_split[0]), data_num)

    line_chart.render_to_png('linechart.png')

    with open("linechart.png", "rb") as imageFile:
        imgstring = base64.b64encode(imageFile.read())
    return imgstring

def Pie (id,title,data): ##data format Category1,25:Category2,75
    pie_chart = pygal.Pie()
    pie_chart.title = title

    data_cols = data.split(':')
    for x in range(0,len(data_cols)):
        data_num = []
        data_cols_split = data_cols[x].split(',')


        for y in range(1,len(data_cols_split)):
            print(data_cols_split[y])
            data_num.append(int(data_cols_split[y]))

            print(data_num)
        pie_chart.add(str(data_cols_split[0]), data_num)
    pie_chart.render_to_png('pie.png')

    with open("pie.png", "rb") as imageFile:
        imgstring = base64.b64encode(imageFile.read())
    return imgstring

def Scatter(id,title,data): ## data format  category.(1,2).(2,2).(1,3):category2.(2,3).(2,3).(4,2).(4,2)
    scatter_chart = pygal.XY(stroke=False)
    scatter_chart.title = title
    data_cols = data.split(':')
    for x in range(0,len(data_cols)):
        data_num = []
        data_cols_split = data_cols[x].split('.')

        for y in range(1,len(data_cols_split)):
            print(data_cols_split[y])
            data_num.append(data_cols_split[y])
        print(data_num)
        scatter_chart.add(str(data_cols_split[0]), [literal_eval(strtuple) for strtuple in data_num])

        scatter_chart.render_to_png('scatter.png')

    with open("scatter.png", "rb") as imageFile:
        imgstring = base64.b64encode(imageFile.read())
    return imgstring

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
    countries = get_countries()
    random_country = countries[random.randint(0, len(countries))]
    response_string = "Hello, I'm Chatbot! Ask me about global COVID data. Currently, " + random_country['Country'] + " has " + str(random_country['TotalConfirmed']) + " confirmed cases of COVID-19."
    response = {
        'question': response_string,
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
