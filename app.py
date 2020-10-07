from flask import Flask, send_from_directory, url_for, render_template, request, session
#from flask_session import Session
from flask_socketio import SocketIO, emit

# for handling data and using api
import requests as req
import pandas as pd
# for plots
import pygal
import base64

import string

# using for tests
import random

from InputProcessor import InputProcessor

application = Flask(__name__, static_folder='templates/static')
application.config['DEBUG'] = True
application.config['SECRET_KEY'] = 'secret!'

#Session(application)

#chat_history = []
#username = "User"

socketio = SocketIO(application, cors_allowed_origins="*", async_mode=None, logger=True, engineio_logger=True)

country_slugs = {}

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
    in_proc = InputProcessor(cleaned_text)
    
    # generate response
    response['question'] = in_proc.process()
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

# https://api.covid19api.com/live/country/:country/status/:status/date/:date
# date format yyyy-mm-ddT00:00:00Z
# ?from=2020-03-01T00:00:00Z&to=2020-04-01T00:00:00Z
midnight = "T00:00:00Z"

# returns a list of country slugs used in API calls
def get_country_slugs():
    r = req.get("https://api.covid19api.com/countries")
    data = r.json()
    return data

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

# returns daily case data for a country from the first case onward
# country must be a valid country slug
# case type can be confirmed, recovered, deaths
def get_case_history(country, case_type="confirmed", start_date=None, end_date=None):
    r_string = "https://api.covid19api.com/total/country/" + country + "/status/" + case_type
    if start_date != None and type(start_date) is str:
        r_string +=  "?from=" + start_date + midnight
        if end_date != None and type(end_date) is str:
            r_string += "&to=" + start_date + midnight
    print("r-string: " + r_string, flush=True)
    print("https://api.covid19api.com/total/country/united-states/status/deaths?from=2020-03-01T00:00:00Z&to=2020-04-01T00:00:00Z" == r_string, flush=True)
    r = req.get(r_string)
    data = r.json()
    return data

### Graphs and plots ###

def test_image():
    with open("test_image.png", "rb") as imageFile:
        imgstring = base64.b64encode(imageFile.read())
    return imgstring

# going to use the same code from the old repo, using pygal
# data is formatted as a list of dictionaries, with value_tag and label_tag as keys
# each dictionary 
def Linechart(title, data, value_tag, label_tag):
    line_chart = pygal.Line()
    line_chart.title = title

    # changes
    for category in data:
        data_num = []
        for entry in category:
            data_num.append(int(entry[value_tag]))
        line_chart.add(str(category[0][label_tag]), data_num)

    return line_chart.render_data_uri()

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
    return pie_chart.render_data_uri()

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

        return scatter_chart.render_data_uri()

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
    # init country list
    #country_slugs = get_country_slugs()
    # test greeting
    countries = get_countries()
    random_country = countries[random.randint(0, len(countries))]
    response_string = "Hello, I'm Chatbot! Ask me about global COVID data."
    #response_string = "Hello, I'm Chatbot! Ask me about global COVID data. Currently, " + random_country['Country'] + " has " + str(random_country['TotalConfirmed']) + " confirmed cases of COVID-19."
    response = {
        'question': response_string,
        'name': 'SCITalk',
        'code': '',
        'images': [],
        'relation': ''
    }
    # TEST PYGAL
    us_data = get_case_history("united-states", "confirmed", "2020-03-01", "2020-04-01")
    print(len(us_data), flush=True)
    linechart = Linechart("United States Confirmed Cases in March", [us_data], "Cases", "Country")
    #tester = test_image()
    #response['question'] += str(len(us_data))
    response['images'].append(linechart)
    emit('init_convo', [response])

# user disconnects
@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', flush=True)

if __name__ == '__main__':
    socketio.run(app)
