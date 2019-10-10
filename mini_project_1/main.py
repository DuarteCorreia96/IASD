import sys
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

    print_types(types)
    

def print_types(types):

    for key in types:
        print("\n")
        for obj in types[key]["data"]:
            print(str(types[key]["data"][obj]))


def main():
    load("examples/2.txt")

if __name__ == "__main__":
    main()