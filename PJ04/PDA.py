import re
import os
chars=[' ',"`","!","\"","#","$","%","&","'","(",")","*","+",",","-",".","/","0","1","2","3","4","5","6","7","8","9",":",";","<","=",">","?","@","A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","[","\\","]","^","_","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","{","|","}","~"]
line_regex = re.compile(r"(\d+),(.*),(.*),(\d+),(.*)")

class DPDA():
    def __init__(self, machine_file):
        """Initialize a machine given a machine text file.
        Sets most of the items to their base type and their empty
        initializations.
        Much like the implementation for Finite Automata,
        reads an input file to make the transition table.
        """
        self.TIMEOUT = 10000
        self.lookup = {}
        self.stack = []
        self.input = ''
        self.accept = []
        self.current_state = 0
        self.alphabet = set()
        self.stack_alpha = set()
        self.language = []
        self.machine_type = ""
        self.states = set() 
        self.read_machine(machine_file)
        self.validate_determinism()
        if self.machine_type == "":
            self.machine_type = "DPDA"

    def reset_machine(self):
        """Set the current state of the machine to 0
        """
        self.current_state = 0
        self.stack = []
        self.input = ''

    def validate_determinism(self):
        """Validates the determinism of the PDA using the rules for a DPDA.
            Because the machine can only have one transition rule per input char/pop char pair
            when it is read in, we only need to verify that there do not exist
            epsilon transitions where other transitions ALSO exist on the same inputs.
        """
        for from_state in self.lookup:
            pop_chars = []
            for x in self.lookup[from_state]:
                pop_chars.append((x,self.lookup[from_state][x].keys()))
            pop_chars = sorted(pop_chars)
            for i in range(len(pop_chars)-1):
                if pop_chars[i] == pop_chars[i+1]:
                    self.machine_type = "NPDA"
                    return
        

    def read_machine(self, machine_file):
        """Reads a machine and collects metrics based off a
        machine file.
        """
        with open(machine_file, "r+") as definition:
            try:
                # Try reading the list of accept states from the
                # first line of the file
                self.accept = re.search("{(.+?)}", definition.readline()).group(1).split(",")
            except AttributeError:
                # If we can't, we don't care. DFA can have no accept 
                # states and still be valid.
                pass
            for i in self.accept:
                # Check that each accept state is a valid state
                # 0-255
                if not int(i) < 256:
                    self.machine_type = "INVALID"
                    return
            for line in definition:
                # If a line is empty, skip it because typos can exist
                if re.match(r"\s",line):
                    continue
                # Perform the regex match on each line using the 
                # compiled regex on line 4
                line_search = re.search(line_regex,line)
                # Try to get a character from the capture groups 
                # in the regular expression match
                try:
                    transition_char = line_search.group(2)
                except AttributeError:
                    # If there isn't anything in the character
                    # capture group, then we don't have a transition
                    # character, and the PDA is invalid
                    self.machine_type = "INVALID"
                    return
                try:
                    pop_char = line_search.group(3)
                except AttributeError:
                    # If we aren't given any character to pop, assume that
                    # we are supposed to pop nothing. Perfectly 
                    # normal behaviour
                    pop_char = '`'
                # Verify that both the beginning state and the
                # state to transition to are valid states
                # in the same way as the accept states
                # and add that state to the list
                # of states if it is valid
                from_state = line_search.group(1)
                if not int(from_state) < 256:
                     self.machine_type = "INVALID"
                     return
                self.states.add(from_state)
                to_state = line_search.group(4)
                if not int(to_state) < 256:
                     self.machine_type = "INVALID"
                     return
                self.states.add(to_state)
                # Get the character to push onto the stack
                try:
                    push_char = line_search.group(5).strip()
                except AttributeError:
                    # Like the pop char, if we don't get anything
                    # to push onto the stack, just assume it's an epsilon
                    push_char = '`'
                to_tuple = (to_state, push_char)
                # If all works, add the transition character to 
                # the list of characters in the alphabet
                self.alphabet.add(transition_char)
                self.stack_alpha.add(push_char)
                self.stack_alpha.add(pop_char)
                # If the transition character isn't one of 
                # the printable characters then the machine is invalid
                if transition_char not in chars:
                    if transition_char == '`':
                        pass
                    else:
                        self.machine_type = "INVALID"
                        return

                # Set up transition table
                try:
                    self.lookup[from_state]
                except:
                    self.lookup[from_state] = {}
                
                # Add character transitions to those states
                try:
                    self.lookup[from_state][transition_char]
                except:
                    self.lookup[from_state][transition_char] = {}
                
                # Add stack pop symbols to the transition
                try:
                    # If we have multiple (different) transitions for the same input character on the same
                    # character we've popped from the stack, we're non deterministic
                    self.lookup[from_state][transition_char][pop_char]
                    if(to_tuple != self.lookup[from_state][transition_char][pop_char]):
                        self.machine_type = 'NPDA'
                except:
                    self.lookup[from_state][transition_char][pop_char] = to_tuple
            

    def run_machine(self, input_string):
        if re.match(r"^\s+$", input_string):
            if str(self.current_state) in self.accept:
                self.language.append("\n")
                return
            else:
                return
        # Initialize transitions so we can properly exit when there are too many transitions taken
        transitions = 0
        # Convert the reversed string to a list to make it mutable
        # Reversing it allows us to better use list operations to deal with the string
        self.input = input_string
        input_string = list(reversed(input_string))
        # run the machine with input string by performing table lookups based on
        # character and the current state
        # ALWAYS start by pushing a ` onto the stack so we know we can pop something off
        # While we have a character in the input string, we keep running
        while input_string and transitions < self.TIMEOUT:
            transitions += 1
            input_char = input_string.pop()
            # If the character isn't valid in the alphabet, then
            # skip this string, as it's not valid in the language
            if input_char not in self.alphabet:
                return
            try:
                stack_char = self.stack.pop()
            except IndexError:
                stack_char = '`'
            try:
                if '`' in self.lookup[str(self.current_state)].keys():
                    if stack_char in self.lookup[str(self.current_state)]['`']:
                        # If there exists an epsilon transition, don't read a character (put it back in the list)
                        # and do the logic with the epsilon transition
                        input_string.append(input_char)
                        input_char = '`'
            except KeyError:
                pass
            try:
                char_list = self.lookup[str(self.current_state)][input_char].keys()
                if '`' in char_list:
                    # Replace the stack char onto the stack to emulate an epislon transition
                    if stack_char is not '`':
                        self.stack.append(stack_char)
                    to_tuple = self.lookup[str(self.current_state)][input_char]['`']
                    # Set the state to be the state stored in the tuple
                    self.current_state = to_tuple[0]
                    # Add the character stored in the tuple to the stack
                    # if it is not the epsilon
                    if to_tuple[1] is not '`':
                        self.stack.append(to_tuple[1])
                else:
                    try:
                        to_tuple = self.lookup[str(self.current_state)][input_char][str(stack_char)]
                        self.current_state = to_tuple[0]
                        if to_tuple[1] is not '`':
                            self.stack.append(to_tuple[1])
                    except:
                        self.current_state = 255
                        self.stack.append('`')
            except:
                # If there isn't a lookup, we can just go to the trap state and write a ` to the stack
                self.current_state = 255
                self.stack.append('`')
        try:
            while '`' in self.lookup[self.current_state].keys() and transitions < self.TIMEOUT and self.current_state != 255:
                transitions += 1
                if self.stack:
                    stack_char = self.stack.pop()
                else:
                    stack_char = '`'
                try:
                    to_tuple = self.lookup[self.current_state]['`'][stack_char]
                    self.current_state = to_tuple[0]
                    if to_tuple[1] is not '`':
                        self.stack.append(to_tuple[1])
                except:
                    self.current_state = 255

        except:
            pass
        if str(self.current_state) in self.accept and transitions != self.TIMEOUT:
            self.language.append(self.input)

