from math import sqrt, pow, inf

import pyhop

def distance(c1, c2):
    x = pow(c1['X'] - c2['X'], 2)
    y = pow(c1['Y'] - c2['Y'], 2)
    return sqrt(x + y)

def select_new_city(state, origin, destination):  # evaluation function
    best = inf  # big float
    for c in state.connection.keys():
        if c not in state.path and c in state.connection[origin]:
            g = state.cost
            h = distance(state.coordinates[c], state.coordinates[destination])
            if g + h < best:
                best_city = c
                best = g + h
    return best_city

def travel_op(state, destination, truck):
    origin = state.trucks[truck]['location']
    d = distance(state.coordinates[origin], state.coordinates[destination])
    if destination in state.connection[origin] and state.location =='inside_truck':
        state.trucks[truck]['location'] = destination
        state.path.append(destination)
        state.cost += d
        return state
    else:
        return False
    


def transport_by_truck(state, goal, truck):
    origin = state.trucks[truck].location
    destination = goal.loc[truck]
    if origin != destination:
        return [('load_truck_op', truck), ('transport_to_city', goal, truck), ('unload_truck_op', truck)]
    return False

def transport_by_truck_c0(state, goal):
    return transport_by_truck(state, goal, 'c0')


def transport_by_truck_c1(state, goal):
    return transport_by_truck(state, goal, 'c1')


def transport_by_truck_c2(state, goal):
    return transport_by_truck(state, goal, 'c2')

pyhop.declare_methods('transport', transport_by_truck)
#pyhop.declare_methods('transport', transport_by_truck_c0, transport_by_truck_c1, transport_by_truck_c2)
print()
pyhop.print_methods()



# INITIAL STATE

state1 = pyhop.State('state1')
state1.cities = {'C0': {'X': 30, 'Y': 255}, 'C1': {'X': 190, 'Y': 70}, 'C2': {'X': 230, 'Y': 340}}
state1.connection = {'C0': {'C1','C2'}, 'C1': {'C0', 'C2'}, 'C2': {'C0', 'C1'}}
state1.points = {'P_01': {'X': 50, 'Y': 150}, 'P_12': {'X': 200, 'Y': 210}}
state1.connectionPoints = {'P_01': {'C0','C1'},'P_12': {'C1','C2'}}
state1.drivers = {'D1': {'location': 'P_01'},'D2': {'location': 'C1'}}
state1.packages = {'P1': {'location': 'C0', 'weight': 15},'D2': {'location': 'C0','weight': 50}}
state1.trucks = {'t1': {'capacity': 100, 'location': 'C1'}, 't2': {'capacity': 500, 'location': 'C0'}}


state1.location = 'C1'
state1.path = ['C1']
state1.cost = 0



# GOAL
goal1 = pyhop.Goal('goal1')
#goal1.final = 'C0'

# Definicion del objetivo

#goal1 = pyhop.Goal('goal1')
goal1.loc = {'D1': 'C0', 'T1': 'C0'}

# print('- If verbose=3, Pyhop also prints the intermediate states:')

# call to the planner
result = pyhop.pyhop(state1, [('transport', goal1)], verbose=3)
