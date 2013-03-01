from libdna import GA

#----------------------------------------------------------------------#

# Initialize stuff:
P = GA.Population(4)

# Initialize population by mutating a default population:
for i in range(10):
    for m in P.genomes:
        m.mutate()

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
