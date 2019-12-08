from probability import BayesNet, BayesNode, elimination_ask
import itertools
import copy

class Room():

    def __init__(self, name):

        self.name = name
        self.adj_rooms = set()
        self.sensors = set()

    def add_connection(self, room):

        self.adj_rooms.add(room)

    def add_sensor(self, sensor):

        self.sensors.add(sensor)

    def __str__(self):

        to_print  = " Name: "  + self.name
        to_print += "\t Connected: " + str(self.adj_rooms) 
        to_print += "\t Sensors: "   + str(self.sensors)
    
        return to_print

class Sensor():

    def __init__(self, sensor_info):

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

    def __init__(self, file):

        self.rooms  = {}
        self.sensors = {}
        self.P       = 0
        self.measure = []

        # Fill problem
        self.read_file(file)

        str_temp = "{}_t_{}"
        bayes_template = []
        for room in self.rooms.values():
            bayes_template.append((str_temp.format(room.name, 0), '', 0.5))
        
        for sensor_id in self.measure[0]:

            sensor = self.sensors[sensor_id]
            bayes_template.append((str_temp.format(sensor.id, 0), str_temp.format(sensor.room, 0), {True: sensor.TPR, False: sensor.FPR}))

        print(self.measure)
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

        for node in bayes_template:
            print(node)

        self.network_template = BayesNet(bayes_template)

    def solve(self):

        all_measures = {}
        for k in range(len(self.measure)):
            for key in self.measure[k]:
                all_measures[key + "_t_" + str(k)] = self.measure[k][key]

        print(all_measures)

        current = {}
        for room in self.rooms.values():
            room_name = room.name + "_t_" + str(k)
            current[room.name] = elimination_ask(room_name, all_measures, self.network_template).prob[True]

        room = max(current, key = current.get)
        likelihood = current[room]
        
        return (room, likelihood)

    def create_truth_table(self, n_parents):

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
    return Problem(input_file).solve()


def main():

    filename = "P5_5_4.txt"
    
    with open("examples/" + filename, "r+") as file:
        solution = solver(file)
    
    print(filename, solution[0], solution[1])

    print("P5_5_4.txt R03 0.9971396828553878")

if __name__ == "__main__":
    main()
