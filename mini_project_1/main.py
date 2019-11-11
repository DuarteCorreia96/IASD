import sys
import copy
import search

from solution import Trip, ASARProblem, State

def main():
    

    filename = "examples/simple5.txt"
    problem = ASARProblem()

    with open(filename, "r+") as file:
        problem.load(file)

    for _ in range(1, 2000):
        best = search.astar_search(problem, problem.heuristic)

        solution_file = "solution.txt"
        with open(solution_file, "w+") as file:
            problem.save(file, best.state)

        if(State.profit != 800):
            print("Deu merda!")

    for key in best.state.counters:
        print(key, ":",best.state.counters[key])

if __name__ == "__main__":
    main()
