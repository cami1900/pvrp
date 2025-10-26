import matplotlib.pyplot as plt
import numpy as np
import itertools 
import random
import copy
import conf


''' MAIN FUNCRIONS '''

# feasibility function considering the 1-vehicle constraint
def check_feasibility_1vehicle(n_vehicles, n_days, n_clients, data, max_clients_kd, vehicle_capacity, distance_matrix, solution):

    # Initialize feasibility and verification vectors:
    # solution = copy.copy(given_solution)
    # feasibility_vector = solution.feasibility_vector()
    # verification_vector = solution.verification_vector()
    # solution.fesibility_vector.initialize()
    # solution.verification_vector.initialize()

    # Create the Rotes matrix: 
    # each matrix is n_clients x n_clients and a element(i, j) is =1 
    # if the vehicle k in the day t goes from customer i to customer j
    routes_matrix = define_routes(n_vehicles, n_days, n_clients, max_clients_kd, solution.assigned_ordered_matrix)
 
    for client_i in range(1, n_clients):

        # Create Ci_assign_matrix
        Ci_assign_matrix = create_customer_matrix(n_vehicles, n_days, client_i, solution.assigned_ordered_matrix)
        # print(f"Client {client_i} assignetion matrix:\n", Ci_assign_matrix)

        # CONSTR 1: required frequency constr
        solution = check_frequency(data, client_i, Ci_assign_matrix, solution)

        # CONSTR 2: 1schedule-1vehicle contraint
        solution = check_sched_vehicle(data, client_i, Ci_assign_matrix, solution)

        # CONSTR 4: for each client i there must be an outing arc (i, j)
        solution = check_arc_existance(client_i, routes_matrix, Ci_assign_matrix, solution)

        # CONSTR 5: flow conservetion -> (for each client i) for each outing arc (i, j) there must be an incoming arc (k, i)
        solution = check_flow_conservation(client_i, routes_matrix, Ci_assign_matrix, solution)

    # verify results: verify the total distance traveled
    V_distances_matrix, solution = verify_distance(n_vehicles, n_days, n_clients, routes_matrix, distance_matrix, solution.route_dist_matrix, solution)

    # verify results: verify the total load transported
    V_loads_matrix, solution = verify_load(data, n_vehicles, n_days, n_clients, max_clients_kd, routes_matrix, solution.transp_demand_matrix, solution)

    # CONSTR 3: vehicle capacity contraint
    solution = check_capacity(n_vehicles, n_days, V_loads_matrix, vehicle_capacity, solution)

    # CONSTR 6: subtour elimination
    solution = check_subtour_elimination(n_vehicles, n_days, n_clients, routes_matrix, solution)

    # Update feasibility and verification vectors:

    
    return V_distances_matrix, V_loads_matrix, solution


