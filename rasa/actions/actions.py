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
from rasa_sdk.events import SlotSet, FollowupAction

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
            EntityFormField("country", "country")
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
        key_string = scope.capitalize() + case_type.capitalize()
        count = data[key_string]
        # report the information
        slot_scope = SlotSet(key='scope', value=scope)
        slot_case_type = SlotSet(key='case_type', value=case_type)
        slot_country = SlotSet(key='country', value=country)
        slot_count = SlotSet(key='count', value=count)
        evt = FollowupAction(name = "utter_case_count")
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
            slot_scope = SlotSet(key='scope', value=scope)
            slot_case_type = SlotSet(key='case_type', value=case_type)
            slot_country = SlotSet(key='country', value=country)
            slot_count = SlotSet(key='count', value=count)
            evt = FollowupAction(name = "utter_case_count")
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
            EntityFormField("countries", "countries")
        ]

    def name(self):
        return "action_case_summary_graph"

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
        vtag = ''
        ltag = 'Country'
        if case_type == 'deaths':
            title = 'Deaths in ' + data['Country']
            vtag = 'Deaths'
        else:
            title = case_type.capitalize() + ' Cases in' + data['Country']
            vtag = case_type.capitalize() + ' Cases'
        linechart = Linechart(title, [dayone], vtag, ltag)
        dispatcher.utter_message(image=linechart)
        return []