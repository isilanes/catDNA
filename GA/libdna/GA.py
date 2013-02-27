import numpy as np
import System as S

#----------------------------------------------------------------------#

class Genome:

    def __init__(self):
        # pawn =   100 always (no index)
        # i = 0, knight
        # i = 1, bishop
        # i = 2, rook
        # i = 3, queen
        # king = 10000 always (no index)
        self.sequence = np.ones((4,)) * 100

    # --- #

    def seq2str(self):
        '''Given a genome sequence, convert to unique string,
        to label it.'''

        string = [ '{0:04d}'.format(int(x)) for x in self.sequence ]
        string = '-'.join(string)

        return string

    # --- #

    def run(self):
        # Build .c file for compiling:
        string = 'int corr0[6] = { 100, ' + ', '.join([str(int(x)) for x in self.sequence]) + ', 10000 };\n'
        with open('src/corr.c', 'w') as f:
            f.write(string)

        # Do compile:
        cmnd = './build-ga.sh {0} && mv catDNA-{0} arena/'.format(self.seq2str())
        print(cmnd)
        #S.cli(cmnd)

        # Run matches: 
        cmnd = './run.sh {0}'.format(self.seq2str())
        print(cmnd)
        #S.cli(cmnd)

#----------------------------------------------------------------------#

class Population:

    def __init__(self, nmembers=4):
        self.members = []
        for m in range(nmembers):
            self.members.append(Genome())

    # --- #

    def run(self):
        for m in self.members:
            m.run()

#----------------------------------------------------------------------#