# feasibility function PVRP
def check_feasibility_pvrp(n_vehicles, n_days, n_clients, data, max_clients_kd, vehicle_capacity, distance_matrix, solution):

    # Initialize feasibility and verification vectors:
    # solution = copy.copy(given_solution)
    # feasibility_vector = solution.feasibility_vector()
    # verification_vector = solution.verification_vector()
    # solution.fesibility_vector.initialize()
    # solution.verification_vector.initialize()

    # Create the Rotes matrix: 
    # each matrix is n_clients x n_clients and a element(i, j) is =1 
    # if the vehicle k in the day t goes from customer i to customer j
    routes_matrix = define_routes(n_vehicles, n_days, n_clients, max_clients_kd, solution.assigned_ordered_matrix)
 
    for client_i in range(1, n_clients):

        # Create Ci_assign_matrix
        Ci_assign_matrix = create_customer_matrix(n_vehicles, n_days, client_i, solution.assigned_ordered_matrix)
        # print(f"Client {client_i} assignetion matrix:\n", Ci_assign_matrix)

        # CONSTR 1: required frequency constr
        solution = check_frequency(data, client_i, Ci_assign_matrix, solution)

        # CONSTR 2: 1schedule-1vehicle contraint
        # solution = check_sched_vehicle(data, client_i, Ci_assign_matrix, solution)

        period_schedule = np.zeros(n_days, dtype=int)
        for day in range(n_days):
            visits_per_day = 0
            for vehicle in range(n_vehicles):
                visits_per_day += Ci_assign_matrix[vehicle, day]
            period_schedule[day] = visits_per_day 
        # actual_schedule = int(''.join(map(str, period_schedule)), 2)
        actual_schedule = int(''.join(str(b) for b in period_schedule), 2)
        possible_schedules = data[client_i, conf.VISIT_START_INDEX:]

        if any(day_in_period > 1 for day_in_period in period_schedule) or not np.intersect1d(actual_schedule, possible_schedules).size:
            solution.feasibility_vector.constr_2 = False


        # CONSTR 4: for each client i there must be an outing arc (i, j)
        solution = check_arc_existance(client_i, routes_matrix, Ci_assign_matrix, solution)

        # CONSTR 5: flow conservetion -> (for each client i) for each outing arc (i, j) there must be an incoming arc (k, i)
        solution = check_flow_conservation(client_i, routes_matrix, Ci_assign_matrix, solution)

    # verify results: verify the total distance traveled
    V_distances_matrix, solution = verify_distance(n_vehicles, n_days, n_clients, routes_matrix, distance_matrix, solution.route_dist_matrix, solution)

    # verify results: verify the total load transported
    V_loads_matrix, solution = verify_load(data, n_vehicles, n_days, n_clients, max_clients_kd, routes_matrix, solution.transp_demand_matrix, solution)

    # CONSTR 3: vehicle capacity contraint
    solution = check_capacity(n_vehicles, n_days, V_loads_matrix, vehicle_capacity, solution)

    # CONSTR 6: subtour elimination
    solution = check_subtour_elimination(n_vehicles, n_days, n_clients, routes_matrix, solution)

    # Update feasibility and verification vectors:

    
    return V_distances_matrix, V_loads_matrix, solution



''' SECONDARY FUNCTIONS'''

def define_routes(n_vehicles, n_days, n_clients, max_clients_kd, assigned_ordered_matrix):

    routes_matrix = np.zeros((n_vehicles, n_days, n_clients, n_clients), dtype=int)
    
    for vehicle_k in range(n_vehicles):
        for day_t in range(n_days):
            for client_i in range(max_clients_kd+1):
                curren_client = assigned_ordered_matrix [vehicle_k][day_t][client_i]
                next_client = assigned_ordered_matrix [vehicle_k][day_t][client_i+1]
                routes_matrix[vehicle_k][day_t][curren_client][next_client] = 1

            routes_matrix[vehicle_k][day_t][0][0] = 0                

    return routes_matrix



def create_customer_matrix(n_vehicles, n_days, client_i, assigned_ordered_matrix):

    Ci_assign_matrix = np.zeros((n_vehicles, n_days), dtype=int)
    vehicle_k, day_t, position = np.where(assigned_ordered_matrix == client_i)
    Ci_assign_matrix[vehicle_k, day_t] = 1

    return Ci_assign_matrix



def check_frequency(data, client_i, Ci_assign_matrix, solution):
    # CONSTR 1: required frequency constr

    required_frequency = data[client_i, conf.FREQ_VISIT_INDEX]
    actual_frequency = Ci_assign_matrix.sum()

    if float(actual_frequency) != required_frequency:
        solution.feasibility_vector.constr_1 = False
        print(f"Incorrect frequency for client {client_i}: expected {required_frequency}, found {actual_frequency}")
        # if actual_frequency == 0:
        #     print(solution.not_assigned_list)
        #     idx = np.where(solution.not_assigned_list == 0)[0][0]  # Trova la posizione in cui compare il primo posto libero
        #     solution.not_assigned_list[idx] = client_i    # inserisce il nuovo cliente
        #     print("not_assigned_list has been updated:\n", solution.not_assigned_list)

    # else:
    #     if solution.fesibility_vector.constr_1 != False:
    #         solution.fesibility_vector.constr_1 += 1


    # raise ValueError(f"Incorrect frequency for client {client_i}: expected {required_frequency}, found {actual_frequency}")
    return solution



