# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction, EventType, Restarted
from rasa_sdk import FormValidationAction
from rasa_sdk.types import DomainDict


from typing import Any, Text, Dict, List, Union
from datetime import date

import requests
import json
import pygal

import os

# resets slot values
class ActionForgetSlots(Action):

    def name(self):
        return "action_forget_slots"
    
    def run(self, dispatcher, tracker, domain):
        countries = SlotSet("countries", None)
        scope = SlotSet("scope", None)
        case_type = SlotSet("case_type", None)
        return [countries, scope, case_type]

# clear chat
class ActionClearChat(Action):

    def name(self):
        return "action_clear_chat"
    
    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="CMD clear")
        return []

# reset bot
class ActionResetBot(Action):

    def name(self):
        return "action_reset_bot"
    
    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="Okay, let's start over.")
        return [Restarted()]

# this action gets a case count for a specific country.
# case types are (Confirmed, Recovered, Deaths)
# scope is (Total, New)
# country needs to be a slug
class ActionCaseCount(Action):

    @staticmethod
    def required_fields():
        return [
            #EntityFormField("scope", "scope"),
            #EntityFormField("case_type", "case_type"),
            EntityFormField("countries", "countries")
        ]

    def name(self):
        return "action_case_count"
    
    def run(self, dispatcher, tracker, domain):
        # get data
        scope = tracker.get_slot('scope')
        if scope == None:
            scope = "total"
        case_type = tracker.get_slot('case_type')
        if case_type == None:
            case_type = "confirmed"
        country = tracker.get_slot('countries')
        # get data from api
        r = requests.get("https://api.covid19api.com/summary")
        summary = r.json()
        # target a country
        countries = summary['Countries']
        if country == None:
            data = summary['Global']
            key_string = scope.capitalize() + case_type.capitalize()
            count = data[key_string]
            # report the information
            response = "There are " + str(count) + " " + scope + " " + case_type + " cases globally."
            if case_type == "deaths":
                response.replace("cases ", "")
            dispatcher.utter_message(text=response)
        elif len(country) == 1:
            country = country[0].lower()
            data = next((item for item in countries if (item['Slug'] == country or item['Country'].lower() == country)), None)
            key_string = scope.capitalize() + case_type.capitalize()
            count = data[key_string]
            # report the information
            response = "There are " + str(count) + " " + scope + " " + case_type + " cases in " + country + "."
            if case_type == "deaths":
                response.replace("cases ", "")
            dispatcher.utter_message(text=response)
        else:
            text = "There are "
            for x in country:
                data = next((item for item in countries if (item['Slug'] == x.lower() or item['Country'].lower() == x.lower())), None)
                key_string = scope.capitalize() + case_type.capitalize()
                text = text + str(data[key_string]) + " " + scope + " " + case_type + " in " + x
                if len(country) == 2 and country.index(x) != 1:
                    text = text + " and "
                elif len(country) == country.index(x) + 2:
                    text = text + ", and "
                elif len(country) == country.index(x) + 1:
                    text = text + "."
                else: 
                    text = text + ", "
            dispatcher.utter_message(text=text)
        #return [slot_scope, slot_case_type, slot_country, slot_count, evt]
        return []



class ActionCaseSummaryGraph(Action):
    @staticmethod
    def required_fields():
        return [
            EntityFormField("countries", "countries")
        ]

    def name(self):
        return "action_case_summary_graph"

    def Linechart(self, title, data, value_tag, label_tag, new):
        line_chart = pygal.Line()

        data_num = []


        if (new):
            num_entries = len(data)

            for i in range(num_entries):
                if i > 0:
                    data[i]['newCases'] = int(data[i]['Cases']) - int(data[i-1]['Cases'])
                else:
                    data[i]['newCases'] = int(data[i]['Cases'])

                data_num.append(data[i]['newCases'])

            title = 'New ' + title
        
        else:
            for entry in data:
                #p = entry['Province']
                c = entry['Cases']
                data_num.append(int(c))
                #if p in data_num:
                #    data_num[p].append(int(c))
                #else:
                #    data_num[p] = [int(c)]
        
        line_chart.title = title
        line_chart.add(data[0][label_tag], data_num)
        if '' in data_num:
           line_chart.add(str(data[0]['Country']), data_num[''])
        
        #for province in data_num:
        #    if province == '':
        #        continue
        #    line_chart.add(province, data_num[province])
        #else:

        return line_chart.render_to_png()

    def run(self, dispatcher, tracker, domain):
        case_type = tracker.get_slot('case_type')
        if case_type == None:
            case_type = "confirmed"

        countries_slot = tracker.get_slot('countries')
        scope = tracker.get_slot('scope')

        newCases = False
        if scope == 'new':
            newCases = True

        if countries_slot == None:
            return []

        country = str(countries_slot[0])

        # get data from api
        r = requests.get("https://api.covid19api.com/summary")
        summary = r.json()
        # target a country
        countries = summary['Countries']
        if country == None:
            data = summary['Global']
        else:
            data = next((item for item in countries if (item['Slug'] == country or item['Country'] == country)), None)

        # extract slug
        slug = ""
        if data != None:
            slug = data['Slug']

        else:
            return []

        # preparing to query api for dayone data
        qstring = "https://api.covid19api.com/total/dayone/country/" + slug + "/status/" + case_type

        # get data from api
        r = requests.get(qstring)
        dayone = r.json()

        # build linechart
        title = ''
        vtag = 'Cases'
        ltag = 'Country'
        if case_type == 'deaths':
            title = 'Deaths in ' + data['Country']
            # vtag = 'deaths'
        else:
            title = case_type.capitalize() + ' Cases in ' + data['Country']
            # vtag = case_type
        
        linechart = self.Linechart(title, dayone, vtag, ltag, newCases)
        # write linechart out to temporary file
        jspath = 'images/graph.png'
        path = '/var/www/html/images/graph.png'
        if (os.path.exists(path)):
            os.remove(path)
        f = open(path, 'xb')
        f.write(linechart)
        f.close()

        # display graph
        dispatcher.utter_message(text="Here's the graph...", image=jspath)

        # countries_slot = SlotSet("countries", None)
        # scope = SlotSet("scope", None)
        # case_type = SlotSet("case_type", None)
        # return [countries_slot, scope, case_type]
        action_performed = SlotSet("action_performed", True)

        return [action_performed]

