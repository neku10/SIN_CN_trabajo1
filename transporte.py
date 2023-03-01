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
            h = distance(state.cities[c], state.cities[destination])
            if g + h < best:
                best_city = c
                best = g + h
    return best_city

def select_new_location(state, origin, destination): 
    best = inf  # big float

    coordenates = {}
    coordenates.update(state.cities)
    coordenates.update(state.points)

    all_connection = {}
    all_connection.update(state.connection)
    all_connection.update(state.connection_points)
    for c in all_connection.keys():
        if c not in state.path_driver and c in all_connection[origin]:
            dist = distance(coordenates[c], coordenates[destination])
            if dist < best:
                best_loc = c
                best =  dist
    return best_loc


# Select driver near to truck
def select_driver(state, truck):  # evaluation function
    best = inf  # big float

    coordenates = {}
    coordenates.update(state.cities)
    coordenates.update(state.points)

    for driver in state.drivers.keys():
        if driver[0] != 'T':
            dist = distance(coordenates[state.drivers[driver]['location']], state.cities[state.trucks[truck]['location']])
            if dist < best:
                closest_driver = driver
                best = dist
    return closest_driver

#---------- OPERATORS --------------

# Move Truck operator
def move_to_city_op(state, destination, truck):
    origin = state.trucks[truck]['location']
    driver = driver_in_truck(state, truck)
    if destination in state.connection[origin] and driver != None:
        state.trucks[truck]['location'] = destination
        state.path.append(destination)
        return state
    return False

# walk
def walk_op(state, driver, destination): 
    state.drivers[driver]['location'] = destination
    return state

# take bus
def take_bus_op(state, driver, destination): 
    state.drivers[driver]['location'] = destination
    return state

def load_driver_op(state, driver, truck):
    if state.drivers[driver]['location'] == state.trucks[truck]['location']:
        state.drivers[driver]['location'] = truck
        return state
    return False


# Load package in truck
def load_package_op(state, package, truck):
    return False

pyhop.declare_operators(move_to_city_op, take_bus_op, walk_op)
print()
pyhop.print_operators()

#---------- METHODS ----------

def move_by_foot(state, driver, destination):
    coordenates = {}
    coordenates.update(state.cities)
    coordenates.update(state.points)
    driver_loc = coordenates[state.drivers[driver]['location']]
    driver_destination = coordenates[destination]
    dist = distance(driver_loc, driver_destination)
    if dist < 100:
        return [('walk_op', driver, destination)]
    return False

def move_by_bus(state, driver, destination):
    return [('take_bus_op', driver, destination)]

pyhop.declare_methods('move_driver_to_location', move_by_foot, move_by_bus)

# Mover camion 
def move_driver_m(state, goal, driver):
    origin = state.drivers[driver]['location']
    destination = goal.loc[driver]
    if origin != destination:
        location = select_new_location(state,origin,destination)
        return [('move_driver_to_location', driver, location), ('move_driver', goal, location)]
    return False

def already_there_d(state, goal, driver):
    origin = state.drivers[driver]['location']
    destination = goal.loc[driver]
    if origin == destination:
        return []
    return False

pyhop.declare_methods('move_driver', move_driver_m, already_there_d)

# Mover camion 
def move_to_city_m(state, goal, truck):
    origin = state.trucks[truck]['location']
    destination = goal.loc[truck]
    if origin != destination:
        city = select_new_city(state,origin,destination)
        driver = driver_in_truck(state, truck)
        if driver == None :
            driver = select_driver(state,truck)
            g = pyhop.Goal("d")
            g.loc = {}
            g.loc[driver] = origin
            return [('move_driver', g, driver), ('load_driver_op', driver, truck ),('move_to_city_op', city, truck), ('move_to_city', goal, truck)]    
        return [('move_to_city_op', city, truck), ('move_to_city', goal, truck)]
    return False

def already_there(state, goal, truck):
    origin = state.trucks[truck]['location']
    destination = goal.loc[truck]
    if origin == destination:
        return []
    return False

pyhop.declare_methods('move_to_city', move_to_city_m, already_there)

#---------- TASKS -------------

def relocate_trucks (state, goal ): 
    trucks = goal.loc.keys()
    for t in trucks: 
        origin = state.trucks[t]['location']
        destination = goal.loc[t]
        if origin != destination:
            return [('move_to_city', goal, t), ('relocate', goal)]
    return []
    
pyhop.declare_methods('relocate', relocate_trucks)

# Tranportar un paquete en un camion
def transport_by_truck(state, goal):
    packages = goal.loc.keys()
    operations = []
    truck = 'T1'
    
    # si hay packetes que no estan en su destino
    if len(packages) > 0:
        # Primero cargamos todos los paquetes
        for p in packages:
            origin = state.packages[p]['location']
            destination = goal.loc[p]
            # buscar paquetes que no estan en el destino
            if origin == destination:
                packages.remove(p)
            else: 
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
state1.connection_points = {'P_01': {'C0','C1'},'P_12': {'C1','C2'}}

# PARA PROBAR EL MOVIMIENTO DEL CAMION VAMOS A PONER UN CONDUCTOR DENTRO
state1.drivers = {'D1': {'location': 'P_01'},'D2': {'location': 'C2'}}
state1.packages = {'P1': {'location': 'C0', 'weight': 15},'P2': {'location': 'C0','weight': 50}}
state1.trucks = {'T1': {'capacity': 100, 'location': 'C1'}, 'T2': {'capacity': 500, 'location': 'C0'}}

state1.path = ['C1']
state1.path_driver = ['P_01']
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
# result = pyhop.pyhop(state1, [('transport', goal_packages)], verbose=3)
result = pyhop.pyhop(state1, [('relocate', goal_trucks)], verbose=3)
