from flask import Flask, send_from_directory, url_for, render_template, request, session
#from flask_session import Session
from flask_socketio import SocketIO, emit

import json as j
# for handling data and using api
from datetime import datetime
import requests as req
import pandas as pd
# for plots
import pygal
import base64

import string

# using for tests
import random
import re

from InputProcessor import InputProcessor

application = Flask(__name__, static_folder='templates/static')
application.config['DEBUG'] = True
application.config['SECRET_KEY'] = 'secret!'

#Session(application)

#chat_history = []
#username = "User"

socketio = SocketIO(application, cors_allowed_origins="*", async_mode=None, logger=True, engineio_logger=True)

country_slugs = {}

### RASA ###

def get_rasa_response(text):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data = {
        "sender" : "user",
        "message" : text
    }
    r = req.post("http://localhost:5005/webhooks/rest/webhook", data = j.dumps(data), headers = headers)
    responses = r.json()
    rasa = {
        'question': 'Huh?',
        'name': 'SCITalk',
        'code': '',
        'images': [],
        'relation': ''
    }
    for response in responses:
        if 'text' in response.keys():
            rasa['question'] = response['text']
        if 'image' in response.keys():
            if response['image'] != None:
                rasa['images'].append(response['image'])
                if rasa['question'] == 'Huh?':
                    rasa['question'] = ""
    return rasa

### Chatbot helper functions ###

# given a message from the user, generates and returns a response from Chatbot
def generate_response(msg, author):
    rasa = get_rasa_response(msg)
    #if rasa != None:
        #response['question'] = rasa
    return rasa

### COVID API ###

# https://api.covid19api.com/live/country/:country/status/:status/date/:date
# date format yyyy-mm-ddT00:00:00Z
# ?from=2020-03-01T00:00:00Z&to=2020-04-01T00:00:00Z
midnight = "T00:00:00Z"

# gets the current datetime formatted for use with the api
def get_datetime_now():
    now = datetime.now().strftime("%Y-%m-%d")
    return now

# returns a list of dicts of country slugs used in API calls
def get_country_slugs():
    r = req.get("https://api.covid19api.com/countries")
    data = r.json()
    return data

# returns a list of dictionaries, each with data about a country
def get_countries():
    data = get_summary()
    #print(data.keys(), flush=True)
    return data['Countries']

# gets daily summary, which contains new and total case data globally and for each country
# dict with keys "Global", "Countries", "Date", "Message"
def get_summary():
    r = req.get("https://api.covid19api.com/summary")
    data = r.json()
    return data

# gets data about a specific country
def get_country(country_name, countries=None):
    if countries == None:
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
            r_string += "&to=" + end_date + midnight
        else:
            r_string += "&to=" + get_datetime_now() + midnight
    r = req.get(r_string)
    data = r.json()
    return data

### Graphs and plots ###

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

# data is a list of dicts
def Pie (title, data, value_tag, label_tag): 
    pie_chart = pygal.Pie()
    pie_chart.title = title

    for category in data:
        data_num = []
        data_num.append(int(category[value_tag]))
        pie_chart.add(category[label_tag], data_num)
    return pie_chart.render_data_uri()

# not ready
## data format  category.(1,2).(2,2).(1,3):category2.(2,3).(2,3).(4,2).(4,2)
def Scatter(id,title,data):
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
def inputoutput(_json):
    print('User input received!', flush=True)
    text = _json['question']
    author = _json['name']
    response = generate_response(text, author)
    if response['question'].startswith("CMD "):
        command = response['question'].split(" ")[1]
        emit('command', command.strip())
    else:
        emit('response', response)

# receiving user feedback
@socketio.on('feedback')
def feedback(_json):
    print('User feedback received!', flush=True)
    timestamp = _json['date'].replace(":", "-")
    filename = "feedback/" + timestamp.replace(" ", "") + ".json"
    with open(filename, 'w') as file:
        j.dump(_json, file)
    emit('feedback_confirm')


# user connects, greet them
@socketio.on('connect')
def test_connect():
    print('Client connected', flush=True)
    
    response_string = "Hello, I'm SCITalk!"
    #response_string = "Hello, I'm Chatbot! Ask me about global COVID data. Currently, " + random_country['Country'] + " has " + str(random_country['TotalConfirmed']) + " confirmed cases of COVID-19."
    response = {
        'question': response_string,
        'name': 'SCITalk',
        'code': '',
        'images': [],
        'relation': ''
    }
    # TEST PYGAL
    # line chart
    #us_data = get_case_history("united-states", "confirmed", "2020-03-01")
    #linechart = Linechart("United States Confirmed Cases in March", [us_data], "Cases", "Country")
    #response['images'].append(linechart)
    # pie chart
    #countries = get_countries()
    #categories = []
    #for i in range(3):
    #    random_country = countries[random.randint(0, len(countries))]
    #    categories.append(random_country)
    #piechart = Pie("Total Deaths by Country", categories, "TotalDeaths", "Country")
    #response['images'].append(piechart)
    # send response
    emit('init_convo', [response])

# user disconnects
@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', flush=True)

if __name__ == '__main__':
    socketio.run(app)
