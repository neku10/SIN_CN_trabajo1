from math import sqrt, pow, inf

import pyhop

#---------- EXTRA FUNCTIONS ----------

# Bus Rate
def bus_rate(dist):
    return 0.4 + 0.05 * dist

# Change path to next route
def nextPath(paths, text):
    return [text + "-" + path for path in paths]

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
def select_new_city(state, origin, destination, truck):  # evaluation function
    best = inf  # big float
    for c in state.connection.keys():
        if c not in state.trucks[truck]['path'] and c in state.connection[origin]:
            g = state.cost
            h = distance(state.cities[c], state.cities[destination])
            if g + h < best:
                best_city = c
                best = g + h
    return best_city

def select_new_location(state, origin, destination, driver): 
    best = inf  # big float

    coordenates = {}
    coordenates.update(state.cities)
    coordenates.update(state.points)

    for c in state.connection_points.keys():
        if c not in state.drivers[driver]['path'] and c in state.connection_points[origin]:
            dist = distance(coordenates[c], coordenates[destination])
            if dist < best:
                best_loc = c
                best =  dist
    return best_loc


# Select driver near to truck
def select_driver(state, truck):  # evaluation function
    driver = driver_in_truck(state, truck)
    if driver != None: return driver

    best = inf  # big float
    best_in_truck = inf
    coordenates = {}
    coordenates.update(state.cities)
    coordenates.update(state.points)
    closest_driver = None
    for driver in state.drivers.keys():
        if state.drivers[driver]['location'][0] != 'T':
            dist = distance(coordenates[state.drivers[driver]['location']], state.cities[state.trucks[truck]['location']])
            if dist < best:
                closest_driver = driver
                best = dist
        else:
            dist = distance(coordenates[state.trucks[state.drivers[driver]['location']]['location']], state.cities[state.trucks[truck]['location']])
            if dist < best_in_truck:
                closest_driver_in_truck = driver
                best_in_truck = dist
    if closest_driver == None:
        return closest_driver_in_truck
    return closest_driver

# Select driver near to truck
def select_truck(state, package):  # evaluation function
    if state.packages[package]['location'][0]  == 'T':
        return state.packages[package]['location']
    
    best = inf  # big float

    closest_truck = None
    for truck in state.trucks.keys():
        if truck not in state.closest_truck :
            dist = distance(state.cities[state.packages[package]['location']], state.cities[state.trucks[truck]['location']])
            if dist < best:
                closest_truck = truck
                best = dist
    state.closest_truck.append(closest_truck)
    return closest_truck

def order_trucks_with_driver(state, trucks): 
    n = len(trucks)
    for i in range(0, n-1):
        if driver_in_truck(state,trucks[i]) != None:
            trucks[i], trucks[0] = trucks[0], trucks[i]
            break
    return trucks
         
#---------- OPERATORS --------------

# Move Truck operator
def move_to_city_op(state, destination, truck):
    origin = state.trucks[truck]['location']
    driver = driver_in_truck(state, truck)
    if destination in state.connection[origin] and driver != None:
        state.trucks[truck]['location'] = destination
        state.trucks[truck]['path'].append(destination)
        return state
    return False

# walk
def walk_op(state, driver, destination): 
    state.drivers[driver]['location'] = destination
    state.drivers[driver]['path'].append(destination)
    return state

# take bus
def take_bus_op(state, driver, destination, rate):
    state.drivers[driver]['location'] = destination
    state.drivers[driver]['path'].append(destination)
    state.drivers[driver]['cash'] = round(state.drivers[driver]['cash'] - rate,2)
    return state

def load_driver_op(state, driver, truck):
    if state.drivers[driver]['location'] == state.trucks[truck]['location']:
        state.drivers[driver]['location'] = truck
        return state
    return False

def unload_driver_op(state, driver, truck):
    if state.drivers[driver]['location'] == truck:
        destination = state.trucks[truck]['location']
        state.drivers[driver]['location'] =  destination
        state.drivers[driver]['path'] = nextPath(state.drivers[driver]['path'], 'done')
        state.drivers[driver]['path'].append(destination)

        return state
    return False

# Load package in truck
def load_package_op(state, package, truck):
    driver = driver_in_truck(state, truck)
    if state.packages[package]['location'] == state.trucks[truck]['location']:
        state.packages[package]['location'] = truck
        state.trucks[truck]['path'] = nextPath(state.trucks[truck]['path'], 'done')
        state.closest_truck = []
        return state
    return False