class ActionCaseCountByTimeMonth(Action):

    @staticmethod
    def required_fields():
        return [
            #EntityFormField("scope", "scope"),
            #EntityFormField("case_type", "case_type"),
            EntityFormField("countries", "countries")
        ]

    def name(self):
        return "action_case_count_by_time_month"
    
    def run(self, dispatcher, tracker, domain): 
        # get data
        scope = tracker.get_slot('scope')
        if scope == None:
            scope = "total"
        case_type = tracker.get_slot('case_type')
        if case_type == None:
            case_type = "confirmed"
        elif case_type == "recoveries":
            case_type = "recovered"
        countries = tracker.get_slot('countries')
        country = "world"
        if countries != None:
            country = countries[0]
        by_time = tracker.get_slot('bytime')
        if by_time == None:
            by_time = "month"
        text = ""
        r = ""
        counts = {}
        currentMonth = date.today().strftime("%m")
        if country == "world":
            text = "Sorry, but SCITalk cannot get global data over time because it would take too long to sum count totals for every country"
            # for x in range(1,13):
            #     counts[x] = 0
            # text = "Globally there have been "
            # r = requests.get("https://api.covid19api.com/countries")
            # summary = r.json()
            # for x in summary:
            #     country = x["Country"]
            #     r2 = requests.get("https://api.covid19api.com/country/" + country + "/status/" + case_type + "?from=2020-03-01T00:00:00Z&to=2020-" + currentMonth + "-01T00:00:00Z")
            #     summary2 = r2.json()
            #     m = 3
            #     for y in summary2:
            #         if int(y["Date"][5:7]) == m:
            #             m += 1
            #             counts[m] = counts[m] + y["Cases"]
            #     m = 1
            #     numM = len(counts)
            #     for x in counts:
            #         text = text + str(counts[x]) + " " + scope + " "
            #         if case_type == "recovered":
            #             text = text + "recoveries in "
            #         elif case_type == "confirmed":
            #             text = text + case_type + " cases in "
            #         else:
            #             text = text + case_type + " in "
            #         if x == 1:
            #             text = text + "January"
            #         elif x == 2:
            #             text = text + "February"
            #         elif x == 3:
            #             text = text + "March"
            #         elif x == 4:
            #             text = text + "April"
            #         elif x == 5:
            #             text = text + "May"
            #         elif x == 6:
            #             text = text + "June"
            #         elif x == 7:
            #             text = text + "July"
            #         elif x == 8:
            #             text = text + "August"
            #         elif x == 9:
            #             text = text + "September"
            #         elif x == 10:
            #             text = text + "October"
            #         elif x == 11:
            #             text = text + "November"
            #         else:
            #             text = text + "December"
                    
            #         if numM == m + 1:
            #             text = text + ", and "
            #         elif numM != m:
            #             text = text + ", "
            #         m += 1
            #     text = text + "."
        else:
            for c in countries:
                country = c
                text = text + "In " + country + " there have been "
                r = requests.get("https://api.covid19api.com/country/" + country + "/status/" + case_type + "?from=2020-03-01T00:00:00Z&to=2020-" + currentMonth + "-01T00:00:00Z")
                summary = r.json()
                m = 3
                if summary[1]["Province"] == "":
                    for x in summary:
                        if int(x["Date"][5:7]) == m:
                            m += 1
                            counts[m] = x["Cases"]
                else:
                    for x in range(m,int(currentMonth) + 1):
                        counts[x] = 0
                    for x in range(len(summary)):
                        if int(summary[x]["Date"][5:7]) == m and int(summary[x]["Date"][8:10]) == 1:
                            counts[m] += summary[x]["Cases"]
                        if x+1 != len(summary) and int(summary[x+1]["Date"][5:7]) != m:
                            m += 1
                m = 1
                numM = len(counts)
                for x in counts:
                    text = text + str(counts[x]) + " " + scope + " "
                    if case_type == "recovered":
                        text = text + "recoveries in "
                    elif case_type == "confirmed":
                        text = text + case_type + " cases in "
                    else:
                        text = text + case_type + " in "
                    if x == 1:
                        text = text + "January"
                    elif x == 2:
                        text = text + "February"
                    elif x == 3:
                        text = text + "March"
                    elif x == 4:
                        text = text + "April"
                    elif x == 5:
                        text = text + "May"
                    elif x == 6:
                        text = text + "June"
                    elif x == 7:
                        text = text + "July"
                    elif x == 8:
                        text = text + "August"
                    elif x == 9:
                        text = text + "September"
                    elif x == 10:
                        text = text + "October"
                    elif x == 11:
                        text = text + "November"
                    else:
                        text = text + "December"
                    
                    if numM == m + 1:
                        text = text + ", and "
                    elif numM != m:
                        text = text + ", "
                    m += 1
                text = text + "."
                if len(countries) > 1:
                    text = text + "\n\n"
        dispatcher.utter_message(text = text)
        return []

