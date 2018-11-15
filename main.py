from simulator import *
import time, sys

f = open(sys.argv[1]).read()
p = Problem(f)
p.parse()
sim = Simulator(p, sys.argv[2])
print("Starting simulation...")
print("Solving problems for each step...")
start = time.time()
sim.solve()
print("Problem solved.")
end = time.time()
elapsed = end - start
print("Total time for solving the problem:", elapsed, "s")
sim.simulate()
