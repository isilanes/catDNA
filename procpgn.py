import re
import sys
import numpy as np

fn = 'run.pgn'

#------------------------------------------------------------------------#

class State:
    
    def __init__(self):
        self.place_pieces()

        # Stats arrays:
        self.corr0 = np.zeros((13,), int)
        self.corr1 = np.zeros((8,8,13,), int)

    # --- #

    def show(self):
        for i in range(8):
            string = ''
            for j in range(8):
                id = self.state[7-i][j]
                sy = id2symbol[id]
                string += '{0:3}'.format(sy)
            print(string)

    # --- #

    def mv(self, mov, white=True):
        # mov = movement (e.g. d4)
        # white = True (white, default) or False (black)

        # Take out check indication, if present:
        if mov[-1] == '+':
            mov = mov[:-1]
        
        # Promotion?:
        promotion = False
        if mov[-2] == '=':
            promotion = True
            promote_to = symbol2id[mov[-1]]
            mov = mov[:-2]

        # Castlings:
        if mov == 'O-O': # short castling
            if white:
                self.state[0][7] = 0
                self.state[0][6] = 6
                self.state[0][5] = 4
                self.state[0][4] = 0
            else:
                self.state[7][7] = 0
                self.state[7][6] = -6
                self.state[7][5] = -4
                self.state[7][4] = 0
            return
        elif mov == 'O-O-O': # long castling
            if white:
                self.state[0][0] = 0
                self.state[0][2] = 6
                self.state[0][3] = 4
                self.state[0][4] = 0
            else:
                self.state[7][0] = 0
                self.state[7][2] = -6
                self.state[7][3] = -4
                self.state[7][4] = 0
            return

        # Destination square:
        to_i = int(mov[-1]) - 1
        to_j = letter2j[mov[-2]]

        # Which piece type was moved?:
        piece = 1
        if mov[0] == 'N':
            piece = 2
        elif mov[0] == 'B':
            piece = 3
        elif mov[0] == 'R':
            piece = 4
        elif mov[0] == 'Q':
            piece = 5
        elif mov[0] == 'K':
            piece = 6

        if not white:
            piece = -piece

        # Extra info?:
        if abs(piece) == 1:
            xtra = mov[:-2]
        else:
            xtra = mov[1:-2]

        capture = False
        from_i = 8
        from_j = 8
        if xtra:
            if xtra[-1] == 'x': # capture
                if xtra == 'x': # then piece other than pawn and no file/rank specification needed
                    capture = True
                else: # then pawn, or otherwise file/rank specification needed
                    capture = True
                    if xtra[0] in letter2j:
                        from_j = letter2j[xtra[0]]
                    elif xtra[0] in [ str(x) for x in range(8) ]:
                        from_i = int(xtra[0]) - 1
            else: # then xtra is either col specification, or rank specification
                if xtra[0] in letter2j:
                    from_j = letter2j[xtra[0]]
                elif xtra[0] in [ str(x) for x in range(8)]:
                    from_i = int(xtra[0]) - 1

        # Identify origin square:
        origin = None
        for i in range(8):
            for j in range(8):
                if self.state[i][j] == piece:
                    # White PAWN:
                    if piece == 1:
                        if capture:
                            if j == from_j:
                                if i == to_i - 1:
                                    origin = [i, j]
                                    # en passant?
                                    if self.state[i][to_j] == -1 and not self.state[to_i][to_j]:
                                        self.state[i][to_j] = 0 # capture en passant
                                    break
                        elif j == to_j:
                            if i == to_i - 1:
                                origin = [i, j]
                                break
                            elif i == to_i - 2 and not self.state[i+1][j]:
                                origin = [i, j]
                                break

                    # Black PAWN:
                    elif piece == -1:
                        if capture:
                            if j == from_j:
                                if i == to_i + 1:
                                    # en passant?
                                    if self.state[i][to_j] == 1 and not self.state[to_i][to_j]:
                                        self.state[i][to_j] = 0 # capture en passant
                                    origin = [i, j]
                                    break
                        elif j == to_j:
                            if i == to_i + 1:
                                origin = [i, j]
                                break
                            elif i == to_i + 2 and not self.state[i-1][j]:
                                origin = [i, j]
                                break

                    # KNIGHTs:
                    elif abs(piece) == 2:
                        di = abs(to_i - i)
                        dj = abs(to_j - j)
                        if from_j < 8:
                            if j == from_j:
                                origin = [i, j]
                                break
                        elif from_i < 8:
                            if i == from_i:
                                origin = [i, j]
                                break
                        else:
                            if di == 1 and dj == 2 or di == 2 and dj == 1:
                                origin = [i, j]
                                break

                    # BISHOPs:
                    elif abs(piece) == 3:
                        di = abs(to_i - i)
                        dj = abs(to_j - j)
                        if di == dj:
                            origin = [i, j]
                            break

                    # ROOKs:
                    elif abs(piece) == 4:
                        if from_j < 8:
                            if j == from_j:
                                origin = [i, j]
                                break
                        elif from_i < 8:
                            if i == from_i:
                                origin = [i, j]
                                break
                        else:
                            if j == to_j:
                                # Any intervening piece?:
                                first = min(i,to_i) + 1
                                last  = max(i,to_i)
                                no_piece = True
                                for ii in range(first, last):
                                    if self.state[ii][j]:
                                        no_piece = False
                                        break

                                if no_piece:
                                    origin = [i, j]

                            elif i == to_i:
                                # Any intervening piece?:
                                first = min(j,to_j) + 1
                                last  = max(j,to_j)
                                no_piece = True
                                for jj in range(first, last):
                                    if self.state[i][jj]:
                                        no_piece = False
                                        break

                                if no_piece:
                                    origin = [i, j]
                                    break

                    # QUEENs:
                    elif abs(piece) == 5:
                        origin = [i, j]
                        break

                    # KINGs:
                    elif abs(piece) == 6:
                        origin = [i, j]
                        break

        if not origin:
            print("Error with movement {0}".format(mov))
            sys.exit()

        # Delete from origin:
        self.state[origin[0]][origin[1]] = 0

        # Place into destiny:
        self.state[to_i][to_j] = piece

        # Pawn promotion:
        if promotion:
            if white:
                self.state[to_i][to_j] = promote_to
            else:
                self.state[to_i][to_j] = -promote_to

    # --- #

    def save(self, dta):
        # If won, add, if lost subtract.

        # corr0
        for i in range(8):
            for j in range(8):
                id = self.state[i][j]
                self.corr0[id] += dta

        # corr1
        for i in range(8):
            for j in range(8):
                id = self.state[i][j] + 6 # state in (-6,+6), id in (0,12)
                self.corr1[i,j,id] += dta

    # --- #

    def place_pieces(self):
        # state[i,j] gives us the state of square in i-th row (from
        # bottom to top), and j-th column, left to right.
        #
        # States are:
        # 
        # -6 = black king
        # -5 = black queen
        # -4 = black rook
        # -3 = black knight
        # -2 = black bishop
        # -1 = black pawn
        #  0 = empty
        #  1 = white pawn
        #  2 = white bishop
        #  3 = white knight
        #  4 = white rook
        #  5 = white queen
        #  6 = white king
        self.state = []
        self.state.append([4, 2, 3, 5, 6, 3, 2, 4])
        self.state.append([1, 1, 1, 1, 1, 1, 1, 1])
        for i in range(4):
            self.state.append([0, 0, 0, 0, 0, 0, 0, 0])
        self.state.append([-1, -1, -1, -1, -1, -1, -1, -1])
        self.state.append([-4, -2, -3, -5, -6, -3, -2, -4])