class ActionCaseCountByTimeDay(Action):

    @staticmethod
    def required_fields():
        return [
            #EntityFormField("scope", "scope"),
            #EntityFormField("case_type", "case_type"),
            EntityFormField("countries", "countries")
        ]

    def name(self):
        return "action_case_count_by_time_day"
    
    def run(self, dispatcher, tracker, domain): 
        # get data
        scope = tracker.get_slot('scope')
        if scope == None:
            scope = "total"
        case_type = tracker.get_slot('case_type')
        if case_type == None:
            case_type = "confirmed"
        countries = tracker.get_slot('countries')
        country = "world"
        if countries != None:
            country = countries[0]
        by_time = tracker.get_slot('bytime')
        if by_time == None:
            by_time = "day"
        by_sub_time = tracker.get_slot('bysubtime')
        if by_sub_time == None:
            by_sub_time = "january" 
        
        text = ""
        counts = {}
        month = ""
        day = ""
        if by_sub_time == "january":
            month = "01"
            day = "31"
        elif by_sub_time == "february":
            month = "02"
            day = "29"
        elif by_sub_time == "march":
            month = "03"
            day = "31"
        elif by_sub_time == "april":
            month = "04"
            day = "30"
        elif by_sub_time == "may":
            month = "05"
            day = "31"
        elif by_sub_time == "june":
            month = "06"
            day = "30"
        elif by_sub_time == "july":
            month = "07"
            day = "31"
        elif by_sub_time == "august":
            month = "08"
            day = "31"
        elif by_sub_time == "september":
            month = "09"
            day = "30"
        elif by_sub_time == "october":
            month = "10"
            day = "31"
        elif by_sub_time == "november":
            month = "11"
            day = "30"
        else:
            month = "12"
            day = "31"
        if country == "world":
            text = "Sorry, but SCITalk cannot get global data over time because it would take too long to sum count totals for every country"
            # for x in range(1,int(day) + 1):
            #     counts[x] = 0
            # text = "Globally there have been "
            # r = requests.get("https://api.covid19api.com/countries")
            # summary = r.json()
            # for x in summary:
            #     country = x["Country"]
            #     r2 = requests.get("https://api.covid19api.com/country/" + country + "/status/" + case_type + "?from=2020-" + month + "-01T00:00:00Z&to=2020-" + month + "-" + day + "T00:00:00Z")
            #     summary2 = r2.json()
            #     d = 1
            #     days = []
            #     for x in summary2: 
            #         if("Date" in x):
            #             days.append(int(x["Date"][8:10]))
            #     days.sort()
            #     if(days):
            #         d = days[0]
            #         if summary2[1]["Province"] == "":
            #             for x in summary2:    
            #                 if int(x["Date"][8:10]) == d:
            #                     counts[d] += x["Cases"]
            #                     d += 1
            #         else:
            #             for x in range(d,int(day) + 1):
            #                 counts[x] = 0
            #             for x in range(len(summary2)):
            #                 if int(summary2[x]["Date"][8:10]) == d:
            #                     counts[d] += summary2[x]["Cases"]
            #                 if x+1 != len(summary2) and int(summary2[x+1]["Date"][8:10]) != d:
            #                     d += 1
            #         d = 1
            #         for x in counts:
            #             text = text + str(counts[x]) + " " + scope + " " 
            #             if case_type == "recovered":
            #                 text = text + "recoveries on " + str(by_sub_time) + " " + str(x)
            #             elif case_type == "confirmed":
            #                 text = text + case_type + " cases on " + str(by_sub_time) + " " + str(x)
            #             else:
            #                 text = text + case_type + " on " + str(by_sub_time) + " " + str(x)
            #             if str(x)[-1] == "1":
            #                 text = text + "st"
            #             elif str(x)[-1] == "2":
            #                 text = text + "nd"
            #             elif str(x)[-1] == "3":
            #                 text = text + "rd"
            #             else:
            #                 text = text + "th"
                        
            #             if int(day) == d + 1:
            #                 text = text + ", and "
            #             elif int(day) != d:
            #                 text = text + ", "
            #             d += 1
            #     text = text + "."
        else:
            for c in countries:
                country = c
                text =  text + "In " + country + " there have been "
                r = requests.get("https://api.covid19api.com/country/" + country + "/status/" + case_type + "?from=2020-" + month + "-01T00:00:00Z&to=2020-" + month + "-" + day + "T00:00:00Z")
                summary = r.json()
                d = 1
                days = []
                for x in summary: 
                    days.append(int(x["Date"][8:10]))
                days.sort()
                d = days[0]
                if summary[1]["Province"] == "":
                    for x in summary:    
                        if int(x["Date"][8:10]) == d:
                            counts[d] = x["Cases"]
                            d += 1
                else:
                    for x in range(d,int(day) + 1):
                        counts[x] = 0
                    for x in range(len(summary)):
                        if int(summary[x]["Date"][8:10]) == d:
                            counts[d] += summary[x]["Cases"]
                        if x+1 != len(summary) and int(summary[x+1]["Date"][8:10]) != d:
                            d += 1
                d = 1
                for x in counts:
                    text = text + str(counts[x]) + " " + scope + " " 
                    if case_type == "recovered":
                        text = text + "recoveries on " + str(by_sub_time) + " " + str(x)
                    elif case_type == "confirmed":
                        text = text + case_type + " cases on " + str(by_sub_time) + " " + str(x)
                    else:
                        text = text + case_type + " on " + str(by_sub_time) + " " + str(x)
                    if str(x)[-1] == "1" and str(x)[-2] != "1":
                        text = text + "st"
                    elif str(x)[-1] == "2" and str(x)[-2] != "1":
                        text = text + "nd"
                    elif str(x)[-1] == "3"and str(x)[-2] != "1":
                        text = text + "rd"
                    else:
                        text = text + "th"
                    
                    if int(day) == d + 1:
                        text = text + ", and "
                    elif int(day) != d:
                        text = text + ", "
                    d += 1
                text = text + "."
                if len(countries) > 1:
                    text = text + "\n\n"
        dispatcher.utter_message(text = text)
        return []
		
		
		
		
class ActionCaseCountSince(Action):

    @staticmethod
    def required_fields():
        return [
            #EntityFormField("scope", "scope"),
            #EntityFormField("case_type", "case_type"),
            EntityFormField("countries", "countries")
        ]

    def name(self):
        return "action_case_count_since"
    
    def run(self, dispatcher, tracker, domain): 
        scope = tracker.get_slot('scope')
        if scope == None:
            scope = "total"
        case_type = tracker.get_slot('case_type')
        if case_type == None:
            case_type = "confirmed"
        countries = tracker.get_slot('countries')
        country = "world"
        if countries != None:
            country = countries[0]
        by_sub_time = tracker.get_slot('bysubtime')
        if by_sub_time == None:
            by_sub_time = "january" 
        
        text = ""
        counts = {}
        month = ""
        if by_sub_time == "january":
            month = "01"
        elif by_sub_time == "february":
            month = "02"
        elif by_sub_time == "march":
            month = "03"
        elif by_sub_time == "april":
            month = "04"
        elif by_sub_time == "may":
            month = "05"
        elif by_sub_time == "june":
            month = "06"
        elif by_sub_time == "july":
            month = "07"
        elif by_sub_time == "august":
            month = "08"
        elif by_sub_time == "september":
            month = "09"
        elif by_sub_time == "october":
            month = "10"
        elif by_sub_time == "november":
            month = "11"
        else:
            month = "12"
        if country == "world":
            text = "Sorry, but SCITalk cannot get global data over time because it would take too long to sum count totals for every country"
        else:
            currentMonth = date.today().strftime("%m")		
            currentDay = date.today().strftime("%d")		
            currentDay = str(int(currentDay) - 1)

            if(currentMonth == month and currentDay == "01"):
               dispatcher.utter_message(text = "Cannot calculate info")
               return []			  
			
            for c in countries:
                country = c
                text =  text + "In " + country + " since " + by_sub_time + " there have been "
                r = requests.get("https://api.covid19api.com/country/" + country + "/status/" + case_type + "?from=2020-" + month + "-01T00:00:00Z&to=2020-" + currentMonth + "-" + currentDay + "T00:00:00Z")
                summary = r.json()
                
                m = int(month)-1
				
                start = 0
                end = 0
                if summary[0]["Province"] == "" and summary[1]["Province"] == "":
                    start = summary[0]["Cases"]
                    end = summary[len(summary)-1]["Cases"]					
					# for x in range(m,int(currentMonth) + 1):
                        # counts[x] = 0
                    # for x in range(len(summary)):
                        # if int(summary[x]["Date"][5:7]) == m and int(summary[x]["Date"][8:10]) == 1:
                            # counts[m] += summary[x]["Cases"]
                        # if x+1 != len(summary) and int(summary[x+1]["Date"][5:7]) != m:
                            # m += 1				
                else:
                    r2 = requests.get("https://api.covid19api.com/country/" + country + "/status/" + case_type + "?from=2020-03-01T00:00:00Z&to=2020-03-01T12:00:00Z")
                    summary2 = r2.json()
                    numProv = len(summary2)
					
                    for i in range(numProv):
                        start += summary[i]["Cases"]
                        end += summary[len(summary)-i-1]["Cases"]	
	                    
                m = 1
                numM = len(counts)
				
                total = end - start
				#counts[numM] - counts[int(month)]
                # i = 1
                # for x in counts:
                    # text = text + str(i) +": " + str(x) + " "				
                    # total = total + counts[x]
                    # i = i + 1
                
                text = text + str(total) +  " " 
                if case_type == "recovered":
                    text = text + "recoveriesl"
                elif case_type == "confirmed":
                    text = text + case_type + " cases."
                else:
                   text = text + case_type + "."
                #text = text + scope
                #text = text + "."
                if len(countries) > 1:
                    text = text + "\n\n"
        dispatcher.utter_message(text = text)
        return []

