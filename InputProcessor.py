#First attempt at taking input and deciphering intent
import requests as req
from FSM import FSM

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

        #goodbye words
        goodbyes = ['goodbye', 'adios', 'have a nice day', 'I\'ll talk to you later', 'see you later', 'Hasta la vista, baby']

        #question words
        questions = ['can', 'what', 'why', 'where', 'show','where', 'when']
        
        # words indicative that user wants to view death-related info
        death_keywords = ['deaths', 'death', 'died', 'fatalities', 'lost']
        mort_rate_keywords = ['mortality']

        # case related keywords
        case_keywords = ['case', 'cases']

        # indicative user wants to view gender-related info
        gender_keywords = ['men', 'women', 'man', 'woman', 'girl', 'boy', 'girls', 'boys', 'gender', 'sex']
        
        # words indicating user wants to see comparison between two things
        comp_keywords = ['difference', 'compare', 'comparison', 'between', 'different', 'than', 'vs']

        # keywords related to age
        age_keywords = ['elderly', 'young', 'old', 'children', 'kids', 'adults']

        #words indicative of recovery related info
        recover_words =['recover', 'recovery', 'recovered', 'survived', 'got better', 'improved']

        #words indivative of states in the US
        states = ["Alaska", "Alabama", "Arkansas", "Arizona", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine", "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina", "North Dakota", "Nebraska", "New Hampshire", "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Virginia", "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming"]

        #words indicative of countries
        Country = ['United States','Afghanistan','Albania','Algeria','American Samoa','Andorra','Angola','Anguilla','Antarctica','Antigua And Barbuda','Argentina','Armenia','Aruba','Australia','Austria','Azerbaijan','Bahamas','Bahrain','Bangladesh','Barbados','Belarus','Belgium','Belize','Benin','Bermuda','Bhutan','Bolivia','Bosnia And Herzegowina','Botswana','Bouvet Island','Brazil','Brunei Darussalam','Bulgaria','Burkina Faso','Burundi','Cambodia','Cameroon','Canada','Cape Verde','Cayman Islands','Central African Rep','Chad','Chile','China','Christmas Island','Cocos Islands','Colombia','Comoros','Congo','Cook Islands','Costa Rica','Cote D`ivoire','Croatia','Cuba','Cyprus','Czech Republic','Denmark','Djibouti','Dominica','Dominican Republic','East Timor','Ecuador','Egypt','El Salvador','Equatorial Guinea','Eritrea','Estonia','Ethiopia','Falkland Islands','Faroe Islands','Fiji','Finland','France','French Guiana','French Polynesia','French S. Territories','Gabon','Gambia','Georgia','Germany','Ghana','Gibraltar','Greece','Greenland','Grenada','Guadeloupe','Guam','Guatemala','Guinea','Guinea-bissau','Guyana','Haiti','Honduras','Hong Kong','Hungary','Iceland','India','Indonesia','Iran','Iraq','Ireland','Israel','Italy','Jamaica','Japan','Jordan','Kazakhstan','Kenya','Kiribati','North Korea','South Korea','Kuwait','Kyrgyzstan','Laos','Latvia','Lebanon','Lesotho','Liberia','Libya','Liechtenstein','Lithuania','Luxembourg','Macau','Macedonia','Madagascar','Malawi','Malaysia','Maldives','Mali','Malta','Marshall Islands','Martinique','Mauritania','Mauritius','Mayotte','Mexico','Micronesia','Moldova','Monaco','Mongolia','Montserrat','Morocco','Mozambique','Myanmar','Namibia','Nauru','Nepal','Netherlands','Netherlands Antilles','New Caledonia','New Zealand','Nicaragua','Niger','Nigeria','Niue','Norfolk Island','Northern Mariana Islands','Norway','Oman','Pakistan','Palau','Panama','Papua New Guinea','Paraguay','Peru','Philippines','Pitcairn','Poland','Portugal','Puerto Rico','Qatar','Reunion','Romania','Russian Federation','Rwanda','Saint Kitts And Nevis','Saint Lucia','St Vincent/Grenadines','Samoa','San Marino','Sao Tome','Saudi Arabia','Senegal','Seychelles','Sierra Leone','Singapore','Slovakia','Slovenia','Solomon Islands','Somalia','South Africa','Spain','Sri Lanka','St. Helena','St.Pierre','Sudan', 'Suriname','Swaziland','Sweden','Switzerland','Syrian Arab Republic','Taiwan','Tajikistan','Tanzania','Thailand','Togo','Tokelau','Tonga','Trinidad And Tobago','Tunisia','Turkey','Turkmenistan','Tuvalu','Uganda','Ukraine','United Arab Emirates','United Kingdom','Uruguay','Uzbekistan','Vanuatu','Vatican City State','Venezuela','Viet Nam','Virgin Islands','Western Sahara','Yemen','Yugoslavia','Zaire','Zambia','Zimbabwe']

        #words indacative of graphs
        graph_words = ['graph', 'line', 'line graph','scatter', 'scatter plot', 'pie', 'pie chart', 'bar', 'bar graph']

        
        # keywords related to global numbers
        glob_keywords = ['internationally', 'globally']

        # keywords related to time
        months = ['january', 'february', 'march', 'april', 'may', 'june', 'july',
                'august', 'september', 'october', 'november', 'december']

        rel_time_keywords = ['yesterday', 'today']

        # keywords related to countries
        r = req.get("https://api.covid19api.com/countries")
        data = r.json()
        countries = []
        for country in data:
            country_slug = country['Slug'] # e.g. united-states
            countries.append(FSM(country_slug))

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

        for x in greetings:
            if x in self.cleanText:
                ret_string += x.capitalize() + '. '

    
        
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
            # simulate country FSMs on current word
            for fsm in countries:
                fsm.simulate_on_input(word)
                if fsm.accept():
                    intents['countries'] += fsm.country_string() + ', '
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

