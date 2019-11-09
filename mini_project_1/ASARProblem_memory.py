from aero_company import Airport, Plane_Class, Plane, Trip
import search
import copy

class State():

    def __init__(self, old_state):

        self.next = old_state

        self.trip_id    = None
        self.plane      = ""
        self.plane_time = 0
        self.cost       = 0

    def __lt__(self, state):
        
        return self.cost < state.cost


class ASARProblem(search.Problem):

    def __init__(self):
        """ Constructor
        """

        self.initial = State(None)
        self.goal = None # Goal will be defined in the goal_test function

    def load(self, file):
        """ Function used to load a new problem from a file.
        """

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


    def result(self, old_state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state). 
        """

        trip = self.problem["L"]["data"][action[0]]
        
        airplane = action[1]
        plane_class = self.problem["P"]["data"][airplane].plane_class

        new_state = State(old_state)
        new_state.trip_id    = trip.id
        new_state.plane      = action[1]
        new_state.plane_time = action[2]
        new_state.cost       = old_state.cost + (trip.max_profit - trip.profit[plane_class])

        return new_state

    def actions(self, state):
        """ Yields the actions that can be executed in the given
        state as tuples of (trip_id, airplane_id).
        """

        trips   = self.problem["L"]["data"]
        ports   = self.problem["A"]["data"]
        planes  = self.problem["P"]["data"]
        p_class = self.problem["C"]["data"]

        # Get trips done so far
        airports = {}
        for port in ports:
            airports[port] = set()

        trips_done  = set()
        planes_time = {}
        
        aux = copy.deepcopy(state)
        while aux.next != None:

            trip = trips[aux.trip_id]
            if (aux.plane not in planes_time):
                planes_time[aux.plane] = aux.plane_time
                airports[trip.arrival].add(aux.plane)

            trips_done.add(trip.id)

            aux = aux.next

        # Trips that still need to be made
        trips_todo = trips.keys() - trips_done
        if (trips_todo == set()):
            return list()

        # checks every plane possibilit for the remaining trips
        planes_unused = planes.keys() - planes_time.keys()

        for trip_id in trips_todo:

            trip         = trips[trip_id]
            depart_port  = ports[trip.departure]
            arrival_port = ports[trip.arrival]

            for plane in planes_unused:
                
                rotation = p_class[planes[plane].plane_class].duration
                current_time = depart_port.open + trip.duration

                if (current_time > arrival_port.open and \
                    planes[plane].plane_class in trip.profit):

                    yield (trip_id, plane, current_time + rotation)

            for plane in airports[depart_port.id]:

                rotation = p_class[planes[plane].plane_class].duration
                current_time = planes_time[plane] + trip.duration

                if (current_time + rotation < arrival_port.close and \
                    current_time            > arrival_port.open  and \
                    planes[plane].plane_class in trip.profit):
                    
                    yield (trip_id, plane, current_time + rotation)

        return list()

    def path_cost(self, current_cost, old_state, action, new_state):
        """ Returns the path cost of the new state, reached from the
        old state by applying action, knowing that the path cost of 
        old state is the current cost.

        This is simply the profit loss of using the class of the airplane
        on the trip when compared to the max profit
        """

        trip = self.problem["L"]["data"][action[0]]
        plane_class = self.problem["P"]["data"][action[1]].plane_class

        return trip.max_profit - trip.profit[plane_class]

    def goal_test(self, state):
        """ Returns True if state s is a goal state, 
        and False otherwise
        """

        trips = self.problem["L"]["data"]
        trips_done    = set()
        planes_start  = {}
        planes_finish = {}

        aux = copy.deepcopy(state)
        while aux.next != None:

            trip = trips[aux.trip_id]

            if (aux.plane not in planes_finish):
                planes_finish[aux.plane] = trip.arrival

            planes_start[aux.plane] = trip.departure

            trips_done.add(trip.id)
            aux = aux.next

        trips_todo = trips.keys() - trips_done
        if (trips_todo != set()):
            return False

        for plane in planes_finish.keys():
            if (planes_start[plane] != planes_finish[plane]):
                return False

        return True

    def heuristic(self, node):

        trips   = self.problem["L"]["data"]
        ports   = self.problem["A"]["data"]
        planes  = self.problem["P"]["data"]

        planes_start = {}
        trips_done   = set()

        aux = copy.deepcopy(node.state)
        while aux.next != None:

            trip = trips[aux.trip_id]

            planes_start[aux.plane] = trip.departure
            trips_done.add(trip.id)

            aux = aux.next

        heuristic  = 0
        trips_todo = trips.keys() - trips_done
        for plane in planes_start:

            start = planes_start[plane]
            trips_stop  = trips_todo.intersection(ports[start].arrival_trips)
            plane_class = planes[plane].plane_class

            min_cost = 0
            for trip_id in trips_stop:

                trip = trips[trip_id]
                cost = trip.max_profit - trip.profit[plane_class]
                
                min_cost = min_cost if min_cost < cost else cost

            heuristic += min_cost

        return heuristic

    def save(self, file, state):

        if (not self.goal_test(state)):
            file.write("Infeasible")
            return

        schedule = {}

        aux = copy.deepcopy(state)
        while aux.next != None:

            if (aux.plane not in schedule):
                schedule[aux.plane] = [] 

            schedule[aux.plane].insert(0, aux.trip_id)
            aux = aux.next

        trips   = self.problem["L"]["data"]
        ports   = self.problem["A"]["data"]
        planes  = self.problem["P"]["data"]
        p_class = self.problem["C"]["data"]

        profit = 0
        for plane in schedule:

            file.write("S " + plane)
            currTime = ports[trips[schedule[plane][0]].departure].open

            for trip_id in schedule[plane]:

                trip    = trips[trip_id]
                hour    = str(currTime // 60) if (currTime // 60) > 9 else str(0) + str(currTime // 60)
                minutes = str(currTime %  60) if (currTime %  60) > 9 else str(0) + str(currTime %  60) 

                str_trip = " " + hour + minutes + " " + trip.departure + " " + trip.arrival
                file.write(str_trip)

                plane_class = planes[plane].plane_class
                currTime   += trip.duration + p_class[plane_class].duration
                profit     += trip.profit[plane_class]
                
            file.write("\n")

        file.write("P " + str(profit) + "\n") 