#------------------------------------------------------------------------#

letter2j = {
        'a' : 0,
        'b' : 1,
        'c' : 2,
        'd' : 3,
        'e' : 4,
        'f' : 5,
        'g' : 6,
        'h' : 7,
        }

id2symbol = {
        -6 : 'k',
        -5 : 'q',
        -4 : 'r',
        -3 : 'b',
        -2 : 'n',
        -1 : 'p',
         0 : '.',
         1 : 'P',
         2 : 'N',
         3 : 'B',
         4 : 'R',
         5 : 'Q',
         6 : 'K',
        }

symbol2id = {
        'k' : -6,
        'q' : -5,
        'r' : -4,
        'b' : -3,
        'n' : -2,
        'p' : -1,
        '.' :  0,
        'P' :  1,
        'N' :  2,
        'B' :  3,
        'R' :  4,
        'Q' :  5,
        'K' :  6,
        }

#------------------------------------------------------------------------#

# Main object:
pos = State()

# Loop variables:
is_match = False
imatch = 0   # index of match
nstates = 0 # number of total states taken into account
won = False
lost = False
read = False
string = ''
debug = False

# Read line by line, and collect info:
with open(fn, 'r') as f:
    for line in f:
        line = line.strip()
        if '[Event ' in line: # count matches
            imatch += 1

        if 'Result' in line:
            if '1-0' in line:
                won = True
            elif '0-1' in line:
                lost = True

        if (won or lost) and '1.' in line:
            read = True
            pos.place_pieces()

        if read:
            string += line

        if read and ('1-0' in line or '0-1' in line):
            # dta=1 (whites won) or dta=-1 (whites lost):
            dta = -1
            if '1-0' in line:
                dta = 1
            
            imove = 0
            string = re.sub('{[^}]*}','',string)
            string = re.sub('[^ ]*\.','|',string)
            moves = string.split('|')
            for move in moves:
                mab = move.split()
                ma, mb = False, False
                if mab:
                    if mab[-1] == '1-0' or mab[-1] == '0-1':
                        mab = mab[:-1]
                    if len(mab) == 2:
                        ma, mb = mab[:2]
                    else:
                        ma = mab[0]
                        mb = False

                    imove += 1 # count moves
                    if not mb: # white checkmate (no black movement)
                        if ma[-1] == '#':
                            ma = ma[:-1]
                        if debug:
                            print(ma)
                        pos.mv(ma)
                    else:
                        if mb[-1] == '#': # black checkmate
                            mb = mb[:-1]
                        if debug:
                            print('---- {0}/{1} --'.format(imatch, imove))
                            print(ma, mb)
                        pos.mv(ma)
                        pos.mv(mb, False)

                    if debug:
                        pos.show()
                    pos.save(dta)
                    nstates += 1

            # Clear some variables for next loop cycle:
            string = ''
            read = False
            won = False
            lost = False

