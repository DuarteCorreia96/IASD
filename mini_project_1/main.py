import sys
from aero_company import *

def load(filename):
    with open(filename) as fh:
        lines = fh.readlines()

    types = {
        "A" : {
            "class": Airport,
            "data" : {}
        },
        "C" : {
            "class": Plane_Class,
            "data" : {}
        },        
        "C" : {
            "class": Plane,
            "data" : {}
        },        
        "L" : {
            "class": Trip,
            "data" : []
        }
    }

    for line in lines:
        key = line[0]
        if (key in types):

            aero_object = types[key]["class"](line)

            if (not isinstance(aero_object, Trip)):
                types[key]["data"][aero_object.id] = aero_object  
            else: 
                types[key]["data"].append(aero_object)     
                    

    print_types(types)
    

def print_types(types):

    for key in types:

        if (key == "L"):
            continue

        print("\n")
        for obj in types[key]["data"]:
            print(str(types[key]["data"][obj]))
    
    print("\n")
    for trip in types["L"]["data"]:
        print(str(trip))

def main():
    load("examples/1.txt")

if __name__ == "__main__":
    main()