# Unload package from truck
def unload_package_op(state, package, truck):
    if state.packages[package]['location'] == truck:
        state.packages[package]['location'] = state.trucks[truck]['location']
        state.trucks[truck]['path'] = nextPath(state.trucks[truck]['path'], 'done')
        return state
    return False

pyhop.declare_operators(load_package_op, unload_package_op, move_to_city_op, load_driver_op, unload_driver_op,  take_bus_op, walk_op)
print()
pyhop.print_operators()

#---------- METHODS ----------

def move_by_bus(state, driver, destination):
    coordenates = {}
    coordenates.update(state.cities)
    coordenates.update(state.points)
    driver_loc = coordenates[state.drivers[driver]['location']]
    driver_destination = coordenates[destination]
    dist = distance(driver_loc, driver_destination)
    rate = bus_rate(dist)
    if rate <= state.drivers[driver]['cash'] and dist > 100:
        return [('take_bus_op', driver, destination, rate)]
    return False

def move_by_foot(state, driver, destination):
    return [('walk_op', driver, destination)]

pyhop.declare_methods('move_driver_to_location', move_by_bus, move_by_foot)

# Mover camion 
def move_driver_m(state, goal, driver):
    origin = state.drivers[driver]['location']
    destination = goal.loc[driver]
    if origin != destination:
        if origin[0] == 'T' :
            return [('unload_driver_op', driver, origin), ('move_driver', goal, driver)]
        location = select_new_location(state,origin,destination, driver)
        return [('move_driver_to_location', driver, location), ('move_driver', goal, driver)]
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
        city = select_new_city(state,origin,destination, truck)
        driver = driver_in_truck(state, truck)
        if driver == None :
            driver = select_driver(state,truck)
            if driver == None:
                return False
            g = pyhop.Goal("d")
            g.loc = {}
            g.loc[driver] = origin
            return [('move_driver', g, driver), ('load_driver_op', driver, truck ),('move_to_city', goal, truck)]    
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

def relocate_drivers_m (state, goal ): 
    drivers = goal.loc.keys()
    for d in drivers: 
        origin = state.drivers[d]['location']
        destination = goal.loc[d]
        if origin != destination:
            return [('move_driver', goal, d), ('relocate_drivers', goal)]
    return []
    
pyhop.declare_methods('relocate_drivers', relocate_drivers_m)

def relocate_trucks_m (state, goal ): 
    trucks = order_trucks_with_driver(state, list(goal.loc.keys()))

    for t in trucks: 
        origin = state.trucks[t]['location']
        destination = goal.loc[t]
        if origin != destination:
            return [('move_to_city', goal, t), ('relocate_trucks', goal)]
    return []
    
pyhop.declare_methods('relocate_trucks', relocate_trucks_m)

def transport_packages_m (state, goal) :
    packages = goal.loc.keys()
    for p in packages:
        origin = state.packages[p]['location']
        destination = goal.loc[p]
        if origin != destination:
            if origin[0] != 'T' :
                truck = select_truck(state, p)
                g1 = pyhop.Goal('T')
                g1.loc = {}
                g1.loc[truck] = origin
                if select_driver(state,truck) != None:
                    return [('move_to_city', g1, truck), ('load_package_op', p, truck), ('transport_packages', goal)  ]
                return [('transport_packages', goal)  ]
            g = pyhop.Goal('TP')
            g.loc = {}
            g.loc[origin] = destination
            return [('move_to_city', g, origin), ('unload_package_op', p, origin), ('transport_packages', goal)]
    return []

pyhop.declare_methods('transport_packages', transport_packages_m)

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

pyhop.declare_methods('transport', transport_by_truck)
print()
pyhop.print_methods()


#---------- INITIAL STATE ----------

state1 = pyhop.State('state1')
state1.cities = {'C0': {'X': 30, 'Y': 255}, 'C1': {'X': 190, 'Y': 70}, 'C2': {'X': 230, 'Y': 340},
                 'C3': {'X': 48, 'Y': 25}, 'C4': {'X': 10, 'Y': 0}, 'C5': {'X': 115, 'Y': 180},
                 'C6': {'X': 300, 'Y': 51}, 'C7': {'X': 250, 'Y': 267}, 'C8': {'X': 27, 'Y': 132}}