if debug:
    print("done {0} states".format(nstates))
    sys.exit()

# Digest some statistics:
totals = {}
for p in range(13):
    totals[p] = 0
    for i in range(8):
        for j in range(8):
            totals[p] += pos.corr1[i,j,p]

# Show statistics:
if False:
    for p in range(13):
        string = '{0:2s} ({1}):\n'.format(id2symbol[p], totals[p])
        for i in range(8):
            for j in range(8):
                v = pos.corr1[7-i,j,p]
                string += '{0:3d} '.format(v)
            string += '\n'

        print(string)

# --- corr0 --- #
max = 0
ave = 0
string = 'int corr0[6][2] = {\n'
for piece in range(1,7):
    pass
string += '};\n'

string += '\n// n = {2}; max = {0:.2f}; ave = {1:.3f}'.format(max, ave/(64*6*2), nstates)
print(string)

# --- corr1 --- #
max = 0
ave = 0
string = 'int corr1[64][6][2] = {\n'
for i in range(8):
    for j in range(8):
        string += '    {\n'
        for piece in range(1,7):
            string += '        {'
            vwhite = 1000.0*pos.corr1[i,j,piece]/nstates
            vblack = 1000.0*pos.corr1[i,j,-piece]/nstates

            if abs(vwhite) > max:
                max = abs(vwhite)
            if abs(vblack) > max:
                max = abs(vblack)

            ave += abs(vwhite) + abs(vblack)

            vwhite = '{0:.0f}'.format(vwhite)
            vblack = '{0:.0f}'.format(vblack)
            string += vwhite + ',' + vblack
            if piece == 6:
                string += '}\n'
            else:
                string += '},\n'
        if i == 7 and j == 7:
            string += '    }\n'
        else:
            string += '    },\n'
string += '};'

string += '\n// n = {2}; max = {0:.2f}; ave = {1:.3f}'.format(max, ave/(64*6*2), nstates)
print(string)
