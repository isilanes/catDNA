import re
import sys
import System as S

#----------------------------------------------------------------------#

def fen2str(fen):
    string = ''
    for char in fen:
        # we add w, because sometimes the FEN is appended with w or b
        # (who moves next)
        if char in 'pnbrqkPNBRQKw':
            string += char
        elif char == '/':
            pass
        else: # else, it's a number of blanks
            for x in range(int(char)):
                string += '.'

        # For when w or b where appended to FEN:
        string = string[:64]

    return string

#----------------------------------------------------------------------#

def show_str(string):
    print('')
    for i in range(8):
        line = string[i*8:i*8+8]
        chars = [ x for x in line ]
        line = ' '.join(chars)
        print(line)

#----------------------------------------------------------------------#

class Correlation:
    '''Holds correlation (statistical) data conveniently.'''

#----------------------------------------------------------------------#

# Use pgn-extract to obtain fen.out:
cmnd = '$HOME/soft/pgn-extract/pgn-extract --fencomments run.pgn > fen.out'
S.cli(cmnd)

# Variables:
fn   = 'fen.out'
won  = 0 # who won: 0 = no one, 1 = white, 2 = black
read = False

# Read file:
with open(fn, 'r') as f:
    for line in f:
        if 'Result' in line:
            string = ''
            if '1-0' in line:
                won = 1
            elif '0-1' in line:
                won = 2
            else:
                won = 0

        if won: # only when someone won
            if '1.' in line:
                read = True

            if read:
                if line == '\n': # stop reading
                    read = False

                    # Once all lines read:
                    m = re.findall('{[^}]*}', string)
                    for e in m:
                        fen = e.split()[1]
                        mfen = fen.split('/')
                        if len(mfen) == 8:
                            ret = fen2str(fen)
                            #show_str(ret)
                else:
                    string += ' ' + line.strip()