class ActionCaseCountBefore(Action):

    @staticmethod
    def required_fields():
        return [
            #EntityFormField("scope", "scope"),
            #EntityFormField("case_type", "case_type"),
            EntityFormField("countries", "countries")
        ]

    def name(self):
        return "action_case_count_before"
    
    def run(self, dispatcher, tracker, domain): 
        scope = tracker.get_slot('scope')
        if scope == None:
            scope = "total"
        case_type = tracker.get_slot('case_type')
        if case_type == None:
            case_type = "confirmed"
        countries = tracker.get_slot('countries')
        country = "world"
        if countries != None:
            country = countries[0]
        by_sub_time = tracker.get_slot('bysubtime')
        if by_sub_time == None:
            by_sub_time = "january" 
        
        text = ""
        counts = {}
        month = ""
        if by_sub_time == "january":
            month = "01"
        elif by_sub_time == "february":
            month = "02"
        elif by_sub_time == "march":
            month = "03"
        elif by_sub_time == "april":
            month = "04"
        elif by_sub_time == "may":
            month = "05"
        elif by_sub_time == "june":
            month = "06"
        elif by_sub_time == "july":
            month = "07"
        elif by_sub_time == "august":
            month = "08"
        elif by_sub_time == "september":
            month = "09"
        elif by_sub_time == "october":
            month = "10"
        elif by_sub_time == "november":
            month = "11"
        else:
            month = "12"
        if country == "world":
            text = "Sorry, but SCITalk cannot get global data over time because it would take too long to sum count totals for every country"
        else:
            for c in countries:
                country = c
                text =  text + "In " + country + " before " + by_sub_time + " there have been "
                r = requests.get("https://api.covid19api.com/country/" + country + "/status/" + case_type + "?from=2020-01-01T00:00:00Z&to=2020-" + month + "-01T00:00:00Z")
                summary = r.json()
                m = int(month)-1
				
                start = 0
                end = 0
                if summary[0]["Province"] == "" and summary[1]["Province"] == "":
                    start = summary[0]["Cases"]
                    end = summary[len(summary)-1]["Cases"]					
					# for x in range(m,int(currentMonth) + 1):
                        # counts[x] = 0
                    # for x in range(len(summary)):
                        # if int(summary[x]["Date"][5:7]) == m and int(summary[x]["Date"][8:10]) == 1:
                            # counts[m] += summary[x]["Cases"]
                        # if x+1 != len(summary) and int(summary[x+1]["Date"][5:7]) != m:
                            # m += 1				
                else:
                    r2 = requests.get("https://api.covid19api.com/country/" + country + "/status/" + case_type + "?from=2020-03-01T00:00:00Z&to=2020-03-01T12:00:00Z")
                    summary2 = r2.json()
                    numProv = len(summary2)
					
                    for i in range(numProv):
                        start += summary[i]["Cases"]
                        end += summary[len(summary)-i-1]["Cases"]	
	                    
                m = 1
                numM = len(counts)
				
                total = end - start
				#counts[numM] - counts[int(month)]
                # i = 1
                # for x in counts:
                    # text = text + str(i) +": " + str(x) + " "				
                    # total = total + counts[x]
                    # i = i + 1
                
                text = text + str(total) +  " " 
                if case_type == "recovered":
                    text = text + "recoveries in "
                elif case_type == "confirmed":
                    text = text + case_type + " cases in "
                else:
                   text = text + case_type + " in "
                text = text + scope
                text = text + "."
                if len(countries) > 1:
                    text = text + "\n\n"
        dispatcher.utter_message(text = text)
        return []

