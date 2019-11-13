import search
import copy
import sys

def convert_time_to_min(str_time):
    """ Converts a str "hhmm" to integer in minutes
    """

    minutes =  int(str_time) % 100
    hours   = (int(str_time) - minutes) // 100

    return hours * 60 + minutes

class Plane:
    """ Saves the information of a airplane.

        .id            :   name of the airplane.
        .plane_class   :   name of the class of 
                            the airplane
                        
    It should be initialized with a line starting with "P"
    """

    def __init__(self, line):

        words = line.split()

        self.id = words[1]
        self.plane_class = words[2]

    def __str__(self):

        to_print  = "  Name: " + str(self.id)
        to_print += "  Class: " + str(self.plane_class)

        return to_print


class Airport:
    """ Saves the information of an Airport.

        .id                :   name of the airport.
        .open              :   time of openning in minutes.
        .close             :   time of closing in minutes.
        .departure_trips   :   trips that depart from that airport
        .arrival_trips     :   trips that end at that airport
    
    It should be initialized with a line starting with "A"
    """

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


class Plane_Class:
    """ Saves information about a plane class.

        .id        :   name of the class.
        .duration  :   rotation time of the plane in minutes.
        .planes    :   set of the planes with that class.
    
    It should be initialized with a line starting with "C"
    """

    def __init__(self, line):

        words = line.split()

        self.id        = words[1]
        self.duration  = convert_time_to_min(words[2]) 
        self.planes    = set()

    def __str__(self):

        to_print  = "  Class: " + str(self.id)
        to_print += "  Duration: " + str(self.duration)

        to_print += "  Planes of the class: "
        for plane in self.planes:
            to_print += plane.id + " | "

        return to_print

    def add_plane(self, plane):

        self.planes.add(plane.id)


class Trip:
    """ Saves the information of a trip.

        .id        :   id of the trip.
        .departure :   departure airport.
        .arrival   :   arrival airport.
        .duration  :   trip duration in minutes.
        .profit    :   dictionary of the profit for every class
                        using the class as key.

    It also saves some global variables of every trip:

        Trip.counter:
            counts trips already created and serves as an id 
            counter so that there is no 2 trips with the same 
            id.

        Trip.min_cost: 
            cost that max profit plane class will have so 
            that it doesn't classes with cost 0, this cost 
            is half of the minimum cost found on every trip.

        Trip.min_order_inv:
            inverse of the most right significant number of cost.
            It's used on the heuristic to diferentiate states 
            with the same cost in order to select ones that 
            expand to less nodes.
    """

    counter       = 0
    min_cost      = sys.maxsize
    min_order_inv = 1

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

        self.max_profit = max(self.profit.values())

        min_cost = sys.maxsize
        for profit in self.profit.values():

            cost = self.max_profit - profit
            if (cost != 0):
                min_cost = min_cost if min_cost < cost / 2 else cost / 2

            while (cost * Trip.min_order_inv) - (cost * Trip.min_order_inv) // 1 > 0:
                Trip.min_order_inv *= 10

        Trip.min_cost = Trip.min_cost if Trip.min_cost < min_cost else min_cost


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

class State():
    """ Saves a state of the problem.

        .next       :   state that originated this state.
        .trip_id    :   trip made from last state to this one.
        .plane      :   plane that made the trip.
        .plane_time :   current time of the plane that made the trip.
        .cost       :   cost of the state.

    Values should be set after initialization of the state.

    It is initialized with the parent state that is set as .next.
    """

    # COMMENT FINAL
    nodes  = 1

    def __init__(self, old_state):

        self.next = old_state
        
        # Just to check branching factor
        # COMMENT FINAL
        State.nodes += 1

        # This values should be updated on result after state creation
        self.trip_id    = None
        self.plane      = ""
        self.plane_time = 0
        self.cost       = 0

    def __lt__(self, state):
        
        return self.cost < state.cost


