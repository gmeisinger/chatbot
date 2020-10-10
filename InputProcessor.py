#First attempt at taking input and deciphering intent

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

        # cleaned text won't have ' anymore!
        greetings = ['hey', 'hi', 'hello', 'whats up', 'howdy']
        for x in greetings:
            if x in self.cleanText:
                return x.capitalize() + '! How can I help you?'

        #goodbye words
        goodbyes = ['goodbye', 'adios', 'have a nice day', 'I\'ll talk to you later', 'see you later', 'Hasta la vista, baby']

        #question words
        questions = ['can', 'what', 'why', 'where', 'show','where', 'when']
        
        # words indicative that user wants to view death-related info
        death_keywords = ['deaths', 'died']
        mort_rate_keywords = ['mortality']

        # indicative user wants to view gender-related info
        gender_keywords = ['men', 'women', 'girls', 'boys', 'gender', 'sex', 'males', 'females']

        #words indicative of recovery related info
        recover_words =['recover', 'recovery', 'recovered', 'survived', 'got better', 'improved']

        #words indivative of states in the US
        states = ["Alaska", "Alabama", "Arkansas", "Arizona", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine", "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina", "North Dakota", "Nebraska", "New Hampshire", "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Virginia", "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming"]

        #words indicative of countries
        Country = ['United States','Afghanistan','Albania','Algeria','American Samoa','Andorra','Angola','Anguilla','Antarctica','Antigua And Barbuda','Argentina','Armenia','Aruba','Australia','Austria','Azerbaijan','Bahamas','Bahrain','Bangladesh','Barbados','Belarus','Belgium','Belize','Benin','Bermuda','Bhutan','Bolivia','Bosnia And Herzegowina','Botswana','Bouvet Island','Brazil','Brunei Darussalam','Bulgaria','Burkina Faso','Burundi','Cambodia','Cameroon','Canada','Cape Verde','Cayman Islands','Central African Rep','Chad','Chile','China','Christmas Island','Cocos Islands','Colombia','Comoros','Congo','Cook Islands','Costa Rica','Cote D`ivoire','Croatia','Cuba','Cyprus','Czech Republic','Denmark','Djibouti','Dominica','Dominican Republic','East Timor','Ecuador','Egypt','El Salvador','Equatorial Guinea','Eritrea','Estonia','Ethiopia','Falkland Islands','Faroe Islands','Fiji','Finland','France','French Guiana','French Polynesia','French S. Territories','Gabon','Gambia','Georgia','Germany','Ghana','Gibraltar','Greece','Greenland','Grenada','Guadeloupe','Guam','Guatemala','Guinea','Guinea-bissau','Guyana','Haiti','Honduras','Hong Kong','Hungary','Iceland','India','Indonesia','Iran','Iraq','Ireland','Israel','Italy','Jamaica','Japan','Jordan','Kazakhstan','Kenya','Kiribati','North Korea','South Korea','Kuwait','Kyrgyzstan','Laos','Latvia','Lebanon','Lesotho','Liberia','Libya','Liechtenstein','Lithuania','Luxembourg','Macau','Macedonia','Madagascar','Malawi','Malaysia','Maldives','Mali','Malta','Marshall Islands','Martinique','Mauritania','Mauritius','Mayotte','Mexico','Micronesia','Moldova','Monaco','Mongolia','Montserrat','Morocco','Mozambique','Myanmar','Namibia','Nauru','Nepal','Netherlands','Netherlands Antilles','New Caledonia','New Zealand','Nicaragua','Niger','Nigeria','Niue','Norfolk Island','Northern Mariana Islands','Norway','Oman','Pakistan','Palau','Panama','Papua New Guinea','Paraguay','Peru','Philippines','Pitcairn','Poland','Portugal','Puerto Rico','Qatar','Reunion','Romania','Russian Federation','Rwanda','Saint Kitts And Nevis','Saint Lucia','St Vincent/Grenadines','Samoa','San Marino','Sao Tome','Saudi Arabia','Senegal','Seychelles','Sierra Leone','Singapore','Slovakia','Slovenia','Solomon Islands','Somalia','South Africa','Spain','Sri Lanka','St. Helena','St.Pierre','Sudan', 'Suriname','Swaziland','Sweden','Switzerland','Syrian Arab Republic','Taiwan','Tajikistan','Tanzania','Thailand','Togo','Tokelau','Tonga','Trinidad And Tobago','Tunisia','Turkey','Turkmenistan','Tuvalu','Uganda','Ukraine','United Arab Emirates','United Kingdom','Uruguay','Uzbekistan','Vanuatu','Vatican City State','Venezuela','Viet Nam','Virgin Islands','Western Sahara','Yemen','Yugoslavia','Zaire','Zambia','Zimbabwe']

        #words indacative of graphs
        graph_words = ['graph', 'line', 'line graph','scatter', 'scatter plot', 'pie', 'pie chart', 'bar', 'bar graph']

        return 'Huh?'

