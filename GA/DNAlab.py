#!/usr/bin/python3

import argparse
from libdna import GA

#------------------------------------------------------------------------------#

# Read arguments:
parser = argparse.ArgumentParser()

parser.add_argument("-n", "--generations",
        help="Amount of generations to run. Default: 5.",
        type=int,
        default=5)

o = parser.parse_args()

#--------------------------------------------------------------------------------#

# Initialize stuff:
P = GA.Population(4, log='log/ga.log')

# Read best genomes from file, then create first generation from it:
P.get_best()
P.next()

# Optimization loop:
for generation in range(o.generations):
    print("\n----- Generation {0}/{1} -----\n".format(generation+1, o.generations))
    
    # Run a cycle and save:
    P.run()

    # Show current results:
    P.show()

    # Produce next generation:
    P.next()
