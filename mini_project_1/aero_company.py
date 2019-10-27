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