import os
import sys
import time
import random
import numpy as np
import subprocess as sp

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
        # Print message:
        print("Running genome: {0} - ".format(self.seq2str()), end='')
        print(" "*4, end="")
        sys.stdout.flush()

        # Build .c file for compiling:
        string = 'int corr0[6] = { 100, ' + ', '.join([str(int(x)) for x in self.sequence]) + ', 10000 };\n'
        with open('corr.c', 'w') as f:
            f.write(string)

        # Do compile:
        id = self.seq2str()
        cmnd = './build-ga.sh {0} && mv catDNA-{0} arena/'.format(id)
        build = sp.Popen(cmnd, shell=True)
        build.communicate()

        # Run matches, and print progress:
        cmnd = './run.sh {0} > log'.format(id)
        run = sp.Popen(cmnd, shell=True)
        fn = 'arena/pgn.{0}'.format(id)
        while run.poll() == None:
            if os.path.isfile(fn):
                cmnd = 'grep -c Result {0}'.format(fn)
                grep = sp.Popen(cmnd, stdout=sp.PIPE, shell=True)
                out, err = grep.communicate()
                if out:
                    out = str(out, encoding="utf-8")
                    out = int(out.strip())
                    string = '\b'*4 + '{0:<4d}'.format(out)
                    print(string, end="")
                    sys.stdout.flush()
            time.sleep(10)
        run.communicate()
        
        # Print "completion":
        grep = sp.Popen(cmnd, stdout=sp.PIPE, shell=True)
        out, err = grep.communicate()
        out = str(out, encoding="utf-8")
        out = int(out.strip())
        string = '\b'*4 + '{0:<4d}'.format(out)
        print(string)

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

    def mutate(self, variability=100):
        '''Produce random mutations to itself.'''

        tmp = []

        for gene in self.sequence:
            gene += random.uniform(-variability,variability)
            if gene > 9999:
                gene = 9999
            elif gene < 100:
                gene = 100
            gene = int(gene)
            tmp.append(gene)

        return tmp

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
        # Specimen 2 and 3 are substituted by their "offspring" with 1, slightly mutated
        # Specimen n > 3 are substituted by mutations of specimen n-3

        # Sort (decorate-sort-undecorate):
        dsu = []
        for m in self.genomes:
            dsu.append([m.score, m])
        try:
            dsu.sort()
        except:
            pass
        dsu.reverse()
        sorted = [ e[1] for e in dsu ] # sorted list

        # Save score of best so far (avoid calculating it in the future):
        self.saved[sorted[0].seq2str()] = sorted[0].score

        # New population:
        new = [ sorted[0] ] # keep first

        # Offspring of 1+2 and 1+3:
        for g in sorted[1:3]:
            off = self.offspring(sorted[0], g)
            off.sequence = off.mutate(25)
            new.append(off)

        # From 4th on, mutate N-3rd randomly:
        for g in sorted[:-3]:
            p = Genome()
            p.sequence = g.mutate()
            new.append(p)

        # Make new population current one:
        self.genomes = new[:]

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
        print("")
        for g in self.genomes:
            string = g.seq2str()
            string += ' : {0:.6f}'.format(g.score)
            print(string)

    # --- #

    def get_best(self,fn):
        '''Get best genomes so far from file "fn".'''

        # Read genomes from file, and sort by score:
        dsu = []
        with open(fn, 'r') as f:
            for line in f:
                seq, score = line.split()
                score = float(score)
                dsu.append([score, seq])

        dsu.sort()
        dsu.reverse()

        # Get nmembers distinct genomes with highest score:
        top = {}
        for score, seq in dsu:
            top[seq] = score
            if len(top) >= len(self.genomes):
                break

        # Build population from it:
        self.genomes = [] # blank present population
        for seq, score  in top.items():
            genes = [ int(x) for x in seq.split('-') ]
            g = Genome()
            g.sequence = genes[:]
            g.score = score
            self.genomes.append(g)

#----------------------------------------------------------------------#
