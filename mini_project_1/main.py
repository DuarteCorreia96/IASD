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

    # types_new = copy.deepcopy(types)

    print_types(types)


def print_types(types):

    for key in types.values():
        for obj in key["data"].values():
            print(str(obj))
        
        print("\n")


def main():
    load("examples/2.txt")

if __name__ == "__main__":
    main()