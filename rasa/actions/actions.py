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
from rasa_sdk.events import SlotSet, FollowupAction, EventType

from typing import Dict, Text, List
from datetime import date

import requests
import json
import pygal

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
            #fa = FollowupAction(name="case_count_form")
            #return [fa]
        case_type = tracker.get_slot('case_type')
        if case_type == None:
            case_type = "confirmed"
            #fa = FollowupAction(name="case_count_form")
            #return [fa]
        country = tracker.get_slot('countries')
        # get data from api
        r = requests.get("https://api.covid19api.com/summary")
        summary = r.json()
        # target a country
        countries = summary['Countries']
        if country == None:
            data = summary['Global']
        else:
            country = country[0]
            data = next((item for item in countries if (item['Slug'] == country or item['Country'] == country)), None)
        key_string = scope.capitalize() + case_type.capitalize()
        count = data[key_string]
        # report the information
        dispatcher.utter_message(
            template="utter_case_count",
            count=count,
            scope=scope,
            case_type=case_type,
            country=country
        )
        #return [slot_scope, slot_case_type, slot_country, slot_count, evt]
        return []

class ActionCaseCountMultCountry(Action):

    @staticmethod
    def required_fields():
        return [
            #EntityFormField("scope", "scope"),
            #EntityFormField("case_type", "case_type"),
            EntityFormField("countries", "countries")
        ]

    def name(self):
        return "action_case_count_multiple_country"
    
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
            dispatcher.utter_message(
                template="utter_case_count",
                count=count,
                scope=scope,
                case_type=case_type,
                country=country
            )
        else:
            text = "There are "
            for x in country:
                data = next((item for item in countries if (item['Slug'] == x or item['Country'] == x)), None)
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

            # if len(country) == 2: #try with just 2 to make sure it can work
            #     data1 = next((item for item in countries if (item['Slug'] == country[0] or item['Country'] == country[0])), None)
            #     key_string1 = scope.capitalize() + case_type.capitalize()
            #     count1 = data1[key_string1]
            #     data2 = next((item for item in countries if (item['Slug'] == country[1] or item['Country'] == country[1])), None)
            #     key_string2 = scope.capitalize() + case_type.capitalize()
            #     count2 = data2[key_string1]
            #     # report the information
            #     slot_scope = SlotSet(key='scope', value=scope)
            #     slot_case_type = SlotSet(key='case_type', value=case_type)
            #     slot_country = SlotSet(key='country1', value=country[0])
            #     slot_country = SlotSet(key='country2', value=country[1])
            #     slot_count = SlotSet(key='count1', value=count1)
            #     slot_count = SlotSet(key='count2', value=count2)
            #     evt = FollowupAction(name = "utter_case_count_two_country")
            #     dispatcher.utter_message(
            #         template="utter_case_count_two_country",
            #         count1=count1,
            #         count2=count2,
            #         scope=scope,
            #         case_type=case_type,
            #         country1=country[0],
            #         country2=country[1]
            #     )
            # else:
            #     dispatcher.utter_message(text="Well why didnt this work?")
        #return [slot_scope, slot_case_type, slot_country, slot_count, evt]
        return []

class ActionCaseSummaryGraph(Action):
    @staticmethod
    def required_fields():
        return [
            EntityFormField("country", "country")
        ]

    def name(self):
        return "action_case_summary_graph"

    def Linechart(self, title, data, value_tag, label_tag):
        line_chart = pygal.Line()
        line_chart.title = title

        # changes
        for category in data:
            data_num = []
            for entry in category:
                data_num.append(int(entry[value_tag]))
            line_chart.add(str(category[0][label_tag]), data_num)

        return line_chart.render_data_uri()

    def run(self, dispatcher, tracker, domain):
        case_type = tracker.get_slot('case_type')
        if case_type == None:
            case_type = "confirmed"

        country = tracker.get_slot('country')
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
        qstring = "https://api.covid19api.com/dayone/country/" + slug + "/status/" + case_type

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
            title = case_type.capitalize() + ' Cases in' + data['Country']
            # vtag = case_type
        linechart = self.Linechart(title, [dayone], vtag, ltag)
        dispatcher.utter_message(
            template='utter_case_count',
            image=linechart,
            scope=scope,
            case_type=case_type,
            country=country)
        return []

