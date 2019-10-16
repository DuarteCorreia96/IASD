import sys
import copy

from ASARProblem import ASARProblem

def main():
    

    filename = "examples/2.txt"
    problem = ASARProblem(filename)

    trip_id = 0
    airplane = "CS-TUA"

    states = [problem.initial]
    states.append(problem.result(states[-1], (trip_id, airplane)))
    states.append(problem.result(states[-1], (1      , airplane)))
    states.append(problem.result(states[-1], (2      , "CS-TVB")))

    for stat in states:
        print("")
        for key in stat:
            if (key == "Problem"):
                continue

            print(key," : ",stat[key])

    for action in problem.actions(states[-2]):
        print(action)

if __name__ == "__main__":
    main()