state1.connection = {'C0': {'C1','C2','C5','C7','C8'}, 'C1': {'C0','C2','C3','C5','C6'}, 'C2': {'C0', 'C1','C5','C7'},
                     'C3': {'C1','C4','C6','C8'},'C4': {'C3'},'C5': {'C0','C1','C2','C7','C8'},'C6': {'C1','C3','C7'},
                     'C7': {'C0','C2','C5','C6'}, 'C8': {'C0','C3','C5'}}
state1.points = {'P_01': {'X': 50, 'Y': 150},'P_08': {'X': 18, 'Y': 186},'P_12': {'X': 200, 'Y': 210},
                 'P_13': {'X': 119, 'Y': 64},'P_15': {'X': 147, 'Y': 122},'P_16': {'X': 250, 'Y': 78},
                 'P_27': {'X': 271, 'Y': 313},'P_34': {'X': 18, 'Y': 33},'P_48': {'X': 19, 'Y': 88},
                 'P_67': {'X': 345, 'Y': 211}}
state1.connection_points = {'P_01': {'C0','C1'},'P_08': {'C0','C8'},'P_12': {'C1','C2'},'P_13': {'C1','C3'},
                            'P_15': {'C1','C5'},'P_16': {'C1','C6'},'P_27': {'C2','C7'},'P_34': {'C3','C4'},
                            'P_48': {'C4','C8'},'P_67': {'C6','C7'},'C0': {'P_01','P_08'},
                            'C1': {'P_01', 'P_12','P_13','P_15','P_16'}, 'C2': {'P_12','P_27'},'C3': {'P_13', 'P_34'},
                            'C4': {'P_34', 'P_48'},'C5': {'P_15'},'C6': {'P_16', 'P_67'},'C7': {'P_27', 'P_67'},
                            'C8': {'P_08', 'P_48'}}

# PARA PROBAR EL MOVIMIENTO DEL CAMION VAMOS A PONER UN CONDUCTOR DENTRO
state1.drivers = {'D1': {'location': 'P_01', 'path':['P_01'], 'cash':50},'D2': {'location': 'C2', 'path':['C2'], 'cash':4000},
                  'D3': {'location': 'P_01', 'path':['P_01'], 'cash':30},'D4': {'location': 'P_12', 'path':['P_12'], 'cash':0}}
#state1.drivers = {'D1': {'location': 'P_01', 'path':['P_01']}}
state1.packages = {'P1': {'location': 'C0', 'weight': 15},'P2': {'location': 'C0','weight': 50},
                   'P3': {'location': 'C6', 'weight': 15},'P4': {'location': 'C7','weight': 50}}
state1.trucks = {'T1': {'capacity': 100, 'location': 'C1', 'path':['C1']}, 'T2': {'capacity': 500, 'location': 'C4', 'path':['C4']},
                 'T3': {'capacity': 100, 'location': 'C2', 'path':['C2']}, 'T4': {'capacity': 500, 'location': 'C0', 'path':['C0']}}
#state1.trucks = {'T1': {'capacity': 100, 'location': 'C1', 'path':['C1']}}

state1.cost = 0
state1.closest_truck = []


#---------- GOAL ----------
# un goal por cada requisito del proyecto
goal_packages = pyhop.Goal('goal_packages')
goal_trucks = pyhop.Goal('goal_trucks')
goal_drivers = pyhop.Goal('goal_drivers')
#goal1.final = 'C0'

# Definicion del objetivo
goal_packages.loc = {'P1': 'C6', 'P2': 'C4','P3': 'C6', 'P4': 'C3'}
goal_trucks.loc = {'T1': 'C0', 'T2': 'C2', 'T3': 'C8'}
goal_drivers.loc = {'D1': 'C2', 'D2': 'P_12'}
#goal1 = pyhop.Goal('goal1')

# print('- If verbose=3, Pyhop also prints the intermediate states:')

# call to the planner
# result = pyhop.pyhop(state1, [('transport', goal_packages)], verbose=3)
result = pyhop.pyhop(state1, [('transport_packages', goal_packages), ('relocate_trucks', goal_trucks), ('relocate_drivers', goal_drivers)], verbose=3)