def check_sched_vehicle(data, client_i, Ci_assign_matrix, solution):
    # CONSTR 2: 1schedule-1vehicle contraint
    
    actual_schedules = np.array([int(''.join(map(str, row)), 2) for row in Ci_assign_matrix])
    possible_schedules = data[client_i, conf.VISIT_START_INDEX:]

    # if len(actual_schedules[actual_schedules != 0]) != 1:
    #     print(f"Incorrect assignation to vehicle of client {client_i}: it has been assigned to {len(actual_schedules[actual_schedules != 0])} vehicles")
    
    # if not np.intersect1d(actual_schedules, possible_schedules).size:
    #     print("no elements")

    if len(actual_schedules[actual_schedules != 0]) != 1 or not np.intersect1d(actual_schedules, possible_schedules).size:
        solution.feasibility_vector.constr_2 = False
        print(f"Incorrect assignation to vehicle-schedule of client {client_i}: it has been assigned to {len(actual_schedules[actual_schedules != 0])} vehicles and to {(actual_schedules[actual_schedules != 0])} schedules")
    
    # else:
    #     if solution.fesibility_vector.constr_2 != False:
    #         solution.fesibility_vector.constr_2 += 1

    return solution



def check_arc_existance(client_i, routes_matrix, Ci_assign_matrix, solution):
    # CONSTR 4: for each client i there must be an outing arc (i, j)

    # Ci_assign_matrix = np.array([[0, 0, 0], [1, 0, 1]])

    v_idx, d_idx = np.where(Ci_assign_matrix == 1)

    for v, d in zip(v_idx, d_idx):
        if not np.any(routes_matrix[v, d, client_i] == 1):  # check that in row client_i exists at list one arc (i, j)
            solution.feasibility_vector.constr_4 = False
            # print(f"Missing arc existance for {client_i}" )

        # else:
        #     solution.fesibility_vector.constr_4 = True

    return solution



def check_flow_conservation(client_i, routes_matrix, Ci_assign_matrix, solution):
    # CONSTR 5: flow conservetion -> (for each client i) for each outing arc (i, j) there must be an incoming arc (k, i)
    
    # Ci_assign_matrix = np.array([[0, 0, 0], [1, 0, 1]])

    v_idx, d_idx = np.where(Ci_assign_matrix == 1)

    for v, d in zip(v_idx, d_idx):
        if not np.any(routes_matrix[v, d, :, client_i] == 1):   # check that in column client_i exists at list one arc (k ,i)
            solution.feasibility_vector.constr_5 = False
            # print(f"Flow is not conserved for {client_i}" )

        # else:
        #     solution.fesibility_vector.constr_5 = True

    return solution



def verify_distance(n_vehicles, n_days, n_clients, routes_matrix, distance_matrix, route_dist_matrix, solution):

    transpose_routes_matrix = np.zeros((n_vehicles, n_days, n_clients, n_clients), dtype=int)
    V_distances_matrix = np.zeros((n_vehicles, n_days), dtype=float)
    
    # transpose_routes_matrix[v_idx, d_idx] = np.transpose(routes_matrix[v_idx, d_idx])
    for v in range(n_vehicles):
        for d in range(n_days):
            transpose_routes_matrix[v, d] = np.transpose(routes_matrix[v, d])    # axes=(0, 1, 3, 2) lascia intatti (v=0, d=1) e inverte i clienti (i=2, j=3) -> 3, 2 
            muliply_matrix = transpose_routes_matrix[v, d] @ distance_matrix
            V_distances_matrix[v, d] = np.trace(muliply_matrix)

            # if V_distances_matrix[v, d] != route_dist_matrix[v, d]:
            #     solution.verification_vector.verif_dist = False
            #     print(f"Total distance of vehicle {v} in the day {d} is wrong")

            if not np.isclose(V_distances_matrix[v, d], route_dist_matrix[v, d], 1e-06, 1e-06):
                solution.verification_vector.verif_dist = False
                print(f"Total distance of vehicle {v} in the day {d} is wrong")
                # print(V_distances_matrix[v, d] - route_dist_matrix[v, d])

            # else:
            #     solution.verification_vector.verif_dist = True

    # transpose_routes_matrix = np.transpose(routes_matrix, axes=(0, 1, 3, 2))    # axes=(0, 1, 3, 2) lascia intatti (v=0, d=1) e inverte i clienti (i=2, j=3) -> 3, 2 
    # muliply_matrix = transpose_routes_matrix[v_idx, d_idx] @ distance_matrix
    # V_distances_matrix[v_idx, d_idx] = np.trace(muliply_matrix)
    # ValueError: shape mismatch: value array of shape (6,6,6,6) could not be broadcast to indexing result of shape (2,3,6,6)

    #  # Transpose last two dims (clients) of routes_matrix
    # transpose_routes_matrix = routes_matrix.transpose(0, 1, 3, 2)  # (v, d, j, i)

    # # Moltiplicazione batch (v, d, j, i) @ (i, k) → (v, d, j, k)
    # mul_matrix = np.einsum('vdji,ik->vdjk', transpose_routes_matrix, distance_matrix)

    # # Traccia per ogni (v, d): somma diagonale per j=k
    # V_distances_matrix = np.einsum('vdii->vd', mul_matrix)

    return V_distances_matrix, solution



