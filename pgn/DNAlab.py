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

# Initialize stuff:
P = Population(2)

# Optimization loop:
for i in range(1):
    # Refresh population:
    P.members[0].sequence[0] = 310
    P.members[1].sequence[3] = 900

    # Generate catDNA executable:
    for m in P.members:
        print(m.sequence)
