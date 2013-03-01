from libdna import GA

#----------------------------------------------------------------------#

# Initialize stuff:
P = GA.Population(4)

# Initialize population:
P.genomes[0].sequence[0] = 200
P.genomes[1].sequence[1] = 350
P.genomes[2].sequence[3] = 500
P.genomes[3].sequence[3] = 750

# Optimization loop:
for generation in range(2):
    print("\n----- Generation {0} -----\n".format(generation))
    
    # Run a cycle and save:
    P.run()

    # Show current results:
    P.show()

    # Produce next generation:
    P.next()
