def convert_time_to_min(str_time):

    minutes =  int(str_time) % 100
    hours   =  (int(str_time) - minutes) // 100

    return hours * 60 + minutes

class Plane:

    location = None
    path = [[]]

    def __init__(self, line):

        words = line.split()

        self.id = words[1]
        self.plane_class = words[2]
        self.path_profit = 0

    def __str__(self):

        to_print  = "  Name: " + str(self.id)
        to_print += "  Class: " + str(self.plane_class)
        to_print += "  Location: " + str(self.location)

        return to_print


class Airport:

    def __init__(self, line):

        words = line.split()

        self.id  = words[1]
        self.open  = convert_time_to_min(words[2])  
        self.close = convert_time_to_min(words[3]) 

        self.departure_trips = set()
        self.arrival_trips = set()

    def __str__(self):

        to_print  = "  Code: " + str(self.id)
        to_print += "  Open: " + str(self.open)
        to_print += "  Close: " + str(self.close)

        to_print += "  Arrival Trips: "
        for trip in self.arrival_trips:
            to_print += str(trip) + " | "

        to_print += "  Departure Trips: "
        for trip in self.departure_trips:
            to_print += str(trip) + " | "

        return to_print

    def add_arrival_trip(self, trip):
        self.arrival_trips.add(trip.id)

    def add_departure_trip(self, trip):
        self.departure_trips.add(trip.id)


class Plane_Class:

    def __init__(self, line):

        words = line.split()

        self.id        = words[1]
        self.duration  = convert_time_to_min(words[2]) 
        self.planes    = []

    def __str__(self):

        to_print  = "  Class: " + str(self.id)
        to_print += "  Duration: " + str(self.duration)

        to_print += "  Planes of the class: "
        for plane in self.planes:
            to_print += plane.id + " | "

        return to_print

    def add_plane(self, plane):

        self.planes.append(plane)


class Trip:

    counter = 0

    def __init__(self, line):

        words = line.split()

        self.departure = words[1]
        self.arrival   = words[2]
        self.duration  = convert_time_to_min(words[3]) 

        self.profit = {}
        self.id = Trip.counter

        Trip.counter += 1

        w = 4
        while (w + 1 < len(words)):

            self.profit[words[w]] = int( words[w + 1] )
            w += 2

    def __str__(self):

        to_print  = "  Id: " + str(self.id)
        to_print += "  From: " + str(self.departure)
        to_print += "  To: " + str(self.arrival)
        to_print += "  Duration: " + str(self.duration)

        template = "  | Class : {:4}   Profit : {:5}"
        for class_key in self.profit:
            to_print += template.format(class_key, self.profit[class_key])

        return to_print

    def __hash__(self):
        return self.id

    def __eq__(self, value):

        if (not isinstance(value, Trip)):
            return False

        if (self.id == value.id):
            return True

        return False

import search
import copy

class Save_State():

    def __init__(self, state):
        self.state = state

    def __lt__(self, save_state):
        return self.state["Cost"] < save_state.state["Cost"]


