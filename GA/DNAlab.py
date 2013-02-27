from libdna import GA

#----------------------------------------------------------------------#

# Initialize stuff:
P = GA.Population(2)

# Optimization loop:
for i in range(1):
    # Refresh population:
    P.members[0].sequence[0] = 310
    P.members[1].sequence[3] = 900

    # Run a cycle:
    P.run()
