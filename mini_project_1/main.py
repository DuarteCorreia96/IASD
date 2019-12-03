import sys
import copy
import search

from solution import Trip, ASARProblem, State
from timeit import default_timer as timer
import numpy as np

def main():   
    
    filename = "examples/private{}.txt"
    solution_file = "solutions/solution{}.txt"

    tests = {1, 2, 3, 4, 5, 6, 7, 8}
    remove = {9}

    for k in tests - remove:

        # print("Solving Problem:", k)

        problem        = ASARProblem()
        State.nodes    = 1
        Trip.counter   = 0
        Trip.min_cost  = sys.maxsize
        start = timer()

        with open(filename.format(k), "r+") as file:
            problem.load(file)

        for _ in range(0, 1):

            best = search.astar_search(problem, problem.heuristic)
            end = timer()
            
            if (best != None): 
                with open(solution_file.format(k), "w+") as file:
                    problem.save(file, best.state)

                b_star = State.nodes ** ( 1 / best.depth)
                branching_str = "Problem: {}\tTime taken: {}\t Number of nodes: {}\t Depth: {} \tB*: {}"

                print(branching_str.format(k, np.round(end - start, 5),State.nodes, best.depth,  round(b_star, 3)))

            else:
                with open(solution_file.format(k), "w+") as file:
                    problem.save(file, best)
                
                print("Problem:", k, "\tTime taken:", np.round(end - start, 5), "\t Infeasible")
            


if __name__ == "__main__":
    main()