class ASARProblem(search.Problem):

    def __init__(self):

        self.initial = State(None)
        self.goal = None # Goal will be defined in the goal_test function

    def load(self, file):
        """ Function used to load a new problem from a file.
        """

        # The dictionary that will save the full problem to be solved
        # This should not be changed outside of this function 
        # And should be used as read-only
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
            self.problem["A"]["data"][trip.departure].departure_trips.add(trip.id)
            self.problem["A"]["data"][trip.arrival].arrival_trips.add(trip.id)

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
        state as triples of (trip_id, airplane_id, plane_time).

        In the case where there are multiple planes of the same class 
        that still haven't done a trip only one of them is returned as
        a action for the trips remaining since they will create equal 
        branches with only the names changed.

        The function also checks if there are trips to return the planes
        that aren't in their starting airport to that same airport. In the 
        case of this being impossible the function returns no actions.
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
        planes_start = {}

        aux = copy.deepcopy(state)
        while aux.next != None:

            trip = trips[aux.trip_id]
            if (aux.plane not in planes_time):
                planes_time[aux.plane] = aux.plane_time
                airports[trip.arrival].add(aux.plane)

            
            planes_start[aux.plane] = trip.departure
            trips_done.add(trip.id)

            aux = aux.next
        
        # Trips that still need to be made
        trips_todo = trips.keys() - trips_done

        # Check if planes can return to start point
        for plane in planes_start:

            start = planes_start[plane]
            if (plane in airports[start]):
                continue

            trips_stop  = trips_todo.intersection(ports[start].arrival_trips)
            if (trips_stop == set()):
                return list()

        # Checks for 1 plane of every class for the unused planes
        planes_unused = set()
        planes_aux    = planes.keys() - planes_time.keys()
        
        for plane_class in p_class.values():
            aux = planes_aux.intersection(plane_class.planes)
            if (aux != set()):
                planes_unused.add(aux.pop())

        # For every remaining trip yield possible airplanes to that trip
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


    def heuristic(self, node):
        """ Calculates a heuristic for the distance of the current state
        to the goal_state.

        This heuristic is composed of 3 distinct parts:

            - Checks how many trips the state still needs to reach a goal 
            state and multiplies this values by the minimum cost of a trip.
            This is help in checking which state needs less actions to 
            reach a goal state.

            - Checks the minimal cost to return airplanes to the starting 
            airport checking if a airplane is not on the start the minimum
            cost of every trip that goes to that airport according to the 
            class of the airplane. If it's impossible to return the airplane 
            to the starting point a goal state cannot be reached and as such
            the heuristic returns a really high value. This part should be 
            usefull in distinguish states with the same amount of trips made.

            - Checks the amount of nodes that this state should expand to and 
            gives higher a higher heuristic score to nodes that expand more 
            states. In order for the heuristic to stay admissible this part only
            adds a values that is lower than the minimal difference between possible
            costs so that it only differentiates states that have the same cost. 
            This is useful because most problems have multiple optimal solutions,
            and this term "forces" the algorithm to not only find a optimal solution,
            but to find the one that has a better effective branching factor, leading 
            to an increase in efficiency in the search.
        """
        
        trips   = self.problem["L"]["data"]
        ports   = self.problem["A"]["data"]
        planes  = self.problem["P"]["data"]

        trips_done   = set()
        planes_start = {}
        airports     = {}
        for port in ports:
            airports[port] = set()

        aux = copy.deepcopy(node.state)
        while aux.next != None:

            trip = trips[aux.trip_id]
            if (aux.plane not in planes_start):
                airports[trip.arrival].add(aux.plane)

            planes_start[aux.plane] = trip.departure
            trips_done.add(trip.id)

            aux = aux.next

        trips_todo = trips.keys() - trips_done
        heuristic  = len(trips_todo) * Trip.min_cost
        for plane in planes_start:

            start = planes_start[plane]
            if (plane in airports[start]):
                continue

            trips_stop  = trips_todo.intersection(ports[start].arrival_trips)
            plane_class = planes[plane].plane_class

            if (trips_stop == set()):
                return sys.maxsize / 20

            min_cost = sys.maxsize
            for trip_id in trips_stop:

                trip = trips[trip_id]
                cost = trip.max_profit - trip.profit[plane_class]
                
                min_cost = min_cost if min_cost < cost else cost

            heuristic += min_cost

        # Prioritize states that origin less states
        action_counter = 0
        for _ in self.actions(node.state):
            action_counter += 1
        
        trip_min_order = 1 / Trip.min_order_inv
        heuristic += trip_min_order / 100 * (action_counter / (action_counter + 1))

        return heuristic

    def path_cost(self, current_cost, old_state, action, new_state):
        """ Returns the path cost of the new state, reached from the
        old state by applying action, knowing that the path cost of 
        old state is the current cost.

        This is simply the profit loss of using the class of the airplane
        on the trip when compared to the max profit plus the current cost.

        In the case of no profit loss the cost is set to a minimal cost 
        that is global for the whole problem.
        """

        trip = self.problem["L"]["data"][action[0]]
        plane_class = self.problem["P"]["data"][action[1]].plane_class

        cost = trip.max_profit - trip.profit[plane_class]
        if (cost == 0):
            cost = Trip.min_cost

        return current_cost + cost

    def goal_test(self, state):
        """ Returns True if state s is a goal state, 
        and False otherwise.
        """

        if (state == None):
            return False
            
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

        # Checks that every trip was made
        trips_todo = trips.keys() - trips_done
        if (trips_todo != set()):
            return False

        # checks that every airplane is on the starting airport
        for plane in planes_finish.keys():
            if (planes_start[plane] != planes_finish[plane]):
                return False

        return True


    def save(self, file, state):
        """ Saves the solution of the problem to an already 
        opened file.
        """

        if(not self.goal_test(state)):
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
