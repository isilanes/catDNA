import re
import sys

fn = 'run.pgn'

#------------------------------------------------------------------------#

class State:

    def __init__(self):
        # state[i,j] gives us the state of cell in i-th row (from
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

    # --- #

    def show(self):
        for i in range(8):
            string = ''
            for j in range(8):
                string += '{0:3d}'.format(self.state[7-i][j])
            print(string)

    # --- #

    def mv(self, mov, white=True):
        # mov = movement (e.g. d4)
        # white = True (white, default) or False (black)

        # Make sense of movement mov:
        to_i = int(mov[-1]) - 1
        to_j = letter2j[mov[-2]]

        moved = 1 # which piece type was moved
        if mov[0] == 'N':
            moved = 3

        if not white:
            moved = -moved

        # Identify origin cell:
        origin = None
        for i in range(8):
            for j in range(8):
                if self.state[i][j] == moved:
                    # White PAWN:
                    if moved == 1:
                        if j == to_j:
                            if i == to_i - 1 or i == to_i - 2:
                                origin = [i, j]
                    # Black PAWN:
                    elif moved == -1:
                        if j == to_j:
                            if i == to_i + 1 or i == to_i + 2:
                                origin = [i, j]
                    # KNIGHTs:
                    if moved == 3:
                        pass

        if not origin:
            print("error")
            sys.exit()

        # Delete from origin:
        self.state[origin[0]][origin[1]] = 0

        # Place into destiny:
        self.state[to_i][to_j] = moved

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

#------------------------------------------------------------------------#

won = False
read = False
string = ''
# Read line by line:
with open(fn, 'r') as f:
    for line in f:
        line = line.strip()
        if 'Result' in line and '1-0' in line:
            won = True

        if won and '1.' in line:
            read = True
            pos = State()

        if read:
            string += line

        if read and '1-0' in line:
            string = re.sub('{[^}]*}','',string)
            string = re.sub('[^ ]*\.','|',string)
            print(string)
            moves = string.split('|')
            for move in moves:
                mab = move.split()
                if mab:
                    pos.show()
                    ma, mb = mab

                    print('----')
                    print(ma, mb)
                    pos.mv(ma)
                    pos.mv(mb, False)
                    pos.show()

            string = ''
            read = False
            won = False