class ASARProblem(search.Problem):

    def __init__(self):
        """ The constructor receives a filename to read 
        and create the problem. It calls the function load
        that receives an already opened file. Notice that this 
        function creates a initial state from the variables 
        present on the file."""

        self.initial = None
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
            "Cost": 0,
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

        self.initial = Save_State(self.initial)
        #self.print_problem()


    def print_problem(self):
        """ Function used to print the full problem, 
        should mostly be used to debug problems."""

        for key in self.problem.values():
            for obj in key["data"].values():
                print(str(obj))

            print("\n")


    def result(self, old_state_save, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state). All variables that do not change 
        from previous state maintain their references"""

        old_state = old_state_save.state
        trip = self.problem["L"]["data"][action[0]]

        airplane = action[1]
        plane_class = self.problem["P"]["data"][airplane].plane_class

        # Initializes new state
        new_state = {}
        
        # Update Profit
        new_state["Profit"]  = old_state["Profit"]
        new_state["Profit"] += trip.profit[plane_class]

        # Update Cost
        max_profit  = max(trip.profit.values())
        trip_profit = trip.profit[plane_class]

        new_state["Cost"]  = old_state["Cost"]
        new_state["Cost"] += max_profit - trip_profit

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

        # Update current time of airplanes
        new_state["Current Time"] = old_state["Current Time"].copy()

        if (airplane not in new_state["Current Time"]):
            new_state["Current Time"][airplane] = self.problem["A"]["data"][trip.departure].open 

        new_state["Current Time"][airplane] += trip.duration + self.problem["C"]["data"][plane_class].duration

        return Save_State(new_state)

    def actions(self, save_state):
        """ Yields the actions that can be executed in the given
        state as tuples of (trip_id, airplane_id).
        """

        state  = save_state.state
        trips   = self.problem["L"]["data"]
        ports   = self.problem["A"]["data"]
        planes  = self.problem["P"]["data"]
        p_class = self.problem["C"]["data"]

        # Trips that still need to be made
        trips_todo = trips.keys() - state["Trips"]
        if (trips_todo == set()):
            return list()

        # checks every plane possibilit for the remaining trips
        planes_unused = planes.keys() - state["Current Time"].keys()
        planes_time   = state["Current Time"]

        for trip_id in trips_todo:

            trip         = trips[trip_id]
            depart_port  = ports[trip.departure]
            arrival_port = ports[trip.arrival]

            for plane in planes_unused:

                if (planes[plane].plane_class in trip.profit and \
                    depart_port.open + trip.duration > arrival_port.open):

                    yield (trip_id, plane)

            for plane in state["Airport"][depart_port.id]:

                rotation = p_class[planes[plane].plane_class].duration
                if (planes_time[plane] + trip.duration + rotation < arrival_port.close and \
                    planes_time[plane] + trip.duration > arrival_port.open  and \
                    planes[plane].plane_class in trip.profit):
                    
                    yield (trip_id, plane)

        return list()

    def path_cost(self, current_cost, old_state, action, new_state):
        """ Returns the path cost of the new state, reached from the
        old state by applying action, knowing that the path cost of 
        old state is the current cost.

        This is simply the profit loss of using the class of the airplane
        on the trip when compared to the max profit
        """

        trip = self.problem["L"]["data"][action[0]]
        plane_class = self.problem["P"]["data"][ action[1]].plane_class

        max_profit  = max(trip.profit.values())
        trip_profit = trip.profit[plane_class]

        return max_profit - trip_profit

    def goal_test(self, save_state):
        """ Returns True if state s is a goal state, 
        and False otherwise
        """

        state = save_state.state
        trips = self.problem["L"]["data"]

        trips_todo = trips.keys() - state["Trips"]
        if (trips_todo != set()):
            return False

        for plane_trip in state["Schedule"].values():

            if (plane_trip != []):

                start = trips[plane_trip[0]].departure
                end   = trips[plane_trip[-1]].arrival
                if (start != end):
                    return False

        return True

    def heuristic(self, node):

        return 0

    def save(self, file, save_state):

        state = save_state.state
        if(not self.goal_test(save_state)):
            file.write("Infeasible")
            return

        trips   = self.problem["L"]["data"]
        ports   = self.problem["A"]["data"]
        planes  = self.problem["P"]["data"]
        p_class = self.problem["C"]["data"]

        for plane in state["Schedule"]:

            if (state["Schedule"][plane] == []):
                continue

            file.write("S " + plane)
            currTime = ports[trips[state["Schedule"][plane][0]].departure].open

            for trip_id in state["Schedule"][plane]:

                hour    = str(currTime // 60) if (currTime // 60) > 9 else str(0) + str(currTime // 60)
                minutes = str(currTime %  60) if (currTime %  60) > 9 else str(0) + str(currTime %  60) 

                str_trip = " " + hour + minutes + " " + trips[trip_id].departure + " " + trips[trip_id].arrival
                file.write(str_trip)

                currTime += trips[trip_id].duration + p_class[planes[plane].plane_class].duration
                
            file.write("\n")

        file.write("P " + str(state["Profit"]) + "\n") 