import sys
import copy
from aero_company import *


def load(filename):
    with open(filename) as fh:
        lines = fh.readlines()

    types = {
        "A" : { "class": Airport,     "data" : {} },
        "C" : { "class": Plane_Class, "data" : {} },        
        "P" : { "class": Plane,       "data" : {} },        
        "L" : { "class": Trip,        "data" : {} }
    }

    for line in lines:
        
        key = line[0]
        if (key in types):
            aero_object = types[key]["class"](line)
            types[key]["data"][aero_object.id] = aero_object  


    # Add planes to their classes
    for c in types["C"]["data"].values():
        for plane in types["P"]["data"].values():
            if (c.id == plane.plane_class):
                c.add_plane(plane)

    # Add trips to their airports
    for trip in types["L"]["data"].values():
        for airport in types["A"]["data"].values():
            if (trip.departure == airport.id):
                airport.add_trip(trip)

    print_types(types)

    return types


def print_types(types):

    for key in types.values():
        for obj in key["data"].values():
            print(str(obj))
        
        print("\n")


def get_new_state(old_state, action):

    trip_id  = action[0]
    airplane = action[1]
    
    problem  = old_state["Problem"]
    plane_class = problem["P"]["data"][airplane].plane_class

    # First creates a shallow copy of old state
    new_state = old_state.copy()

    # Then modifies the part that is affected by the new trip
    new_state[airplane] = {}

    profit = problem["L"]["data"][trip_id].profit[plane_class]
    new_state[airplane]["Profit"]  = old_state[airplane]["Profit"] + profit
    new_state["Total Profit"]     += profit

    new_state[airplane]["Airport"] = problem["L"]["data"][trip_id].arrival
    new_state[airplane]["Schedule"] = copy.copy(old_state[airplane]["Schedule"])
    new_state[airplane]["Schedule"].append(problem["L"]["data"][trip_id])

    return new_state

def main():
    
    problem = load("examples/2.txt")
    
    state = {"Problem": problem, "Total Profit" : 0}
    for key in problem["P"]["data"]:

        state[key] = {}
        state[key]["Profit"] = 0
        state[key]["Airport"] = None
        state[key]["Schedule"] = []

    trip_id = 0
    airplane = "CS-TUA"

    states = [state]
    states.append(get_new_state(states[-1], (trip_id, airplane)))
    states.append(get_new_state(states[-1], (1      , airplane)))
    states.append(get_new_state(states[-1], (2      , "CS-TVB")))

    for stat in states:
        print("")
        for key in stat:
            if (key == "Problem"):
                continue

            print(key," : ",stat[key])


if __name__ == "__main__":
    main()
