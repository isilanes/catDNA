import numpy as np

#----------------------------------------------------------------------#

class Genome:

    def __init__(self):
        # pawn =   100 always (no index)
        # i = 0, knight
        # i = 1, bishop
        # i = 2, rook
        # i = 3, queen
        # king = 10000 always (no index)
        self.sequence = np.zeros((4,))

#----------------------------------------------------------------------#

class Population:

    def __init__(self, nmembers=4):
        self.members = []
        for m in range(nmembers):
            self.members.append(Genome())

#----------------------------------------------------------------------#