class ActionCaseCountByTime(Action):

    @staticmethod
    def required_fields():
        return [
            #EntityFormField("scope", "scope"),
            #EntityFormField("case_type", "case_type"),
            EntityFormField("countries", "countries")
        ]

    def name(self):
        return "action_case_count_by_time"
    
    def run(self, dispatcher, tracker, domain): #note to jake, figure out why bysubtime isnt getting pulled in
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
        by_sub_time = tracker.get_slot('bysubtime')
        if by_time == None:
            by_time = "month"
        if by_time == "day" and by_sub_time == None:
            by_sub_time = "january" #if they ask by day but dont specify... default to january?
        text = ""
        if by_time == "month":
            r = ""
            counts = {}
            currentMonth = date.today().strftime("%m")
            if country == "world":
                for x in range(1,13):
                    counts[x] = 0
                text = "Globally there have been "
                r = requests.get("https://api.covid19api.com/countries")
                summary = r.json()
                for x in summary:
                    country = x["Country"]
                    r2 = requests.get("https://api.covid19api.com/country/" + country + "/status/" + case_type + "?from=2020-03-01T00:00:00Z&to=2020-" + currentMonth + "-01T00:00:00Z")
                    summary2 = r2.json()
                    m = 3
                    for y in summary2:
                        if int(y["Date"][5:7]) == m:
                            m += 1
                            counts[m] = counts[m] + y["Cases"]

            else:
                text = "In " + country + " there have been "
                r = requests.get("https://api.covid19api.com/country/" + country + "/status/" + case_type + "?from=2020-03-01T00:00:00Z&to=2020-" + currentMonth + "-01T00:00:00Z")
                summary = r.json()
                m = 3
                if summary[0]["Province"] == "":
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
                text = text + str(counts[x]) + " " + scope + " " + case_type + " in "
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
        else:
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
                #  stuff
                text = "Globally there have been "
            else:
                text = "In " + country + " there have been "
                r = requests.get("https://api.covid19api.com/country/" + country + "/status/" + case_type + "?from=2020-" + month + "-01T00:00:00Z&to=2020-" + month + "-" + day + "T00:00:00Z")
                summary = r.json()
                d = 1
                if summary[0]["Province"] == "":
                    for x in summary:
                        if int(x["Date"][8:10] == d):
                            d += 1
                            counts[m] = x["Cases"]
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
                    text = text + str(counts[x]) + " " + scope + " " + case_type + " on " + str(by_sub_time) + " " + str(x)
                    if str(x)[-1] == "1":
                        text = text + "st"
                    elif str(x)[-1] == "2":
                        text = text + "nd"
                    elif str(x)[-1] == "3":
                        text = text + "rd"
                    else:
                        text = text + "th"
                    
                    if int(day) == d + 1:
                        text = text + ", and "
                    elif int(day) != d:
                        text = text + ", "
                    d += 1
                text = text + "."
        dispatcher.utter_message(text = text)
        # report the information
        # slot_scope = SlotSet(key='scope', value=scope)
        # slot_case_type = SlotSet(key='case_type', value=case_type)
        # slot_country = SlotSet(key='country', value=country)
        # slot_count = SlotSet(key='count', value=count)
        # evt = FollowupAction(name = "utter_case_count")
        # dispatcher.utter_message(
        #     template="utter_case_count",
        #     count=count,
        #     scope=scope,
        #     case_type=case_type,
        #     country=country
        # )
        #return [slot_scope, slot_case_type, slot_country, slot_count, evt]
        return []