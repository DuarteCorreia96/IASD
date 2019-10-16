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
            "Profit": 0, 
            "Trips": set(),
            "Airport": {},
            "Schedule": {},
            "Unused": set()
        }
        
        # Initialize airplanes schedule
        for key in self.problem["P"]["data"]:
            self.initial["Schedule"][key] = []
            self.initial["Unused"].add(key)

        # Initialize airports sets
        for key in self.problem["A"]["data"]:
            self.initial["Airport"][key] = set()

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
        self.actions(state). All variables that do not change 
        from previous state maintain their references"""

        trip = self.problem["L"]["data"][action[0]]

        airplane = action[1]
        plane_class = self.problem["P"]["data"][airplane].plane_class

        # Initializes new state
        new_state = {}
        
        # Update Profit
        new_state["Profit"]  = old_state["Profit"]
        new_state["Profit"] += trip.profit[plane_class]

        # Update Trips done
        new_state["Trips"] = old_state["Trips"].copy()
        new_state["Trips"].add(trip.id)

        # Updates Airpot List
        new_state["Airport"] = {}
        for port in old_state["Airport"]:
            if (port == trip.arrival or port == trip.departure):
                new_state["Airport"][port] = old_state["Airport"][port].copy()
            else:
                new_state["Airport"][port] = old_state["Airport"][port]

        new_state["Airport"][trip.departure].discard(airplane)
        new_state["Airport"][trip.arrival].add(airplane)

        # Update airplane schedules
        new_state["Schedule"] = {}
        for plane in old_state["Schedule"]:
            if (plane == airplane):
                new_state["Schedule"][plane] = old_state["Schedule"][plane].copy()
            else:
                new_state["Schedule"][plane] = old_state["Schedule"][plane]

        new_state["Schedule"][airplane].append(trip.id)

        # Update unused airplanes if needed
        if (airplane in old_state["Unused"]):
            new_state["Unused"] = old_state["Unused"].copy()
            new_state["Unused"].remove(airplane)
        else:
            new_state["Unused"] = old_state["Unused"]

        return new_state

    def actions(self, state):
        """ Yields the actions that can be executed in the given
        state as tuples of (trip_id, airplane_id).

        TO DO! check if the trip is possible because schedule of airport
        """

        trips = self.problem["L"]["data"]
        ports = self.problem["A"]["data"]
        
        # At the start where the airplanes are still unused
        for plane in state["Unused"]:
            for trip in trips:
                if (trip not in state["Trips"]):
                    yield (trip, plane)

        # Searches trips per airport
        for port in ports.values():
            for trip in port.trips:
                if (trip not in state["Trips"]):
                    for plane in state["Airport"][port.id]:
                        yield (trip, plane)