class ActionCaseCountSinceSpecific(Action):

    @staticmethod
    def required_fields():
        return [
            #EntityFormField("scope", "scope"),
            #EntityFormField("case_type", "case_type"),
            EntityFormField("countries", "countries")
        ]

    def name(self):
        return "action_case_count_since_specific"
    
    def run(self, dispatcher, tracker, domain): 
        scope = tracker.get_slot('scope')
        if scope == None:
            scope = "total"
        case_type = tracker.get_slot('case_type')
        if case_type == None:
            case_type = "confirmed"
        countries = tracker.get_slot('countries')
        country = "world"
        if countries != None:
            country = countries[0]
        by_sub_time = tracker.get_slot('bysubtime')
        if by_sub_time == None:
            by_sub_time = "january" 
        by_day = tracker.get_slot('byday')
        if by_day == None:
            by_day = 1
        if "-" in by_day:
            by_day = by_day.replace("-", " ")

        text = ""
        counts = {}
        month = ""
        day = ""
        if by_sub_time == "january":
            month = "01"
        elif by_sub_time == "february":
            month = "02"
        elif by_sub_time == "march":
            month = "03"
        elif by_sub_time == "april":
            month = "04"
        elif by_sub_time == "may":
            month = "05"
        elif by_sub_time == "june":
            month = "06"
        elif by_sub_time == "july":
            month = "07"
        elif by_sub_time == "august":
            month = "08"
        elif by_sub_time == "september":
            month = "09"
        elif by_sub_time == "october":
            month = "10"
        elif by_sub_time == "november":
            month = "11"
        else:
            month = "12"
        
        if by_day == "1" or by_day == "one" or by_day == "first":
            day = "01"
        elif by_day == "2" or by_day == "two" or by_day == "second":
            day = "02"
        elif by_day == "3" or by_day == "three" or by_day == "third":
            day = "03"
        elif by_day == "4" or by_day == "four" or by_day == "fourth":
            day = "04"
        elif by_day == "5" or by_day == "five" or by_day == "fifth":
            day = "05"
        elif by_day == "6" or by_day == "six" or by_day == "sixth":
            day = "06"
        elif by_day == "7" or by_day == "seven" or by_day == "seventh":
            day = "07"
        elif by_day == "8" or by_day == "eight" or by_day == "eighth":
            day = "08"
        elif by_day == "9" or by_day == "nine" or by_day == "ninth":
            day = "09"
        elif by_day == "10" or by_day == "ten" or by_day == "tenth":
            day = "10"
        elif by_day == "11" or by_day == "eleven" or by_day == "eleventh":
            day = "11"
        elif by_day == "12" or by_day == "twelve" or by_day == "twelfth":
            day = "12"
        elif by_day == "13" or by_day == "thirteen" or by_day == "thirteenth":
            day = "13"
        elif by_day == "14" or by_day == "fourteen" or by_day == "fourteenth":
            day = "14"
        elif by_day == "15" or by_day == "fifteen" or by_day == "fifteenth":
            day = "15"
        elif by_day == "16" or by_day == "sixteen" or by_day == "sixteenth":
            day = "16"
        elif by_day == "17" or by_day == "seventeen" or by_day == "seventeenth":
            day = "17"
        elif by_day == "18" or by_day == "eighteen" or by_day == "eighteenth":
            day = "18"
        elif by_day == "19" or by_day == "nineteen" or by_day == "nineteenth":
            day = "19"
        elif by_day == "20" or by_day == "twenty" or by_day == "twentieth":
            day = "20"
        elif by_day == "21" or by_day == "twenty one" or by_day == "twenty first":
            day = "21"
        elif by_day == "22" or by_day == "twenty two" or by_day == "twenty second":
            day = "22"
        elif by_day == "23" or by_day == "twenty three" or by_day == "twenty third":
            day = "23"
        elif by_day == "24" or by_day == "twenty four" or by_day == "twenty fourth":
            day = "24"
        elif by_day == "25" or by_day == "twenty five" or by_day == "twenty fifth":
            day = "25"
        elif by_day == "26" or by_day == "twenty six" or by_day == "twenty sixth":
            day = "26"
        elif by_day == "27" or by_day == "twenty seven" or by_day == "twenty seventh":
            day = "27"
        elif by_day == "28" or by_day == "twenty eight" or by_day == "twenty eighth":
            day = "28"
        elif by_day == "29" or by_day == "twenty nine" or by_day == "twenty ninth":
            day = "29"
        elif by_day == "30" or by_day == "thirty" or by_day == "thirtieth":
            day = "30"
        else:
            day = "31"

        if month == "02" or month == "04" or month == "06" or month == "09" or month == "11":
            if day == "31" or (month == "02" and day == "30"):
                text = "Please enter a valid date."
                dispatcher.utter_message(text = text)
                return []

        if country == "world":
            text = "Sorry, but SCITalk cannot get global data over time because it would take too long to sum count totals for every country"
        else:
            currentMonth = date.today().strftime("%m")		
            currentDay = date.today().strftime("%d")		
            currentDay = str(int(currentDay) - 1)

            if(currentMonth == month and currentDay == "01"):
               dispatcher.utter_message(text = "Cannot calculate info")
               return []			  
			
            for c in countries:
                country = c
                text =  text + "In " + country + " since " + by_sub_time + " "
                if day[-1] == "1" and day[-2] != "1":
                    if day[0] == "0":
                        text = text + day[1] + "st"
                    else:
                        text = text + day + "st"
                elif day[-1] == "2" and day[-2] != "1":
                    if day[0] == "0":
                        text = text + day[1] + "nd"
                    else:
                        text = text + day + "nd"
                elif day[-1] == "3"and day[-2] != "1":
                    if day[0] == "0":
                        text = text + day[1] + "rd"
                    else:
                        text = text + day + "rd"
                else:
                    if day[0] == "0":
                        text = text + day[1] + "th"
                    else:
                        text = text + day + "th"
                text = text + " there have been "
                
                r = requests.get("https://api.covid19api.com/country/" + country + "/status/" + case_type + "?from=2020-" + month + "-" + day + "T00:00:00Z&to=2020-" + currentMonth + "-" + currentDay + "T00:00:00Z")
                summary = r.json()
                
                m = int(month)-1
				
                start = 0
                end = 0
                if summary[0]["Province"] == "" and summary[1]["Province"] == "":
                    start = summary[0]["Cases"]
                    end = summary[len(summary)-1]["Cases"]					
					# for x in range(m,int(currentMonth) + 1):
                        # counts[x] = 0
                    # for x in range(len(summary)):
                        # if int(summary[x]["Date"][5:7]) == m and int(summary[x]["Date"][8:10]) == 1:
                            # counts[m] += summary[x]["Cases"]
                        # if x+1 != len(summary) and int(summary[x+1]["Date"][5:7]) != m:
                            # m += 1				
                else:
                    r2 = requests.get("https://api.covid19api.com/country/" + country + "/status/" + case_type + "?from=2020-03-01T00:00:00Z&to=2020-03-01T12:00:00Z")
                    summary2 = r2.json()
                    numProv = len(summary2)
					
                    for i in range(numProv):
                        start += summary[i]["Cases"]
                        end += summary[len(summary)-i-1]["Cases"]	
	                    
                m = 1
                numM = len(counts)
				
                total = end - start
				#counts[numM] - counts[int(month)]
                # i = 1
                # for x in counts:
                    # text = text + str(i) +": " + str(x) + " "				
                    # total = total + counts[x]
                    # i = i + 1
                
                text = text + str(total) +  " " 
                if case_type == "recovered":
                    text = text + "recoveries in "
                elif case_type == "confirmed":
                    text = text + case_type + " cases in "
                else:
                   text = text + case_type + " in "
                text = text + scope
                text = text + "."
                if len(countries) > 1:
                    text = text + "\n\n"
        dispatcher.utter_message(text = text)
        return []

