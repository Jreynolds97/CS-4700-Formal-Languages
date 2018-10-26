import io
import os
from transition import transitions

cwd = os.path.dirname(__file__)
results_folder = os.path.join(cwd,"results")
jackfile_folder = os.path.join(cwd,"jack_files")

SY_OP = ['+', '*', '/', '&', '|', '<', '>']

def get_col(in_char):
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
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)
    for jackfile in os.listdir(jackfile_folder):
        filename = os.fsdecode(jackfile)
        with open(os.path.join(jackfile_folder,filename)) as f:
            print(filename)
            tokens = []
            current_char = ' '
            col = 'INITIAL'
            current_state = 'INITIAL'
            prev_state = 'INITIAL'
            current_token = ''
            x = 0
        
            current_char = f.read(1)
            while True:
                if current_char == '':
                    break
                col = get_col(current_char)
                try:
                    current_state = transitions[current_state][col]
                except:
                    try:
                        current_state = transitions[current_state]['*']
                    except:
                        current_state = 'INITIAL'
                # print(current_char, current_token, current_state)
                I=0
                if(current_state == 'INITIAL'):
                    if(prev_state in ['SLASH', 'STAR']):
                        tokens.append((current_token, 'SY_OP'))
                    elif('COMMENT' in prev_state):
                        continue
                    elif('IDENT' in prev_state):
                        tokens.append((current_token, 'IDENT'))
                    elif('INTEGER' in prev_state):
                        tokens.append((current_token, 'INTEGER'))
                    elif(prev_state not in ['SPACE', 'NEWLINE']):
                        tokens.append((current_token, prev_state))
                    current_token = ''
                else:
                    current_token += current_char
                    current_char = f.read(1)
                prev_state = current_state
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
                tok_file.write("{}\t{}\n".format(token[1],token[0]))
