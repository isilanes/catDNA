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
for generation in range(2):

    # Run a cycle and save:
    P.run()

    # Produce next generation:
    P.next()

    # Show new generation:
    P.show()
