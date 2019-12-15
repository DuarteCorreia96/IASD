from probability import BayesNet, BayesNode, elimination_ask
import itertools
import copy

class Room():
    """ Class that saves the information about a room

        Saves the room name, and sets of every sensor 
        of the room and all adjacent rooms.
    """

    def __init__(self, name):
        """ Initiliazes a Room() with the given name 
        """

        self.name = name
        self.adj_rooms = set()
        self.sensors = set()

    def add_connection(self, room):
        """ Adds a adjacent room
        """

        self.adj_rooms.add(room)

    def add_sensor(self, sensor):
        """ Adds a sensor to the room
        """

        self.sensors.add(sensor)

    def __str__(self):

        to_print  = " Name: "  + self.name
        to_print += "\t Connected: " + str(self.adj_rooms) 
        to_print += "\t Sensors: "   + str(self.sensors)
    
        return to_print

class Sensor():
    """ Class that saves a sensor information.

        Saves the sensor id, the room where is 
        placed and the True Posite Rate (TPR) 
        and False Positive Rate (FPR) of the 
        sensor.
    """

    def __init__(self, sensor_info):
        """ Initiliazes the sensor with a array of sensor info

            This array should contain in positions:
                0: sensor id
                1: room of the sensor
                2: True Positive Rate
                3: False Positive Rate
        """

        self.id   = sensor_info[0] 
        self.room = sensor_info[1]
        self.TPR  = float(sensor_info[2])
        self.FPR  = float(sensor_info[3])

    def __str__(self):

        to_print  = " Id: " + self.id
        to_print += "\t Room: " + self.room 
        to_print += "\t TPR: " + self.TPR
        to_print += "\t FPR: " + self.FPR

        return to_print

class Problem:
    """ Class that saves a problem to be solved, also providing methods to solve it.

        It saves the needed variables to construct the baysean network and the network.
    """

    def __init__(self, file):
        """ Initializes the problem with an opened file.

        Creates the bayesian network onwhich every room is a child of itself 
        and the adjacent rooms at timestep t-1 and is parent of sensors that
        exist on the room and make measures at time t.  
        """

        self.rooms  = {}
        self.sensors = {}
        self.P       = 0
        self.measure = []

        # Fills the problem variables
        self.read_file(file)

        # Constructs the bayesian network
        str_temp = "{}_t_{}"
        bayes_template = []

        # First constructs the base network at time 0
        for room in self.rooms.values():
            bayes_template.append((str_temp.format(room.name, 0), '', 0.5))
        
        for sensor_id in self.measure[0]:

            sensor = self.sensors[sensor_id]
            bayes_template.append((str_temp.format(sensor.id, 0), str_temp.format(sensor.room, 0), {True: sensor.TPR, False: sensor.FPR}))

        # Then adds every timestep connecting rooms from the timestep before and sensors needed
        for k in range(1, len(self.measure)):

            for room in self.rooms.values():          
                aux_str =  str_temp.format(room.name, k - 1)  
                for parent in room.adj_rooms:
                    aux_str += " " + str_temp.format(parent, k - 1)  

                truth_table = self.create_truth_table(len(room.adj_rooms) + 1) if room.adj_rooms else {True: 1, False: 0} 
                bayes_template.append((str_temp.format(room.name, k), aux_str, truth_table))

            for sensor_id in self.measure[k]:

                sensor = self.sensors[sensor_id]
                bayes_template.append((str_temp.format(sensor.id, k), str_temp.format(sensor.room, k), {True: sensor.TPR, False: sensor.FPR}))

        self.network_template = BayesNet(bayes_template)

    def solve(self):
        """ Returns the room with higher probability of being on fire
        and that same probability using elimination_ask().
        """

        # Joins all measurements to a single one
        all_measures = {}
        for k in range(len(self.measure)):
            for key in self.measure[k]:
                all_measures[key + "_t_" + str(k)] = self.measure[k][key]

        # Calculates the probability of each room to be on fire
        current = {}
        for room in self.rooms.values():
            room_name = room.name + "_t_" + str(k)
            current[room.name] = elimination_ask(room_name, all_measures, self.network_template).prob[True]

        room = max(current, key = current.get)
        likelihood = current[room]
        
        return (room, likelihood)

    def create_truth_table(self, n_parents):
        """ Creates a truth table based on the number of parents the room has.

        The truth table probabilities are described as:
            If the same room is on fire then it will continue to be on fire (1)
            If a connected room is on fire then the room will be on fire with the 
                probability of the fire propagation (P)
            If the room is not on fire and no adjacent room is on fire then the 
                room will not be on fire (0)

        This table supposes that the same room at time t-1 is the first parent.
        """

        truth_table = {}
        combs = list(itertools.product([True, False], repeat = n_parents))

        for comb in combs:
            if(comb[0]):
                truth_table[comb] = 1
            elif(any(comb)):
                truth_table[comb] = self.P
            else:
                truth_table[comb] = 0

        return truth_table

    def read_file(self, file):
        """ Reads the file and saves the information needed
        to build the bayesian network.

            self.rooms   : Saves info of every room
            self.sensors : Saves info of every sensor
            self.P       : Fire propagation probability
            self.measure : Saves info of every measurement in order
        """

        lines = file.readlines()
        for line in lines:

            words = line[1:].split()

            if (line[0] == 'R'):

                for room in words:
                    self.rooms[room] = Room(room)

            elif (line[0] == 'C'):

                for connections in words: 
                    connection = connections.split(',')
                    self.rooms[connection[0]].add_connection(connection[1])
                    self.rooms[connection[1]].add_connection(connection[0])

            elif (line[0] == 'S'):
                
                for sensor in words:
                    sensor_info = sensor.split(':')   
                    self.sensors[sensor_info[0]] = Sensor(sensor_info)

                    room = sensor_info[1]
                    if (room not in self.rooms):
                        self.rooms[room] = Room(room)

                    self.rooms[room].add_sensor(sensor_info[0])

            elif (line[0] == 'P'):

                self.P =  float(words[0])

            elif (line[0] == 'M'):

                measure = {}
                for sensor in words:
                    sensor_info = sensor.split(':')  
                    measure[sensor_info[0]] = True if sensor_info[1] == 'T' else False

                self.measure.append(measure)

    def __str__(self):

        to_print = " Rooms:"
        for room in self.rooms.values():
            to_print += "\n\t" + str(room)

        to_print += "\n Sensors:"
        for sensor in self.sensors:
            to_print += "\n\t" + str(sensor)

        to_print += "\n P = " + str(self.P)
        to_print += "\n Meausures: "
        for measure in self.measure:
            to_print += "\n\t" + str(measure)

        return to_print

def solver(input_file):
    """ Method that returns the solution of a problem described in
    the input_file.
    """

    return Problem(input_file).solve()

import os, sys
import time

def main():

    files = os.listdir( 'examples/' )
    
    for filename in files:
        
        start = time.time()
        if (filename == 'solutions.txt'):
            continue
        
        with open("examples/" + filename, "r+") as file:
            solution = solver(file)
    
        print(filename, solution[0], solution[1])
        
        end = time.time()
        print(filename, end - start)


if __name__ == "__main__":
    main()
