#!/usr/bin/env python3.6

import probability

class Problem:

    def __init__(self, fh):
        lines = fh.readlines()
        [self.R, self.C, self.S, self.P, self.M] = process(lines)
        """"print(R)
        print(C)
        print(S)
        print(P)
        print(M)"""""
        parentsR = []
        parentsS = []
        for room in self.R:  # dictionary that associates each room with it adjacent rooms
            parents = []
            for edge in self.C:
                if edge[0] == room:
                    parents.append(edge[1])  # confirm that this isn't a problem
                elif edge[1] == room:
                    parents.append(edge[0])
            parentsR.append(parents)
            parents = []
            for sensor in self.S:
                if sensor[1] == room:  # allows more than one sensor per room
                    parents.append(sensor[0])
            parentsS.append(parents)
        self.adjDict = {self.R[i]: parentsR[i] for i in range(len(self.R))}
        self.sensDict = {self.R[i]: parentsS[i] for i in range(len(self.R))}

    def truthtable(self, n):
        if n < 1:
            return [[]]
        subtable = self.truthtable(n - 1)
        return [row + [v] for row in subtable for v in [True, False]]

    def solve(self):
        T, F = True, False
        net = probability.BayesNet()

        # time 0
        i = 0
        for room in self.R:
            net.add((room+str(i), '', 0.5))

        for sensor in self.S:
            a = float(sensor[2])
            b = float(sensor[3])
            net.add((sensor[0]+str(i), sensor[1]+'0', {T: a, F: b}))
        # as many time samples as measurements
        for k in range(len(self.M)-1):                               #ordem dos for esta a tornar o programa lento
            i = i + 1

            node_specs = []
            for room in self.R:                                      #room's nodes
                parents = room + str(i-1)                            #first parent is always the room at the previous sample time
                X = room + str(i)
                for p in self.adjDict[room]:
                    parents = parents + ' ' + p + str(i - 1)

                # probability table
                cpt = {}
                n = len(self.adjDict[room])+1
                matrix = self.truthtable(n)

                for element in matrix:
                    key = tuple(element)
                    value = 0                                       #confirm this value
                    if key[0] is T:
                        value = 1
                    else:
                        if len(key)>1:                              #safety
                            for bl in key[1:]:
                                if bl is True:
                                    value = self.P
                                    break
                    cpt.update({key: value})
                net.add((X, parents, cpt))

            for sensor in self.S:                                   #sensor nodes --> fazer dicionario com estes valores de TPR e FPR?
                a = float(sensor[2])
                b = float(sensor[3])
                net.add(((sensor[0])+str(i), (sensor[1] + str(i)), {T: a, F: b}))

        evidences = {}
        for i in range(len(self.M)):
            for sensor in self.M[i]:
                evidences.update({sensor[0]+str(i): sensor[1] is 'T'})
        p = {}
        for room in self.R:
            p.update({room : probablity.elimination_ask(room + str(len(self.M)-1), evidences, net)[1]})
        room = max(p, key=p.get)
        answer = (room, p[room])
        #print(answer)

        #name = self.R[0] + '0'
        """"name = 'S010'

        node = net.variable_node(name)
        print(node.variable, node.parents)"""""

        return answer


def process(lines):
    R=[]
    C=[]
    S=[]
    P=[]
    M=[]

    for ln in lines:

            if ln[0] == 'R':
                R.append([s for s in ln.split()[1:] ])

            if ln[0] == 'C':
                doors = ln.split()[1:]
                for door in doors:
                    aux = []
                    for i in range(len(door)):
                        if door[i] == ',':
                            aux.append(door[0:i])
                            aux.append(door[i+1:])
                    C.append(aux)

            if ln[0] == 'S':
                sensors = ln.split()
                for s in sensors[1:]:
                    j=0
                    aux = []
                    for i in range(len(s)):
                        if s[i] == ':':
                            aux.append(s[j:i])
                            j=i+1
                    aux.append(s[j:-1])
                    S.append(aux)

            if ln[0] == 'P':
                P.append([s for s in ln.split()[1:] ])

            if ln[0] == 'M':
                measures = ln.split()[1:]
                sampling = []
                for m in measures:
                    aux = []
                    for i in range(len(m)):
                        if m[i] == ':':
                            aux.append(m[0:i])
                            aux.append(m[i+1:])
                    sampling.append(aux)
                M.append(sampling)

    return [R[0], C, S, float(P[0][0]), M]


def solver(input_file):
    return Problem(input_file).solve()
