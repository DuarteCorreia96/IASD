from aero_company import *
import search
import copy

class ASARProblem(search.Problem):

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
        for plane in self.problem["P"]["data"].values():
            self.problem["C"]["data"][plane.plane_class].add_plane(plane)

        # Add trips to their airports
        for trip in self.problem["L"]["data"].values():
            self.problem["A"]["data"][trip.departure].add_departure_trip(trip)
            self.problem["A"]["data"][trip.arrival].add_arrival_trip(trip)

        # Initializes initial state
        self.initial = {
            "Profit": 0, 
            "Trips": set(),
            "Airport": {},
            "Schedule": {},
            "Current Time": {},
        }
        
        # Initialize airplanes schedule
        for key in self.problem["P"]["data"]:
            self.initial["Schedule"][key] = []

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
                new_state["Schedule"][plane]     = old_state["Schedule"][plane].copy()
            else:
                new_state["Schedule"][plane] = old_state["Schedule"][plane]

        new_state["Schedule"][airplane].append(trip.id)

        # Update current time of airplanes
        new_state["Current Time"] = old_state["Current Time"].copy()

        if (airplane not in new_state["Current Time"]):
            new_state["Current Time"][airplane] = self.problem["A"]["data"][trip.departure].open 

        new_state["Current Time"][airplane] += trip.duration + self.problem["C"]["data"][plane_class].duration

        return new_state

    def actions(self, state):
        """ Yields the actions that can be executed in the given
        state as tuples of (trip_id, airplane_id).
        """

        trips  = self.problem["L"]["data"]
        ports  = self.problem["A"]["data"]
        planes = self.problem["P"]["data"]

        
        # Trips that still need to be made
        trips_todo = trips.keys() - state["Trips"]
        if (trips_todo == set()):
            return list()

        # At the start where the airplanes are still unused
        planes_unused = planes.keys() - state["Current Time"].keys()

        for plane in planes_unused:
            for trip_id in trips_todo:
                if (planes[plane].plane_class in trips[trip_id].profit):
                    yield (trip_id, plane)

        # checks every plane possibilit for the remaining trips
        planes_time = state["Current Time"]

        for trip_id in trips_todo:

            trip         = trips[trip_id]
            depart_port  = ports[trip.departure]
            arrival_port = ports[trip.arrival]

            for plane in state["Airport"][depart_port.id]:

                if (planes_time[plane] + trip.duration < arrival_port.close and \
                    planes[plane].plane_class in trip.profit):
                    
                    yield (trip_id, plane)

        return list()