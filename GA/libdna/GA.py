import random
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
        self.score = 0

    # --- #

    def seq2str(self):
        '''Given a genome sequence, convert to unique string,
        to label it.'''

        string = [ '{0:04d}'.format(int(x)) for x in self.sequence ]
        string = '-'.join(string)

        return string

    # --- #

    def run(self):
        # Print:
        print("Running genome {0}".format(self.sequence))

        # Build .c file for compiling:
        string = 'int corr0[6] = { 100, ' + ', '.join([str(int(x)) for x in self.sequence]) + ', 10000 };\n'
        with open('corr.c', 'w') as f:
            f.write(string)

        # Do compile:
        cmnd = './build-ga.sh {0} && mv catDNA-{0} arena/'.format(self.seq2str())
        #print(cmnd)
        S.cli(cmnd)

        # Run matches: 
        cmnd = './run.sh {0} > log'.format(self.seq2str())
        #print(cmnd)
        S.cli(cmnd)

        # Read log:
        with open('log', 'r') as f:
            for line in f:
                if 'Score of catDNA-' in line:
                    aline = line.split()
                    won  = int(aline[-7])
                    lost = int(aline[-5])
                    draw = int(aline[-3])
                    score = (won * 1 + draw * 0.5) / (won + lost + draw)

        # We keep the last result:
        self.score = score

        # We save to file:
        self.save()

    # --- #

    def save(self):
        with open('ga.log', 'a') as f:
            string = '{0} {1:.6f}\n'.format(self.seq2str(), self.score)
            f.write(string)

    # --- #

    def mutate(self):
        '''Produce random mutations to itself.'''

        tmp = []

        for gene in self.sequence:
            gene += random.uniform(-100,100)
            if gene > 9999:
                gene = 9999
            elif gene < 100:
                gene = 100
            gene = int(gene)
            tmp.append(gene)

        self.sequence = tmp[:]

#----------------------------------------------------------------------#

class Population:

    def __init__(self, nmembers=4):
        self.genomes = []
        self.saved = {}
        for m in range(nmembers):
            self.genomes.append(Genome())

    # --- #

    def run(self):
        for m in self.genomes:
            s = m.seq2str()
            if s in self.saved:
                m.score = self.saved[s]
            else:
                m.run()

    # --- #

    def next(self):
        # The specimens are ordered by score.
        # Specimen 1 is kept
        # Specimen 2 and 3 are substituted by their "offspring" with 1
        # Specimen 4 and next ones are kept, randomly mutated

        # Sort (decorate-sort-undecorate):
        dsu = []
        for m in self.genomes:
            dsu.append([m.score, m])
        dsu.sort()
        dsu.reverse()
        sorted = [ e[1] for e in dsu ] # sorted list

        # Save score of best so far (avoid calculating it in the future):
        self.saved[sorted[0].seq2str()] = sorted[0].score

        # New population:
        new = [ sorted[0] ] # keep first

        # Offspring of 1+2 and 1+3:
        for g in sorted[1:3]:
            off = self.offspring(sorted[0], g)
            new.append(off)

        # From 4th on, mutate randomly:
        for g in sorted[3:]:
            g.mutate()
            new.append(g)

        # Make new population current one:
        self.genomes = new

    # --- #

    def offspring(self, A, B):
        '''Generate random offspring of genomes A and B.'''

        C = Genome()
        for i in range(len(A.sequence)):
            Ai = A.sequence[i]
            Bi = B.sequence[i]
            C.sequence[i] = random.choice([Ai, Bi])

        return C
    
    # --- #

    def show(self):
        for g in self.genomes:
            string = ''
            for gene in g.sequence:
                string += '{0:04d} '.format(int(gene))
            string += 'score = {0:.6f}'.format(g.score)
            print(string)

#----------------------------------------------------------------------#
