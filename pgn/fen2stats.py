import re
import numpy as np
import System as S

#----------------------------------------------------------------------#


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

    def __init__(self):
        self.nstates = 0
        self.symbol2pc = {
                'P' : [ 0, 0 ], # 0 = pawn,   0 = white
                'N' : [ 1, 0 ], # 1 = knight, 0 = white
                'B' : [ 2, 0 ], # 2 = bishop, 0 = white
                'R' : [ 3, 0 ], # 3 = rook,   0 = white
                'Q' : [ 4, 0 ], # 4 = queen,  0 = white
                'K' : [ 5, 0 ], # 5 = king,   0 = white
                'p' : [ 0, 1 ], # 0 = pawn,   1 = black
                'n' : [ 1, 1 ], # 1 = knight, 1 = black
                'b' : [ 2, 1 ], # 2 = bishop, 1 = black
                'r' : [ 3, 1 ], # 3 = rook,   1 = black
                'q' : [ 4, 1 ], # 4 = queen,  1 = black
                'k' : [ 5, 1 ], # 5 = king,   1 = black
                }
        self.abundance = [8, 2, 2, 2, 1, 1]
        self.corr0   = np.zeros((6,2,))

    # --- #

    def save(self, fen, won):
        '''Read a FEN, and extract info from it.'''

        self.nstates += 1

        strfen = self.fen2str(fen)
        for i in range(64): # FEN must have 64 values
            v = strfen[i]
            if v != '.':
                piece, color = self.symbol2pc[v]
                if won == 1:
                    self.corr0[piece, color] += 1
                else:
                    self.corr0[piece, color] -= 1

    # --- #

    def fen2str(self, fen):
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

# Use pgn-extract to obtain fen.out:
cmnd = '$HOME/soft/pgn-extract/pgn-extract --fencomments run.pgn > fen.out'
#S.cli(cmnd)

# Variables:
fn   = 'fen.out'
won  = 0 # who won: 0 = no one, 1 = white, 2 = black
read = False
C = Correlation()

# Read file:
with open(fn, 'r') as f:
    for line in f:
        if 'Result' in line:
            string = ''
            if '1-0' in line:
                won = 1
            elif '0-1' in line:
                won = 0
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
                            C.save(fen, won)
                else:
                    string += ' ' + line.strip()

defa = [ 100, 310, 320, 500, 900, 10000 ]
print(C.nstates)
scale = 800.0/C.corr0[0,0]
# Show info:
for piece in range(6):
    b, n = C.corr0[piece]
    rel = C.nstates * C.abundance[piece]
    #val = (b - n)/rel # count
    #val = int(6000*val)                          # scale
    val = C.corr0[piece,0] * scale / C.abundance[piece]
    print(defa[piece], val, b/rel - n/rel)