for machine_file in os.listdir(os.path.dirname(__file__)):
    input_count = 0
    if "04.pda" not in machine_file:
        continue
    try:
        machine = DPDA(os.path.join(os.path.dirname(__file__),machine_file))
        if machine.machine_type == "DPDA":
            with open(os.path.join(os.path.dirname(__file__), "strings.txt"), "r") as input_file:
                input_count = 0
                for input_string in input_file:
                    input_string = input_string.strip()
                    machine.reset_machine()
                    machine.run_machine(input_string)
                    input_count += 1
                
        with open(os.path.join(os.path.join(os.path.dirname(__file__),"results"),"{}.txt".format(machine_file.replace(".pda",""))), "w+") as lang_file:
            for string in machine.language:
                lang_file.write("{}\n".format(string))
        with open(os.path.join(os.path.join(os.path.dirname(__file__),"results"),"{}.log".format(machine_file.replace(".pda",""))), "w+") as log_file:
            log_file.write("Valid: {}\n".format(machine.machine_type))
            log_file.write("States: {}\n".format(len(machine.states)))
            log_file.write("Input Alphabet: {}\n".format(''.join(sorted([x for x in machine.alphabet if x is not '`']))))
            log_file.write("Stack Alphabet: {}\n".format(''.join(sorted([x for x in machine.stack_alpha if x is not '`']))))
            log_file.write("Accepted Strings: {} / {}\n".format(len(machine.language), input_count))
    except IOError as e:
        pass
