#First attempt at taking input and deciphering intent
import requests as req

class InputProcessor:
    """A class created with the intent of processing user input for SCITalk Chatbot"""
    
    cleanText = []  # initialized to empty list, will hold list of words as
                    # produced by clean_text function in app.py

    def __init__(self, cleaned_text):
        self.cleanText = cleaned_text

    def process(self):
        """Starts input processing rules. This is nowhere near a finished product.
           At the moment, it returns text to be output by the chatbot. The end goal
           is to have it output a structure that can be utilized by a content planner
           to begin constructing an intelligent response."""
        
        ret_string = '' # string to return

        greetings = ['hey', 'hi', 'hello']
        for x in greetings:
            if x in self.cleanText:
                ret_string += x.capitalize() + '. '
        
        # words indicative that user wants to view death-related info
        death_keywords = ['deaths', 'death', 'died', 'fatalities', 'lost']
        mort_rate_keywords = ['mortality']

        # case related keywords
        case_keywords = ['case', 'cases']

        # indicative user wants to view gender-related info
        gender_keywords = ['men', 'women', 'girls', 'boys', 'gender', 'sex']
        
        # words indicating user wants to see comparison between two things
        comp_keywords = ['difference', 'compare', 'comparison', 'between', 'different', 'than', 'vs']

        # keywords related to age
        age_keywords = ['elderly', 'young', 'old', 'children', 'kids', 'adults']

        # keywords related to countries
        r = req.get("https://api.covid19api.com/countries")
        data = r.json()
        countries = []
        for country in data:
            countries.append(country['Slug'])
        '''
            To represent multi-word countries, I'm going to build finite state machines.
            For example: the FSM for United Kingdom will have 3 states (e.g. 0,1,2). It will
            be initialized to state 0, when we come across 'united' in the cleaned text, it
            will transition to state 1. In state 1, 'kingdom' will cause a transition to
            state 2. State 2 will be the accept state, then united-kingdom will be marked in
            the input!! One word countries will be represented as 2-state FSMs. This will create
            some memory overhead for sure, but I think it's about as good as we can get with
            respect to time-complexity. Let me know if you think we can improve upon this!
            - Andrew
        '''
        # keywords related to global numbers
        glob_keywords = ['internationally', 'globally']

        # keywords related to time
        months = ['january', 'february', 'march', 'april', 'may', 'june', 'july',
                'august', 'september', 'october', 'november', 'december']

        rel_time_keywords = ['yesterday', 'today']
        
        # this loop will be where we decipher user intent
        intents = {}    # dict holding boolean values
                        # if True, user wants to view info related to
                        # respective key
        intents['death'] = False
        intents['mortality'] = False
        intents['cases'] = False
        intents['gender'] = False
        intents['comparison'] = False
        intents['age'] = False
        intents['month'] = ''
        intents['country'] = ''
        intents['global'] = False

        for word in self.cleanText:
            if word in death_keywords:
                intents['death'] = True
            if word in mort_rate_keywords:
                intents['mortality'] = True
            if word in case_keywords:
                intents['cases'] = True
            if word in gender_keywords:
                intents['gender'] = True
            if word in comp_keywords:
                intents['comparison'] = True
            if word in age_keywords:
                intents['age'] = True
            if word in months:
                intents['month'] += word.capitalize() + ', '
            if word in countries:
                intents['country'] += word.capitalize() + ', '
            if word in glob_keywords:
                intents['global'] = True
        
        ret_string += 'You want information related to: '
        for val in intents:
            if intents[val] is True:
                ret_string += val.capitalize() + ', '
            elif (val == 'month' or val == 'country') and intents[val] != '':
                ret_string += intents[val]
        
        return ret_string

    def __build_country_fsms(self, slugs):
        '''
        Private method to build FSMs for country detection in 
        user input
        '''