class ActionCaseCountBeforeSpecific(Action):

    @staticmethod
    def required_fields():
        return [
            #EntityFormField("scope", "scope"),
            #EntityFormField("case_type", "case_type"),
            EntityFormField("countries", "countries")
        ]

    def name(self):
        return "action_case_count_before_specific"
    
    def run(self, dispatcher, tracker, domain): 
        scope = tracker.get_slot('scope')
        if scope == None:
            scope = "total"
        case_type = tracker.get_slot('case_type')
        if case_type == None:
            case_type = "confirmed"
        countries = tracker.get_slot('countries')
        country = "world"
        if countries != None:
            country = countries[0]
        by_sub_time = tracker.get_slot('bysubtime')
        if by_sub_time == None:
            by_sub_time = "january" 
        by_day = tracker.get_slot('byday')
        if by_day == None:
            by_day = 1
        if "-" in by_day:
            by_day = by_day.replace("-", " ")

        text = ""
        counts = {}
        month = ""
        day = ""
        if by_sub_time == "january":
            month = "01"
        elif by_sub_time == "february":
            month = "02"
        elif by_sub_time == "march":
            month = "03"
        elif by_sub_time == "april":
            month = "04"
        elif by_sub_time == "may":
            month = "05"
        elif by_sub_time == "june":
            month = "06"
        elif by_sub_time == "july":
            month = "07"
        elif by_sub_time == "august":
            month = "08"
        elif by_sub_time == "september":
            month = "09"
        elif by_sub_time == "october":
            month = "10"
        elif by_sub_time == "november":
            month = "11"
        else:
            month = "12"
        
        if by_day == "1" or by_day == "one" or by_day == "first":
            day = "01"
        elif by_day == "2" or by_day == "two" or by_day == "second":
            day = "02"
        elif by_day == "3" or by_day == "three" or by_day == "third":
            day = "03"
        elif by_day == "4" or by_day == "four" or by_day == "fourth":
            day = "04"
        elif by_day == "5" or by_day == "five" or by_day == "fifth":
            day = "05"
        elif by_day == "6" or by_day == "six" or by_day == "sixth":
            day = "06"
        elif by_day == "7" or by_day == "seven" or by_day == "seventh":
            day = "07"
        elif by_day == "8" or by_day == "eight" or by_day == "eighth":
            day = "08"
        elif by_day == "9" or by_day == "nine" or by_day == "ninth":
            day = "09"
        elif by_day == "10" or by_day == "ten" or by_day == "tenth":
            day = "10"
        elif by_day == "11" or by_day == "eleven" or by_day == "eleventh":
            day = "11"
        elif by_day == "12" or by_day == "twelve" or by_day == "twelfth":
            day = "12"
        elif by_day == "13" or by_day == "thirteen" or by_day == "thirteenth":
            day = "13"
        elif by_day == "14" or by_day == "fourteen" or by_day == "fourteenth":
            day = "14"
        elif by_day == "15" or by_day == "fifteen" or by_day == "fifteenth":
            day = "15"
        elif by_day == "16" or by_day == "sixteen" or by_day == "sixteenth":
            day = "16"
        elif by_day == "17" or by_day == "seventeen" or by_day == "seventeenth":
            day = "17"
        elif by_day == "18" or by_day == "eighteen" or by_day == "eighteenth":
            day = "18"
        elif by_day == "19" or by_day == "nineteen" or by_day == "nineteenth":
            day = "19"
        elif by_day == "20" or by_day == "twenty" or by_day == "twentieth":
            day = "20"
        elif by_day == "21" or by_day == "twenty one" or by_day == "twenty first":
            day = "21"
        elif by_day == "22" or by_day == "twenty two" or by_day == "twenty second":
            day = "22"
        elif by_day == "23" or by_day == "twenty three" or by_day == "twenty third":
            day = "23"
        elif by_day == "24" or by_day == "twenty four" or by_day == "twenty fourth":
            day = "24"
        elif by_day == "25" or by_day == "twenty five" or by_day == "twenty fifth":
            day = "25"
        elif by_day == "26" or by_day == "twenty six" or by_day == "twenty sixth":
            day = "26"
        elif by_day == "27" or by_day == "twenty seven" or by_day == "twenty seventh":
            day = "27"
        elif by_day == "28" or by_day == "twenty eight" or by_day == "twenty eighth":
            day = "28"
        elif by_day == "29" or by_day == "twenty nine" or by_day == "twenty ninth":
            day = "29"
        elif by_day == "30" or by_day == "thirty" or by_day == "thirtieth":
            day = "30"
        else:
            day = "31"
        
        if month == "02" or month == "04" or month == "06" or month == "09" or month == "11":
            if day == "31" or (month == "02" and day == "30"):
                text = "Please enter a valid date."
                dispatcher.utter_message(text = text)
                return []

        if country == "world":
            text = "Sorry, but SCITalk cannot get global data over time because it would take too long to sum count totals for every country"
        else:
            for c in countries:
                country = c
                text =  text + "In " + country + " before " + by_sub_time + " "
                if day[-1] == "1" and day[-2] != "1":
                    if day[0] == "0":
                        text = text + day[1] + "st"
                    else:
                        text = text + day + "st"
                elif day[-1] == "2" and day[-2] != "1":
                    if day[0] == "0":
                        text = text + day[1] + "nd"
                    else:
                        text = text + day + "nd"
                elif day[-1] == "3"and day[-2] != "1":
                    if day[0] == "0":
                        text = text + day[1] + "rd"
                    else:
                        text = text + day + "rd"
                else:
                    if day[0] == "0":
                        text = text + day[1] + "th"
                    else:
                        text = text + day + "th"
                text = text + " there have been "

                r = requests.get("https://api.covid19api.com/country/" + country + "/status/" + case_type + "?from=2020-01-01T00:00:00Z&to=2020-" + month + "-" + day + "T00:00:00Z")
                summary = r.json()
                
                m = int(month)-1
				
                start = 0
                end = 0
                if summary[0]["Province"] == "" and summary[1]["Province"] == "":
                    start = summary[0]["Cases"]
                    end = summary[len(summary)-1]["Cases"]					
					# for x in range(m,int(currentMonth) + 1):
                        # counts[x] = 0
                    # for x in range(len(summary)):
                        # if int(summary[x]["Date"][5:7]) == m and int(summary[x]["Date"][8:10]) == 1:
                            # counts[m] += summary[x]["Cases"]
                        # if x+1 != len(summary) and int(summary[x+1]["Date"][5:7]) != m:
                            # m += 1				
                else:
                    r2 = requests.get("https://api.covid19api.com/country/" + country + "/status/" + case_type + "?from=2020-03-01T00:00:00Z&to=2020-03-01T12:00:00Z")
                    summary2 = r2.json()
                    numProv = len(summary2)
					
                    for i in range(numProv):
                        start += summary[i]["Cases"]
                        end += summary[len(summary)-i-1]["Cases"]	
	                    
                m = 1
                numM = len(counts)
				
                total = end - start
				#counts[numM] - counts[int(month)]
                # i = 1
                # for x in counts:
                    # text = text + str(i) +": " + str(x) + " "				
                    # total = total + counts[x]
                    # i = i + 1
                
                text = text + str(total) +  " " 
                if case_type == "recovered":
                    text = text + "recoveries in "
                elif case_type == "confirmed":
                    text = text + case_type + " cases in "
                else:
                   text = text + case_type + " in "
                text = text + scope
                text = text + "."
                if len(countries) > 1:
                    text = text + "\n\n"
        dispatcher.utter_message(text = text)
        return []

