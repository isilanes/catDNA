from libdna import GA

#----------------------------------------------------------------------#

# Initialize stuff:
P = GA.Population(4)

# Initialize population:
P.genomes[0].sequence[0] = 200
P.genomes[1].sequence[1] = 200
P.genomes[2].sequence[2] = 200
P.genomes[3].sequence[3] = 200

# Optimization loop:
ngen = 10
for generation in range(ngen):
    print("\n----- Generation {0}/{1} -----\n".format(generation+1, ngen))
    
    # Run a cycle and save:
    P.run()

    # Show current results:
    P.show()

    # Produce next generation:
    P.next()
