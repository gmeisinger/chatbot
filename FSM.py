class FSM:
    fsm = []
    state = 0

    def __init__(self, st, delimiter='-'):
        self.fsm = st.split(delimiter)
        self.fsm.append('*')

    def __str__(self):
        st = ''
        i = 0
        for state in self.fsm:
            st += 'State ' + str(i) + ': ' + state + '\n'
            i += 1
        return st
    
    def simulate_on_input(self, st):
        if st == self.fsm[self.state]:
            self.state += 1
        else:
            self.state = 0

    def accept(self):
        if self.fsm[self.state] == '*':
            return True
        else:
            return False

    def country_string(self):
        st = ''
        for word in self.fsm:
            if word == 'and' or word == 'of':
                st += word + ' '
            elif word == '*':
                break
            else:
                st += word.capitalize() + ' '

        return st[0:len(st)-1]  # removes hanging space
