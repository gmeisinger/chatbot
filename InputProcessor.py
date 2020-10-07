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

        greetings = ['hey', 'hi', 'hello', 'what\'s up']
        for x in greetings:
            if x in self.cleanText:
                return x.capitalize() + '! How can I help you?'
        
        # words indicative that user wants to view death-related info
        death_keywords = ['deaths', 'died']
        mort_rate_keywords = ['mortality']

        # indicative user wants to view gender-related info
        gender_keywords = ['men', 'women', 'girls', 'boys', 'gender', 'sex']

        return 'Huh?'

