import re
import sys
import numpy as np

fn = 'run.pgn'

#------------------------------------------------------------------------#

class State:

    def __init__(self):
        self.place_pieces()

        # Stats array:
        self.stats = np.zeros((8,8,13,), int)

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
        if mov[0] == 'B':
            piece = 2
        elif mov[0] == 'N':
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
                                if i == to_i - 1 or i == to_i - 2:
                                    origin = [i, j]
                                    break
                        elif j == to_j:
                            if i == to_i - 1:
                                origin = [i, j]
                                break
                            if i == to_i - 2 and not self.state[i+1][j]:
                                origin = [i, j]
                                break

                    # Black PAWN:
                    elif piece == -1:
                        if capture:
                            if j == from_j:
                                if i == to_i + 1 or i == to_i + 2:
                                    origin = [i, j]
                                    break
                        elif j == to_j:
                            if i == to_i + 1:
                                origin = [i, j]
                                break
                            if i == to_i + 2 and not self.state[i-1][j]:
                                origin = [i, j]
                                break

                    # BISHOPs:
                    elif abs(piece) == 2:
                        di = abs(to_i - i)
                        dj = abs(to_j - j)
                        if di == dj:
                            origin = [i, j]
                            break

                    # KNIGHTs:
                    elif abs(piece) == 3:
                        di = abs(to_i - i)
                        dj = abs(to_j - j)
                        if from_j < 8:
                            if j == from_j:
                                origin = [i, j]
                                break
                        else:
                            if di == 1 and dj == 2 or di == 2 and dj == 1:
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

    def save(self):
        for i in range(8):
            for j in range(8):
                id = self.state[i][j]
                self.stats[i,j,id] += 1

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
        self.state.append([4, 3, 2, 5, 6, 2, 3, 4])
        self.state.append([1, 1, 1, 1, 1, 1, 1, 1])
        for i in range(4):
            self.state.append([0, 0, 0, 0, 0, 0, 0, 0])
        self.state.append([-1, -1, -1, -1, -1, -1, -1, -1])
        self.state.append([-4, -3, -2, -5, -6, -2, -3, -4])

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
        -3 : 'n',
        -2 : 'b',
        -1 : 'p',
         0 : '.',
         1 : 'P',
         2 : 'B',
         3 : 'N',
         4 : 'R',
         5 : 'Q',
         6 : 'K',
        }

symbol2id = {
        'k' : -6,
        'q' : -5,
        'r' : -4,
        'n' : -3,
        'b' : -2,
        'p' : -1,
        '.' :  0,
        'P' :  1,
        'B' :  2,
        'N' :  3,
        'R' :  4,
        'Q' :  5,
        'K' :  6,
        }

#------------------------------------------------------------------------#

# Main object:
pos = State()

# Loop variables:
imatch = 0 # index of match
won = False
read = False
string = ''

# Read line by line, and collect info:
with open(fn, 'r') as f:
    for line in f:
        line = line.strip()
        if '[Event ' in line: # count matches
            imatch += 1

        if 'Result' in line and '1-0' in line:
            won = True

        if won and '1.' in line:
            read = True
            pos.place_pieces()

        if read:
            string += line

        if read and '1-0' in line:
            imove = 0
            string = re.sub('{[^}]*}','',string)
            string = re.sub('[^ ]*\.','|',string)
            print(string)
            moves = string.split('|')
            for move in moves:
                mab = move.split()
                if mab:
                    imove += 1 # count moves
                    ma, mb = mab
                    if mb == '1-0': # checkmate
                        print(ma)
                        if ma[-1] == '#':
                            ma = ma[:-1]
                        pos.mv(ma)
                    else:
                        print('---- {0}/{1} --'.format(imatch, imove))
                        print(ma, mb)
                        pos.mv(ma)
                        pos.mv(mb, False)

                    pos.show()
                    pos.save()

            string = ''
            read = False
            won = False

# Digest some statistics:
totals = {}
for p in range(-6,7):
    totals[p] = 0
    for i in range(8):
        for j in range(8):
            totals[p] += pos.stats[i,j,p]

# Show statistics:
for p in range(-6,7):
    string = '{0:2s} ({1}):\n'.format(id2symbol[p], totals[p])
    for i in range(8):
        for j in range(8):
            v = pos.stats[7-i,j,p]
            string += '{0:3d} '.format(v)
        string += '\n'

    print(string)
