import re
import sys
import numpy as np

fn = 'run.pgn'

#------------------------------------------------------------------------#

# Global vars:
EMPTY       = 0
blackKing   = 1
blackQueen  = 2
blackRook   = 3
blackBishop = 4
blackKnight = 5
blackPawn   = 6
whitePawn   = 7
whiteKnight = 8
whiteBishop = 9
whiteRook   = 10
whiteQueen  = 11
whiteKing   = 12

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
        if mov[-1] == '#':
            mov = mov[:-1]
        
        # Promotion?:
        promotion = False
        if mov[-2] == '=':
            promotion = True
            if white:
                promote_to = symbol2id[mov[-1]]
            else:
                promote_to = symbol2id[mov[-1].lower()] # lowercase white piece is equivalent black piece
            mov = mov[:-2]

        # Castlings:
        if mov == 'O-O': # short castling
            if white:
                self.state[0][7] = EMPTY
                self.state[0][6] = whiteKing
                self.state[0][5] = whiteRook
                self.state[0][4] = EMPTY
            else:
                self.state[7][7] = EMPTY
                self.state[7][6] = blackKing
                self.state[7][5] = blackRook
                self.state[7][4] = EMPTY
            return
        elif mov == 'O-O-O': # long castling
            if white:
                self.state[0][0] = EMPTY
                self.state[0][2] = whiteKing
                self.state[0][3] = whiteRook
                self.state[0][4] = EMPTY
            else:
                self.state[7][0] = EMPTY
                self.state[7][2] = blackKing
                self.state[7][3] = blackRook
                self.state[7][4] = EMPTY
            return

        # Destination square:
        to_i = int(mov[-1]) - 1
        to_j = letter2j[mov[-2]]

        # Which piece type was moved?:
        if white:
            piece = whitePawn
            if mov[0] == 'N':
                piece = whiteKnight
            elif mov[0] == 'B':
                piece = whiteBishop
            elif mov[0] == 'R':
                piece = whiteRook
            elif mov[0] == 'Q':
                piece = whiteQueen
            elif mov[0] == 'K':
                piece = whiteKing
        else:
            piece = blackPawn
            if mov[0] == 'N':
                piece = blackKnight
            elif mov[0] == 'B':
                piece = blackBishop
            elif mov[0] == 'R':
                piece = blackRook
            elif mov[0] == 'Q':
                piece =blackQueen
            elif mov[0] == 'K':
                piece = blackKing

        # Extra info?:
        if piece == whitePawn or piece == blackPawn:
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
                    if piece == whitePawn:
                        if capture:
                            if j == from_j:
                                if i == to_i - 1:
                                    origin = [i, j]
                                    # en passant?
                                    if self.state[i][to_j] == blackPawn and self.state[to_i][to_j] == EMPTY:
                                        self.state[i][to_j] = EMPTY # capture en passant
                                    break
                        elif j == to_j:
                            if i == to_i - 1:
                                origin = [i, j]
                                break
                            elif i == to_i - 2 and self.state[i+1][j] == EMPTY:
                                origin = [i, j]
                                break

                    # Black PAWN:
                    elif piece == blackPawn:
                        if capture:
                            if j == from_j:
                                if i == to_i + 1:
                                    # en passant?
                                    if self.state[i][to_j] == whitePawn and self.state[to_i][to_j] == EMPTY:
                                        self.state[i][to_j] = EMPTY # capture en passant
                                    origin = [i, j]
                                    break
                        elif j == to_j:
                            if i == to_i + 1:
                                origin = [i, j]
                                break
                            elif i == to_i + 2 and self.state[i-1][j] == EMPTY:
                                origin = [i, j]
                                break

                    # KNIGHTs:
                    elif piece == whiteKnight or piece == blackKnight:
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
                    elif piece == whiteBishop or piece == blackBishop:
                        di = abs(to_i - i)
                        dj = abs(to_j - j)
                        if di == dj:
                            origin = [i, j]
                            break

                    # ROOKs:
                    elif piece == whiteRook or piece == blackRook:
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
                                    if self.state[ii][j] != EMPTY:
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
                                    if self.state[i][jj] != EMPTY:
                                        no_piece = False
                                        break

                                if no_piece:
                                    origin = [i, j]
                                    break

                    # QUEENs:
                    elif piece == whiteQueen or piece == blackQueen:
                        origin = [i, j]
                        break

                    # KINGs:
                    elif piece == whiteKing or piece == blackKing:
                        origin = [i, j]
                        break

        if not origin:
            print("Error with movement {0}".format(mov))
            sys.exit()

        # Delete from origin:
        self.state[origin[0]][origin[1]] = EMPTY

        # Place into destiny:
        self.state[to_i][to_j] = piece

        # Pawn promotion:
        if promotion:
            self.state[to_i][to_j] = promote_to

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
                id = self.state[i][j]
                self.corr1[i,j,id] += dta

    # --- #

    def place_pieces(self):
        # state[i,j] gives us the state of square in i-th row (from
        # bottom to top), and j-th column, left to right.
        #
        # States are:
        # 
        #  0 = empty
        #  1 = black king
        #  2 = black queen
        #  3 = black rook
        #  4 = black bishop
        #  5 = black knight
        #  6 = black pawn
        #  7 = white pawn
        #  8 = white bishop
        #  9 = white knight
        # 10 = white rook
        # 11 = white queen
        # 12 = white king
        self.state = []

        # White pieces:
        self.state.append([whiteRook, whiteKnight, whiteBishop, whiteQueen, \
                whiteKing, whiteBishop, whiteKnight, whiteRook])
        self.state.append([whitePawn, whitePawn, whitePawn, whitePawn, \
                whitePawn, whitePawn, whitePawn, whitePawn])

        # Empty squares:
        for i in range(4):
            self.state.append([EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY])

        # Black pieces:
        self.state.append([blackPawn, blackPawn, blackPawn, blackPawn, \
                blackPawn, blackPawn, blackPawn, blackPawn])
        self.state.append([blackRook, blackKnight, blackBishop, blackQueen, \
                blackKing, blackBishop, blackKnight, blackRook])

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
    blackKing   : 'k',
    blackQueen  : 'q',
    blackRook   : 'r',
    blackBishop : 'b',
    blackKnight : 'n',
    blackPawn   : 'p',
    EMPTY       : '.',
    whitePawn   : 'P',
    whiteKnight : 'N',
    whiteBishop : 'B',
    whiteRook   : 'R',
    whiteQueen  : 'Q',
    whiteKing   : 'K',
    }

symbol2id = {
        'k' : blackKing,
        'q' : blackQueen,
        'r' : blackRook,
        'b' : blackBishop,
        'n' : blackKnight,
        'p' : blackPawn,
        '.' : EMPTY,
        'P' : whitePawn,
        'N' : whiteKnight,
        'B' : whiteBishop,
        'R' : whiteRook,
        'Q' : whiteQueen,
        'K' : whiteKing,
        }

#------------------------------------------------------------------------#

# Main object:
S = State()

# Loop variables:
is_match = False
imatch = 0  # index of match
nstates = 0 # number of total states taken into account
won = False
lost = False
read = False
string = ''
debug = True

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
            S.place_pieces()

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
                        if debug:
                            print(ma)
                        S.mv(ma)
                    else:
                        if debug:
                            print('---- {0}/{1} --'.format(imatch, imove))
                            print(ma, mb)
                        S.mv(ma)
                        S.mv(mb, False)

                    if debug:
                        S.show()
                    S.save(dta)
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
