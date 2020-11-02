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
#from rasa_sdk.events import 

import requests
import json

# this action gets a case count for a specific country.
# case types are (Confirmed, Recovered, Deaths)
# scope is (Total, New)
# country needs to be a slug
class ActionCaseCount(Action):

    #@staticmethod
    #def required_fields():
    #    return [
    #        EntityFormField("scope", "scope"),
    #        EntityFormField("case_type", "case_type"),
    #        EntityFormField("country", "country")
    #    ]

    def name(self):
        return "action_case_count"
    
    def run(self, dispatcher, tracker, domain):
        # get data
        scope = tracker.get_slot('scope')
        case_type = tracker.get_slot('case_type')
        country = tracker.get_slot('country')
        summary = get_summary()
        # target a country
        countries = summary['Countries']
        data = next((item for item in countries if (item['Slug'] == country or item['Country'] == country)), None)
        key_string = scope.capitalize() + case_type.capitalize()
        count = data[key_string]
        # report the information
        slot_scope = SlotSet(key='scope', value=scope)
        slot_case_type = SlotSet(key='case_type', value=case_type)
        slot_country = SlotSet(key='country', value=country)
        slot_count = SlotSet(key='count', value=count)
        evt = FollowupAction(name = "utter_case_count")
        #dispatcher.utter_message(
        #    template="utter_case_count",
        #    count=count,
        #    scope=scope,
        #    case_type=case_type,
        #    country=country
        #)
        return [slot_scope, slot_case_type, slot_country, slot_count, evt]
    
    # gets daily summary, which contains new and total case data globally and for each country
    # dict with keys "Global", "Countries", "Date", "Message"
    def get_summary():
        r = requests.get("https://api.covid19api.com/summary")
        data = r.json()
        return data