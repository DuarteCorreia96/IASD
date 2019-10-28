import sys
import copy

from ASARProblem import ASARProblem

def main():
    

    filename = "examples/2.txt"
    problem = ASARProblem()

    with open(filename, "r+") as file:
        problem.load(file)

    trip_id = 0
    airplane = "CS-TUA"

    states = [problem.initial]
    states.append(problem.result(states[-1], (trip_id, airplane)))
    states.append(problem.result(states[-1], (1      , airplane)))
    states.append(problem.result(states[-1], (2      , "CS-TVB")))

    states.append(problem.result(states[-1], (3      , "CS-TVB")))
    states.append(problem.result(states[-1], (4      , "CS-TVB")))
    states.append(problem.result(states[-1], (5      , "CS-TVB")))

    print(states)

    for stat in states:
        print("")
        for key in stat.state:
            if (key == "Problem"):
                continue

            print(key," : ",stat.state[key])

    for action in problem.actions(states[-1]):
        action_cost = problem.path_cost(0, states[-1], action, states[-1])
        print("action:", action, "\t cost:", action_cost)

if __name__ == "__main__":
    main()
