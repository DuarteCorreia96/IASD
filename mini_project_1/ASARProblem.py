from aero_company import *
from search import Problem
import copy

class ASARProblem(Problem):

    def __init__(self, filename):
        """ The constructor receives a filename to read 
        and create the problem. It calls the function load
        that receives an already opened file. Notice that this 
        function creates a initial state from the variables 
        present on the file."""

        with open(filename, "r") as f:
            self.load(f)

        self.goal = None # Goal will be defined in the goal_test function

    def load(self, file):
        """ Function used to load a new problem from a file.
        This function also initiates the initial state of the problem."""

        # The dictionary that will save the full problem to be solved
        # This should not be changed outside of this function 
        self.problem = {
            "A": {"class": Airport,     "data": {}},
            "C": {"class": Plane_Class, "data": {}},
            "P": {"class": Plane,       "data": {}},
            "L": {"class": Trip,        "data": {}}
        }

        # Reading of the file and subsquent parsing
        lines = file.readlines()
        for line in lines:

            key = line[0]
            if (key in self.problem):
                aero_object = self.problem[key]["class"](line)
                self.problem[key]["data"][aero_object.id] = aero_object

        # Add planes to their classes
        for c in self.problem["C"]["data"].values():
            for plane in self.problem["P"]["data"].values():
                if (c.id == plane.plane_class):
                    c.add_plane(plane)

        # Add trips to their airports
        for trip in self.problem["L"]["data"].values():
            for airport in self.problem["A"]["data"].values():
                if (trip.departure == airport.id):
                    airport.add_trip(trip)

        # Initializes initial state
        self.initial = {
            "Total Profit": 0, 
            "Trips": set()
        }
        
        for key in self.problem["P"]["data"]:

            self.initial[key] = {}
            self.initial[key]["Profit"] = 0
            self.initial[key]["Airport"] = None
            self.initial[key]["Schedule"] = []

        self.print_problem()


    def print_problem(self):
        """ Function used to print the full problem, 
        should mostly be used to debug problems."""

        for key in self.problem.values():
            for obj in key["data"].values():
                print(str(obj))

            print("\n")


    def result(self, old_state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""

        trip_id  = action[0]
        airplane = action[1]

        plane_class = self.problem["P"]["data"][airplane].plane_class

        # First creates a shallow copy of old state
        new_state = old_state.copy()

        # Then modifies the part that is affected by the new trip
        new_state[airplane] = {}

        profit = self.problem["L"]["data"][trip_id].profit[plane_class]
        new_state[airplane]["Profit"] = old_state[airplane]["Profit"] + profit
        new_state["Total Profit"] += profit

        # Saves the already done trips in a set for easy acess
        new_state["Trips"] = old_state["Trips"].copy()
        new_state["Trips"].add(trip_id)

        new_state[airplane]["Airport"] = self.problem["L"]["data"][trip_id].arrival
        new_state[airplane]["Schedule"] = copy.copy(
            old_state[airplane]["Schedule"])
        new_state[airplane]["Schedule"].append(trip_id)

        return new_state
