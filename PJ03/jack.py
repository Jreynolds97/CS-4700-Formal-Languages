import io
import os
from transition import transitions

cwd = os.path.dirname(__file__)
results_folder = os.path.join(cwd,"results")
jackfile_folder = os.path.join(cwd,"jack_files")

SY_OP = ['+', '*', '/', '&', '|', '<', '>']

def tranform(in_char):
    """Transform maps tokens to their state name to make it easier
    to read the state table

    Parameters
    ----------
    in_char : character
        The character to map to a state name
    """
    in_char = str(in_char)
    if(in_char in ['\r', '\n', '\r\n']):
        return 'NEWLINE'
    elif(in_char in '/'):
        return 'SLASH'
    elif(in_char in '*'):
        return 'STAR'
    elif(in_char in '"'):
        return 'QUOTE'
    elif(in_char.isspace()):
        return 'SPACE'
    elif(in_char.isdigit()):
        return in_char
    elif(in_char.isalpha()):
        return in_char
    elif(in_char in '_'):
        return 'UNDERSCORE'
    elif(in_char == '('):
        return 'SY_LPAREN'
    elif(in_char == ')'):
        return 'SY_RPAREN'
    elif(in_char == '['):
        return 'SY_LBRACKET'
    elif(in_char == ']'):
        return 'SY_RBRACKET'
    elif(in_char == '{'):
        return 'SY_LBRACE'
    elif(in_char == '}'):
        return 'SY_RBRACE'
    elif(in_char == ';'):
        return 'SY_SEMI'
    elif(in_char == '.'):
        return 'SY_PERIOD'
    elif(in_char == ','):
        return 'SY_COMMA'
    elif(in_char == '='):
        return 'SY_EQ'
    elif(in_char == '-'):
        return 'SY_MINUS'
    elif(in_char == '~'):
        return 'SY_NOT'
    elif(in_char in SY_OP):
        return 'SY_OP'
    return 'BADTOKEN'

if __name__ == '__main__':
    # Make the results folder if it doesn't exist
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)
    # Loop through each of the .jack files in the jackfile folder
    for jackfile in os.listdir(jackfile_folder):
        # Decode the filename if it has special OS encoding
        filename = os.fsdecode(jackfile)
        with open(os.path.join(jackfile_folder,filename)) as f:
            # Initial setup of the DFA with an empty char, and the initial state
            tokens = []
            current_char = ' '
            char_transition = 'INITIAL'
            current_state = 'INITIAL'
            prev_state = 'INITIAL'
            current_token = ''
        
            # Read the first character from the file
            current_char = f.read(1)
            while True:
                # Detect if the character was empty, as that is how Python represensts EOF
                if current_char == '':
                    break
                # Get the character transiton from the transform function
                char_transition = tranform(current_char)
                # The logic to keep the transition table small. 
                # This is akin to the logic that I used in PJ01 for the trap state transitions
                try:
                    # If there exists a proper transition for the current state and char, take it
                    current_state = transitions[current_state][char_transition]
                except:
                    # Otherwise, try getting the '*' transition from the table
                    try:
                        current_state = transitions[current_state]['*']
                    except:
                    # If all else fails, the machine doesn't have an explicit transition for the
                    # character, and doesn't have a redirected wildcard, so return to the initial
                    # state to read the next token properly
                        current_state = 'INITIAL'

                # If the current state the machine is in is the INITIAL state, then we've 
                # finished a token, and need to determine what category the token is in
                if(current_state == 'INITIAL'):
                    # The previous state variable is what allows for maxmunch and for
                    # the distinguishing of token type. 

                    # If the state is one of the unique SLASH or STAR states, then it's a 
                    # system operator
                    if(prev_state in ['SLASH', 'STAR']):
                        tokens.append((current_token, 'SY_OP'))
                    # If it's a comment we ignore it in the write out
                    elif('COMMENT' in prev_state):
                        continue
                    # There are many identifier states that are used for distinguishing
                    # different identifiers within the keywords. So if we're in ANY of those
                    # states, we have an identifier
                    elif('IDENT' in prev_state):
                        tokens.append((current_token, 'IDENT'))
                    # The same with identifiers is true for integers
                    elif('INTEGER' in prev_state):
                        tokens.append((current_token, 'INTEGER'))
                    # If the previous state was a space character, just ignore it. Otherwise
                    # write the full token and the previous state to the token list
                    elif(prev_state not in ['SPACE', 'NEWLINE']):
                        tokens.append((current_token, prev_state))
                    # After writing a token (or not) to the token file, reset the token 
                    # to an empty character to properly be able to read the next token. 
                    # This ALSO does not read from the file, which allows us to us the
                    # character that we just read to determine where it would go
                    # properly. 
                    current_token = ''
                else:
                    # If we haven't returned to the initial state, we're still in the same
                    # maxed munched token, so we append the character to the token and 
                    # read the next character from the file
                    current_token += current_char
                    current_char = f.read(1)
                # remember where we are in the previous state variable so if we reach the end
                # of the token, we remember what token type we read
                prev_state = current_state

            # Do the writing logic again, but at the very end of the file
            if(current_state not in ['SPACE','NEWLINE'] and current_token != ''):
                if(prev_state in ['SLASH', 'STAR']):
                    tokens.append((current_token, 'SY_OP'))
                elif('COMMENT' in prev_state):
                    pass
                elif('IDENT' in prev_state):
                        tokens.append((current_token, 'IDENT'))
                elif('INTEGER' in prev_state):
                    tokens.append((current_token, 'INTEGER'))
                else:
                    tokens.append((current_token, prev_state))

        with open(os.path.join(results_folder,"{}.tok".format(filename.replace('.jack',''))),'w+') as tok_file:
            for token in tokens:
                tok_file.write("{},{}\n".format(token[1],token[0]))