class ActionCaseCountOnDay(Action):

    @staticmethod
    def required_fields():
        return [
            #EntityFormField("scope", "scope"),
            #EntityFormField("case_type", "case_type"),
            EntityFormField("countries", "countries")
        ]

    def name(self):
        return "action_case_count_on_day"
    
    def run(self, dispatcher, tracker, domain): 
        scope = tracker.get_slot('scope')
        if scope == None:
            scope = "total"
        case_type = tracker.get_slot('case_type')
        if case_type == None:
            case_type = "confirmed"
        countries = tracker.get_slot('countries')
        country = "world"
        if countries != None:
            country = countries[0]
        by_sub_time = tracker.get_slot('bysubtime')
        if by_sub_time == None:
            by_sub_time = "january" 
        by_day = tracker.get_slot('byday')

        text = ""
        counts = {}
        month = ""
        nextMonth = ""
        if by_sub_time == "january":
            month = "01"
            nextMonth = "02"
        elif by_sub_time == "february":
            month = "02"
            nextMonth = "03"
        elif by_sub_time == "march":
            month = "03"
            nextMonth = "04"
        elif by_sub_time == "april":
            month = "04"
            nextMonth = "05"
        elif by_sub_time == "may":
            month = "05"
            nextMonth = "06"
        elif by_sub_time == "june":
            month = "06"
            nextMonth = "07"
        elif by_sub_time == "july":
            month = "07"
            nextMonth = "08"
        elif by_sub_time == "august":
            month = "08"
            nextMonth = "09"
        elif by_sub_time == "september":
            month = "09"
            nextMonth = "10"
        elif by_sub_time == "october":
            month = "10"
            nextMonth = "11"
        elif by_sub_time == "november":
            month = "11"
            nextMonth = "12"
        else:
            month = "12"
            nextMonth = "01"
        if by_day == None:
            if country == "world":
                text = "Sorry, but SCITalk cannot get global data over time because it would take too long to sum count totals for every country"
            else:
                for c in countries:
                    country = c
                    text =  text + "In " + country + " on " + by_sub_time + " there have been "
                    if month != "12":
                        r = requests.get("https://api.covid19api.com/country/" + country + "/status/" + case_type + "?from=2020-" + month +"-01T00:00:00Z&to=2020-" + nextMonth + "-01T00:00:00Z")
                    else:
                        r = requests.get("https://api.covid19api.com/country/" + country + "/status/" + case_type + "?from=2020-" + month +"-01T00:00:00Z&to=2021-" + nextMonth + "-01T00:00:00Z")
                    summary = r.json()
                    m = int(month)-1
                    
                    start = 0
                    end = 0
                    if summary[0]["Province"] == "" and summary[1]["Province"] == "":
                        start = summary[0]["Cases"]
                        end = summary[len(summary)-1]["Cases"]
                    else:
                        r2 = requests.get("https://api.covid19api.com/country/" + country + "/status/" + case_type + "?from=2020-03-01T00:00:00Z&to=2020-03-01T12:00:00Z")
                        summary2 = r2.json()
                        numProv = len(summary2)
                        
                        for i in range(numProv):
                            start += summary[i]["Cases"]
                            end += summary[len(summary)-i-1]["Cases"]	
                            
                    m = 1
                    numM = len(counts)
                    
                    total = end - start
                    text = text + str(total) +  " " 
                    if case_type == "recovered":
                        text = text + "recoveries in "
                    elif case_type == "confirmed":
                        text = text + case_type + " cases in "
                    else:
                        text = text + case_type + " in "
                    text = text + scope
                    text = text + "."
                    if len(countries) > 1:
                        text = text + "\n\n"
        else:
            if "-" in by_day:
                by_day = by_day.replace("-", " ")
            day = ""
            nextDay = ""
            if by_day == "1" or by_day == "one" or by_day == "first":
                day = "01"
                newDay = "02"
            elif by_day == "2" or by_day == "two" or by_day == "second":
                day = "02"
                newDay = "03"
            elif by_day == "3" or by_day == "three" or by_day == "third":
                day = "03"
                newDay = "04"
            elif by_day == "4" or by_day == "four" or by_day == "fourth":
                day = "04"
                newDay = "05"
            elif by_day == "5" or by_day == "five" or by_day == "fifth":
                day = "05"
                newDay = "06"
            elif by_day == "6" or by_day == "six" or by_day == "sixth":
                day = "06"
                newDay = "07"
            elif by_day == "7" or by_day == "seven" or by_day == "seventh":
                day = "07"
                newDay = "08"
            elif by_day == "8" or by_day == "eight" or by_day == "eighth":
                day = "08"
                newDay = "09"
            elif by_day == "9" or by_day == "nine" or by_day == "ninth":
                day = "09"
                newDay = "10"
            elif by_day == "10" or by_day == "ten" or by_day == "tenth":
                day = "10"
                newDay = "11"
            elif by_day == "11" or by_day == "eleven" or by_day == "eleventh":
                day = "11"
                newDay = "12"
            elif by_day == "12" or by_day == "twelve" or by_day == "twelfth":
                day = "12"
                newDay = "13"
            elif by_day == "13" or by_day == "thirteen" or by_day == "thirteenth":
                day = "13"
                newDay = "14"
            elif by_day == "14" or by_day == "fourteen" or by_day == "fourteenth":
                day = "14"
                newDay = "15"
            elif by_day == "15" or by_day == "fifteen" or by_day == "fifteenth":
                day = "15"
                newDay = "16"
            elif by_day == "16" or by_day == "sixteen" or by_day == "sixteenth":
                day = "16"
                newDay = "17"
            elif by_day == "17" or by_day == "seventeen" or by_day == "seventeenth":
                day = "17"
                newDay = "18"
            elif by_day == "18" or by_day == "eighteen" or by_day == "eighteenth":
                day = "18"
                newDay = "19"
            elif by_day == "19" or by_day == "nineteen" or by_day == "nineteenth":
                day = "19"
                newDay = "20"
            elif by_day == "20" or by_day == "twenty" or by_day == "twentieth":
                day = "20"
                newDay = "21"
            elif by_day == "21" or by_day == "twenty one" or by_day == "twenty first":
                day = "21"
                newDay = "22"
            elif by_day == "22" or by_day == "twenty two" or by_day == "twenty second":
                day = "22"
                newDay = "23"
            elif by_day == "23" or by_day == "twenty three" or by_day == "twenty third":
                day = "23"
                newDay = "24"
            elif by_day == "24" or by_day == "twenty four" or by_day == "twenty fourth":
                day = "24"
                newDay = "25"
            elif by_day == "25" or by_day == "twenty five" or by_day == "twenty fifth":
                day = "25"
                newDay = "26"
            elif by_day == "26" or by_day == "twenty six" or by_day == "twenty sixth":
                day = "26"
                newDay = "27"
            elif by_day == "27" or by_day == "twenty seven" or by_day == "twenty seventh":
                day = "27"
                newDay = "28"
            elif by_day == "28" or by_day == "twenty eight" or by_day == "twenty eighth":
                day = "28"
                newDay = "29"
            elif by_day == "29" or by_day == "twenty nine" or by_day == "twenty ninth":
                day = "29"
                newDay = "30"
            elif by_day == "30" or by_day == "thirty" or by_day == "thirtieth":
                day = "30"
                newDay = "31"
            else:
                day = "31"
                newDay = "01"
            
            if month == "02" or month == "04" or month == "06" or month == "09" or month == "11":
                if day == "31" or (month == "02" and day == "30"):
                    text = "Please enter a valid date."
                    dispatcher.utter_message(text = text)
                    return []

            if country == "world":
                text = "Sorry, but SCITalk cannot get global data over time because it would take too long to sum count totals for every country"
            else:
                for c in countries:
                    country = c
                    text =  text + "In " + country + " on " + by_sub_time + " "
                    if day[-1] == "1" and day[-2] != "1":
                        if day[0] == "0":
                            text = text + day[1] + "st"
                        else:
                            text = text + day + "st"
                    elif day[-1] == "2" and day[-2] != "1":
                        if day[0] == "0":
                            text = text + day[1] + "nd"
                        else:
                            text = text + day + "nd"
                    elif day[-1] == "3"and day[-2] != "1":
                        if day[0] == "0":
                            text = text + day[1] + "rd"
                        else:
                            text = text + day + "rd"
                    else:
                        if day[0] == "0":
                            text = text + day[1] + "th"
                        else:
                            text = text + day + "th"
                    text = text + " there have been "

                    r = ""
                    if day != "31":
                        r = requests.get("https://api.covid19api.com/country/" + country + "/status/" + case_type + "?from=2020-" + month + "-" + day + "T00:00:00Z&to=2020-" + month + "-" + newDay + "T00:00:00Z")
                    else:
                        r = requests.get("https://api.covid19api.com/country/" + country + "/status/" + case_type + "?from=2020-" + month + "-" + day + "T00:00:00Z&to=2020-" + newMonth + "-" + newDay + "T00:00:00Z")
                    summary = r.json()
                    
                    m = int(month)-1
                    
                    start = 0
                    end = 0
                    if summary[0]["Province"] == "" and summary[1]["Province"] == "":
                        start = summary[0]["Cases"]
                        end = summary[len(summary)-1]["Cases"]
                    else:
                        r2 = requests.get("https://api.covid19api.com/country/" + country + "/status/" + case_type + "?from=2020-03-01T00:00:00Z&to=2020-03-01T12:00:00Z")
                        summary2 = r2.json()
                        numProv = len(summary2)
                        
                        for i in range(numProv):
                            start += summary[i]["Cases"]
                            end += summary[len(summary)-i-1]["Cases"]	
                            
                    m = 1
                    numM = len(counts)
                    
                    total = end - start
                    text = text + str(total) +  " " 
                    if case_type == "recovered":
                        text = text + "recoveries in "
                    elif case_type == "confirmed":
                        text = text + case_type + " cases in "
                    else:
                        text = text + case_type + " in "
                    text = text + scope
                    text = text + "."
                    if len(countries) > 1:
                        text = text + "\n\n"
        dispatcher.utter_message(text = text)
        return []