def verify_load(data, n_vehicles, n_days, n_clients, max_clients_kd, routes_matrix, transp_demand_matrix, solution):

    V_loads_matrix = np.zeros((n_vehicles, n_days), dtype=int)

    for v in range(n_vehicles):
        for d in range(n_days):
            clients_i_j = np.where(routes_matrix[v, d] == 1)
            V_loads_matrix[v, d] = data[clients_i_j[0], conf.DEMAND_INDEX].sum()

            if V_loads_matrix[v, d] != transp_demand_matrix[v, d]:
                solution.verification_vector.verif_load = False
                # print(f"Total load of vehicle {v} in the day {d} is wrong")

            # else:
            #     solution.verification_vector.verif_load = True


    return V_loads_matrix, solution



def check_capacity(n_vehicles, n_days, V_loads_matrix, vehicle_capacity, solution):
    # CONSTR 3: vehicle capacity contraint

    for v in range(n_vehicles):
        for d in range(n_days):
            if V_loads_matrix[v, d] > vehicle_capacity:
                solution.feasibility_vector.constr_3 = False
                # print(f"Total load of vehicle {v} in the day {d} is bigger than total capacity: {V_loads_matrix[v, d]} > {vehicle_capacity}")

    return solution



def check_subtour_elimination(n_vehicles, n_days, n_clients, routes_matrix, solution):
    # CONSTR 6: subtour elimination

    # delate zero rows and zero columns
    sub_routes_matrix = {
        (v, d): routes_matrix[v, d][np.ix_(
            np.any(routes_matrix[v, d] != 0, axis=1),
            np.any(routes_matrix[v, d] != 0, axis=0)
        )]
        for v in range(n_vehicles)
        for d in range(n_days)}

    # Raise each matrix to all powers from 1 to nodes (number of clients + depot) and then sum them.
    summed_powers_matrix = {}
    for (v, d), mat in sub_routes_matrix.items():
        nodes = mat.shape[0] 
        total = np.zeros_like(mat)
        
        power = np.identity(nodes, dtype=mat.dtype)
        
        for _ in range(1, nodes +1):
            power = power @ mat
            total += power

        summed_powers_matrix[(v, d)] = total

        # if each summed_powers_matrix is equal to a matrix of only 1
        if np.any(summed_powers_matrix[(v, d)] != 1):
            solution.feasibility_vector.constr_6 = False
            print(f"There is a sub-tour in the planned tour of vehicle {v} in the day {d}" )

    return solution



def update_output_vectors(solution):



    return solution



# FUNZIONI VETTORIZZATE
def define_routes_vectorized(n_vehicles, n_days, n_clients, max_clients_kd, assigned_ordered_matrix):
    
    routes_matrix = np.zeros((n_vehicles, n_days, n_clients, n_clients), dtype=int)

    # Prendiamo tutti i client_i (tranne l'ultimo per ogni giorno/veicolo)
    current_clients = assigned_ordered_matrix[:, :, :-1]  # Shape: (n_vehicles, n_days, max_clients_kd+1)
    next_clients = assigned_ordered_matrix[:, :, 1:]      # Shape: (n_vehicles, n_days, max_clients_kd+1)

    # Flatten per broadcasting diretto sugli indici della matrice routes_matrix
    v_idx, d_idx, c_idx = np.indices(current_clients.shape)

    # Imposta a 1 le rotte tra current_clients e next_clients
    routes_matrix[v_idx, d_idx, current_clients, next_clients] = 1

    # Imposta esplicitamente [0][0] = 0 per ogni veicolo/giorno (non necessario se già 0, ma per fedeltà al codice originale)
    routes_matrix[:, :, 0, 0] = 0

    return routes_matrix



