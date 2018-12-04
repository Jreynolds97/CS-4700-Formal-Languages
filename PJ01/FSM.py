import re
import os
chars=["!","\"","#","$","%","&","'","(",")","*","+",",","-",".","/","0","1","2","3","4","5","6","7","8","9",":",";","<","=",">","?","@","A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","[","\\","]","^","_","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","{","|","}","~"]
line_regex = re.compile("(\d+),(.*),(\d+)")

class Machine():
    def __init__(self, machine_file):
        """Initialize a machine given a machine text file.
        Sets most of the items to their base type and their empty
        initializations.
        It then calls the read machine function to parse the file.
        At the end, if there hasn't been any change of the machine type
        upon being processed, it sets the machine type to a DFA.
        """
        self.lookup = {}
        self.accept = []
        self.current_state = 0
        self.alphabet = set()
        self.language = []
        self.machine_type = ""
        self.states = set() 
        self.read_machine(machine_file)
        if self.machine_type == "":
            self.machine_type = "DFA"

    def reset_machine(self):
        """Set the current state of the machine to 0
        """
        self.current_state = 0

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
                if re.match("\s",line):
                    continue
                # Perform the regex match on each line using the 
                # compiled regex on line 4
                line_search = re.search(line_regex,line)
                # Try to get a character from the capture groups 
                # in the regular expression match
                try:
                    transition_char = line_search.group(2)
                except AttributeError:
                    # If we can't get a character in that group,
                    # assume epsilon transition and mark machine as
                    # an NFA
                    self.machine_type = "NFA"
                    return
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
                to_state = line_search.group(3)
                if not int(to_state) < 256:
                     self.machine_type = "INVALID"
                     return
                self.states.add(to_state)
                # If all works, add the transition character to 
                # the list of characters in the alphabet
                self.alphabet.add(transition_char)
                # If the transition character isn't one of 
                # the printable characters (or ` signifying epsilon)
                # then we treat it specially
                if transition_char not in chars:
                    if transition_char == '`':
                        self.machine_type = "NFA"
                        return
                    else:
                        self.machine_type = "INVALID"
                        return
                # Set up the lookup table
                try:
                    self.lookup[transition_char]
                except:
                    self.lookup[transition_char]={}
                
                # Set up the table for the char
                try:
                    self.lookup[transition_char][from_state]
                    self.machine_type = "NFA"
                    return
                except:
                    self.lookup[transition_char][from_state]=to_state
            

    def run_machine(self, input_string):
        if re.match("^\s+$", input_string):
            if str(self.current_state) in self.accept:
                self.language.append("\n")
                return
            else:
                return
        # run the machine with input string by performing table lookups based on
        # character and the current state
        for input_char in input_string:
            # If the character isn't valid in the alphabet, then
            # skip this string, as it's not valid in the language
            if input_char not in self.alphabet:
                return    
            try:
                self.current_state = self.lookup[str(input_char)][str(self.current_state)]
            except:
                self.current_state = 255
        if str(self.current_state) in self.accept:
            self.language.append(input_string)

if not os.path.exists(os.path.join(os.path.dirname(__file__),"results")):
    os.makedirs(os.path.join(os.path.dirname(__file__),"results"))

input_count = 0
for machine_file in os.listdir(os.path.join(os.path.dirname(__file__),"machine_files")):
    try:
        machine = Machine(os.path.join(os.path.dirname(__file__),os.path.join(os.path.join(os.path.dirname(__file__),"machine_files"), machine_file)))    
        if machine.machine_type == "DFA":
            with open(os.path.join(os.path.dirname(__file__), "input.txt"), "r") as input_file:
                input_count = 0
                for input_string in input_file:
                    input_string = input_string.strip()
                    machine.reset_machine()
                    machine.run_machine(input_string)
                    input_count += 1
                
            with open(os.path.join(os.path.join(os.path.dirname(__file__),"results"),"{}.txt".format(machine_file.replace(".fa",""))), "w+") as lang_file:
                for string in machine.language:
                    lang_file.write("{}\n".format(string))
            with open(os.path.join(os.path.join(os.path.dirname(__file__),"results"),"{}.log".format(machine_file.replace(".fa",""))), "w+") as log_file:
                log_file.write("Valid: {}\n".format(machine.machine_type))
                log_file.write("States: {}\n".format(len(machine.states)))
                log_file.write("Alphabet: {}\n".format(''.join(sorted(machine.alphabet))))
                log_file.write("Accepted Strings: {} / {}\n".format(len(machine.language), input_count))

    except IOError as e:
        pass