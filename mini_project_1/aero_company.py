
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
        self.open  = words[2]
        self.close = words[3]

        self.trips = []

    def __str__(self):

        to_print  = "  Code: " + str(self.id)
        to_print += "  Open: " + str(self.open)
        to_print += "  Close: " + str(self.close)

        to_print += "  Trips: "
        for trip in self.trips:
            to_print += str(trip.id) + " | "

        return to_print

    def add_trip(self, trip):

        self.trips.append(trip)


class Plane_Class:

    def __init__(self, line):

        words = line.split()

        self.id        = words[1]
        self.duration  = words[2]
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
        self.duration  = words[3]

        self.profit = []
        self.id = Trip.counter

        Trip.counter += 1

        w = 4
        while (w + 1 < len(words)):

            self.profit.append((words[w], words[w + 1])) 
            w += 2

    def __str__(self):

        to_print  = "  From: " + str(self.departure)
        to_print += "  To: " + str(self.arrival)
        to_print += "  Duration: " + str(self.duration)

        template = "  | Class : {:4}   Profit : {:5}"
        for class_cost in self.profit:
            to_print += template.format(class_cost[0], class_cost[1])

        return to_print

    