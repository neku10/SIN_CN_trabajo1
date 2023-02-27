from math import sqrt, pow, inf

import pyhop

#---------- EXTRA FUNCTIONS ----------

# Wich driver is in truck
def driver_in_truck(state, truck):
    for d in state.drivers.keys():
        if (state.drivers[d]['location'] == truck):
            return d
    return None

# Calculate distance between 2 points
def distance(c1, c2):
    x = pow(c1['X'] - c2['X'], 2)
    y = pow(c1['Y'] - c2['Y'], 2)
    return sqrt(x + y)

# Select next city to move
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

# Select driver near to truck


#---------- OPERATORS --------------

# Move Truck operator
def travel_op(state, destination, truck):
    origin = state.trucks[truck]['location']
    d = distance(state.coordinates[origin], state.coordinates[destination])
    driver = driver_in_truck(state, truck)
    if destination in state.connection[origin] and driver != None:
        state.trucks[truck]['location'] = destination
        state.path.append(destination)
        state.cost += d
        return state
    return False
    
# Load package in truck
def load_truck_op(state, package, truck):

    return False

#---------- ACTIONS ----------

# Tranportar un paquete en un camion
def transport_by_truck(state, goal):
    packages = goal.keys()
    operations = []
    truck = 'T1'
    
    # buscar paquetes que no estan en el destino
    for idx,package in packages:
        origin = state.packages[package]['location']
        destination = goal.loc[package]
        if origin == destination:
            packages.pop(idx)
    
    # si hay packetes que no estan en su destino
    if len(packages) > 0:
        # Primero cargamos todos los paquetes
        for p in packages:
            operations.append[('load_truck_op', p, truck)] # Cargar el paquete en el camion, checar si hay packetes que entregar en esa ciudad
        # Luego los repartimos
        for p in packages:
            operations.append[('transport_to_city', goal[p], truck)] # Mover el camion a la otra ciudad
            operations.append[('unload_truck_op', p, truck)] # Descargar el paquete del camion
        return operations
    return False

#def transport_by_truck_c0(state, goal):
#    return transport_by_truck(state, goal, 'c0')
#
#def transport_by_truck_c1(state, goal):
#    return transport_by_truck(state, goal, 'c1')
#
#
#def transport_by_truck_c2(state, goal):
#    return transport_by_truck(state, goal, 'c2')

pyhop.declare_methods('transport', transport_by_truck)
#pyhop.declare_methods('transport', transport_by_truck_c0, transport_by_truck_c1, transport_by_truck_c2)
print()
pyhop.print_methods()



#---------- INITIAL STATE ----------

state1 = pyhop.State('state1')
state1.cities = {'C0': {'X': 30, 'Y': 255}, 'C1': {'X': 190, 'Y': 70}, 'C2': {'X': 230, 'Y': 340}}
state1.connection = {'C0': {'C1','C2'}, 'C1': {'C0', 'C2'}, 'C2': {'C0', 'C1'}}
state1.points = {'P_01': {'X': 50, 'Y': 150}, 'P_12': {'X': 200, 'Y': 210}}
state1.connectionPoints = {'P_01': {'C0','C1'},'P_12': {'C1','C2'}}

# PARA PROBAR EL MOVIMIENTO DEL CAMION VAMOS A PONER UN CONDUCTOR DENTRO
state1.drivers = {'D1': {'location': 'P_01'},'D2': {'location': 'T1'}}
state1.packages = {'P1': {'location': 'C0', 'weight': 15},'D2': {'location': 'C0','weight': 50}}
state1.trucks = {'T1': {'capacity': 100, 'location': 'C1'}, 'T2': {'capacity': 500, 'location': 'C0'}}

state1.path = ['C1']
state1.cost = 0


#---------- GOAL ----------
# un goal por cada requisito del proyecto
goal_packages = pyhop.Goal('goal_packages')
goal_trucks = pyhop.Goal('goal_trucks')
goal_drivers = pyhop.Goal('goal_drivers')
#goal1.final = 'C0'

# Definicion del objetivo
goal_packages.loc = {'P1': 'C1', 'P2': 'C2'}
goal_trucks.loc = {'T1': 'C0'}
goal_drivers.loc = {'D1': 'C0'}
#goal1 = pyhop.Goal('goal1')

# print('- If verbose=3, Pyhop also prints the intermediate states:')

# call to the planner
result = pyhop.pyhop(state1, [('transport', goal_packages)], verbose=3)