class ActionDayOne(Action):


    @staticmethod
    def required_fields():
        return [
            #EntityFormField("scope", "scope"),
            #EntityFormField("case_type", "case_type"),
            EntityFormField("countries", "countries")
        ]
    
    def name(self):
        return "get_first_day"
        
        
    def run(self, dispatcher, tracker, domain): 
        case_type = tracker.get_slot('case_type')
        if case_type == None:
            case_type = "confirmed"
        countries = tracker.get_slot('countries')
        country = "world"
        if countries != None:
            country = countries[0]

        
        text = ""
        if country == "world":
            text = "The first confirmed case (reported in the api) occured in China on January 22, the actual first case according to an unpublicised report was November 17, 2019."
        else:
            for c in countries:
                r = requests.get("https://api.covid19api.com/total/dayone/country/" + c + "/status/confirmed")
                summary = r.json()
                
                if(summary != []):
                    date = summary[0]["Date"]
                    text += "The first case (reported in the api) in " + c + " was on "
                    
                    month = int(date[5:7])
                    
                    if month == 1:
                        text += "January "
                    if month == 2:
                        text +="February "
                    if month == 3:
                        text +="March "
                    if month == 4:
                        text+= "April "
                    if month==5:
                        text+= "May "
                    if month==6:
                        text+= "June "
                    if month==7:
                        text+= "July "
                    if month==8:
                        text+= "August "
                    if month==9:
                        text+= "September"
                    if month==10:
                        text+= "October "
                    if month==11:
                        text+= "November "
                    if month==12:
                        text+= "December "
                        
                        
                    text += date[8:10] + " " + date[0:4]
                    text = text + "."
                else:
                    text += "No recorded cases in " + c
                    
                if len(countries) > 1:
                    text = text + "\n\n"
        dispatcher.utter_message(text = text)
        return []



###########
#  FORMS  #
###########

class CaseCountFormValidator(FormValidationAction):

    def name(self):
        return "validate_case_count_form"
    
    @staticmethod
    def scope_db() -> List[Text]:
        """Database of supported values"""
        return ["new", "total"]
    
    @staticmethod
    def case_type_db() -> List[Text]:
        #Database of supported values
        return ["confirmed", "recovered", "deaths"]

    def validate_scope(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]:
        #Validate scope value.
        if slot_value == None:
            return {"scope": "total"}
        return {"scope": slot_value}

    def validate_case_type(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]:
        #Validate case_type value.
        if slot_value == None:
            return {"case_type": "confirmed"}
        return {"case_type": slot_value}
    
    def validate_use_global(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]:
        #Validate use_global value.

        if isinstance(slot_value, str):
            if "global" in slot_value:
                return {"use_global": True}
            else:
                return {"use_global": False}
        elif type(slot_value) is bool:
            return {"use_global": slot_value}
        else:
            return {"use_global": False}   
    
    def validate_countries_text(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]:
        #Validate countries value.
        countries = tracker.get_slot("countries")
        if countries != None:
            c_text = ""
            for c in countries:
                c_text += ", " + c
            return {"countries_text": countries[0]}
        return {"countries_text": None}