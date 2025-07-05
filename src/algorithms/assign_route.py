import matplotlib.pyplot as plt
import numpy as np
import itertools 
import random
import copy
import conf
import classes
from py2opt.routefinder import RouteFinder




def assign_to_1_vehicle_algorithm(n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, sorted_data, distance_matrix, distance_matrix_adjusted, closeness_matrix):
    """
    Assigns customers to vehicles daily routes by searching the optimal set of routes 
        for a fleet of vehicles that must collect the garbage from a set of customers. 

    Args:
        - sorted_data (matrix): A sorted customers' data matrix.
        - distance_matrix (matrix): A Manhattan distances matrix between customers, depot included.

    Returns:
        - Assigned customers matrix: contains the assigned customers lists
        - Transported demand matrix: 
        - Route distances matrix
        - Not assigned customers list: a list of all the customers the have not been assigned.

    Notes:
        - data --> real_client_index  VS  sorted_data --> sor_client_i
        - distance_matrix is based on real_client_index
        - S_assigned_cust_matrix is based on real_client_index
        - assigned_ordered_matrix, not_assigned_list are based on real_client_index
    """

    # print("\n\nStarting algorithmm...")

    # Create output solution
    (OBJ_tot_dist, assigned_ordered_matrix, not_assigned_list, transp_demand_matrix, route_dist_matrix) = output_matrices(n_vehicles, n_days, n_clients, max_clients_kd)

    # Suppose (S) to add client i to each vehicle in every day of the period, then:
    # - verify if its a feasible solution (capacity contraint and schedules contraint) 
    # - calculate distances of the routes
    # - assign client to the solution that minimizes the total distance

    for sor_client_i in range(1, len(sorted_data)):  # skip the depot --> len(sorted_data)

        # STEP 1: add client i
        (real_client_index, S_assigned_cust_matrix) = assign_client(sor_client_i, n_vehicles, n_days, sorted_data, assigned_ordered_matrix)

        # STEP 2: update vehicle load
        (demand_i, S_loads_matrix) = load_vehicle(sor_client_i, n_vehicles, n_days, sorted_data, transp_demand_matrix)

        # STEP 3: vehicle capacity constraint
        (S_poss_assign_matrix) = check_capacity(n_vehicles, n_days, vehicle_capacity, S_loads_matrix)

        # STEP 4: define the possible schedules
        (S_visit_comb_matrix) = define_schedules(sor_client_i, n_days, sorted_data)
        
        # STEP 5: impose schedules --> check feasibility (frequency constraint)
        (min_freq_i, S_fesibility_matrix) = impose_schedules (sor_client_i, sorted_data, S_poss_assign_matrix, S_visit_comb_matrix)

        if not np.any(S_fesibility_matrix >= min_freq_i):   # if min_freq_i is not satisfied
            # not_assigned_list.append(real_client_index)     # add client i to not_assigned_list
            first_zero = np.where(not_assigned_list == 0)[0]
            not_assigned_list[first_zero] = real_client_index
            continue
            
        # STEP 6: update matrices
        (S_fesibility_matrix, S_visit_comb_matrix, S_poss_assign_matrix) = update_matrices(min_freq_i, S_fesibility_matrix, S_visit_comb_matrix, S_poss_assign_matrix)
        (S_fesibility_matrix) = update_feasibility(min_freq_i, S_fesibility_matrix)

        # STEP 7: calculate distances
        ''' hai sostituito la distance_matrix con la distance_matrix_adjusted'''
        # (S_distances_matrix, S_assigned_cust_matrix) = calculate_distances_PERMUTATION(n_vehicles, n_days, S_poss_assign_matrix, S_assigned_cust_matrix, distance_matrix)
        (S_distances_matrix, S_assigned_cust_matrix) = calculate_distances_CLOSNESS_line_route(n_vehicles, n_days, S_poss_assign_matrix,  S_assigned_cust_matrix, distance_matrix_adjusted, closeness_matrix)

        # STEP 8: calculate the Schedule distances matrix 
        (S_sched_dist_matrix) = calculate_sched_dist(S_distances_matrix, S_visit_comb_matrix, S_fesibility_matrix)

        # STEP 9: find the combination with minimum distance
        (winning_vehicle, winning_schedule) = find_winning_comb(S_sched_dist_matrix)

        # STEP 10: update output matrices
        (assigned_ordered_matrix, transp_demand_matrix, route_dist_matrix) = update_out_matrices(n_vehicles, n_days, winning_vehicle, winning_schedule, 
                                                                                                    assigned_ordered_matrix, transp_demand_matrix, route_dist_matrix, 
                                                                                                    S_visit_comb_matrix, S_assigned_cust_matrix, S_loads_matrix, S_distances_matrix)

    # STEP 11:
    (assigned_ordered_matrix) = add_depot(n_vehicles, n_days, assigned_ordered_matrix)
    # 2-opt:
    ''' hai sostituito la distance_matrix con la distance_matrix_adjusted'''
    (assigned_ordered_matrix, route_dist_matrix) = two_opt_route(n_vehicles, n_days, distance_matrix, distance_matrix_adjusted, route_dist_matrix, assigned_ordered_matrix)
    
    # STEP 12: calculate the total distance traveled (OBJECTIVE FUNCTION)
    (OBJ_tot_dist) = calculate_tot_dist(n_vehicles, n_days, route_dist_matrix, OBJ_tot_dist)

    solution_0 = classes.Solution(OBJ_tot_dist, assigned_ordered_matrix, not_assigned_list, transp_demand_matrix, route_dist_matrix)
    # solution_0.print()

    return solution_0


''' STEPS FUNCTIONS '''

def output_matrices(n_vehicles, n_days, n_clients, max_clients_kd):
    
    # Crate OBJECTIVE VALUE:
    OBJ_tot_dist = 0
    # Create a zero Assigned customers matrix 
    # assigned_ordered_matrix = [[[] for _ in range(n_days)] for _ in range(n_vehicles)] 
    assigned_ordered_matrix = np.zeros((n_vehicles, n_days, max_clients_kd+2), dtype=int)
    # Create a Not assigned customers list
    not_assigned_list = np.zeros(n_clients)
    # Create a zero Transported demand matrix
    transp_demand_matrix = np.zeros((n_vehicles, n_days), dtype=int)
    # Create a zero Route distances matrix
    route_dist_matrix = np.zeros((n_vehicles, n_days), dtype=float)

    return (OBJ_tot_dist, assigned_ordered_matrix, not_assigned_list, transp_demand_matrix, route_dist_matrix)


def assign_client (sor_client_i, n_vehicles, n_days, sorted_data, assigned_ordered_matrix):

    real_client_index = int(sorted_data[sor_client_i][conf.CLIENT_ID_INDEX])
    S_assigned_cust_matrix = copy.deepcopy(assigned_ordered_matrix)

    for vehicle_k in range(n_vehicles):
        for day_t in range(n_days):
            # S_assigned_cust_matrix[vehicle_k][day_t].append(real_client_index)
            # S_assigned_cust_matrix[vehicle_k][day_t] = S_assigned_cust_matrix[vehicle_k][day_t] + [real_client_index]
            first_zero = np.where(S_assigned_cust_matrix[vehicle_k][day_t] == 0)[0]
            S_assigned_cust_matrix[vehicle_k, day_t, first_zero[0]] = real_client_index

    return(real_client_index, S_assigned_cust_matrix)


def load_vehicle (sor_client_i, n_vehicles, n_days, sorted_data, transp_demand_matrix):

    demand_i = int(sorted_data[sor_client_i][conf.DEMAND_INDEX])
    S_loads_matrix = copy.deepcopy(transp_demand_matrix)

    for vehicle_k in range(n_vehicles):
        for day_t in range(n_days):
            S_loads_matrix[vehicle_k][day_t] += demand_i

    return(demand_i, S_loads_matrix)


def check_capacity (n_vehicles, n_days, vehicle_capacity, S_loads_matrix):

    S_poss_assign_matrix =  S_loads_matrix - vehicle_capacity 

    for vehicle_k in range(n_vehicles):
        for day_t in range(n_days):
            if S_poss_assign_matrix[vehicle_k][day_t] <= 0:
                S_poss_assign_matrix[vehicle_k][day_t] = 1
            else: 
                S_poss_assign_matrix[vehicle_k][day_t] = 0

    return (S_poss_assign_matrix)


def define_schedules (sor_client_i, n_days, sorted_data):
    # print("sor_client_i", sor_client_i)
    n_visit_comb_i = int(sorted_data[sor_client_i][conf.N_VISIT_INDEX])
    S_visit_comb_matrix = np.zeros((n_days, n_visit_comb_i), dtype=int)

    for schedule in range(n_visit_comb_i):
        binary_str = format(int(sorted_data[sor_client_i][conf.VISIT_START_INDEX + schedule]), f'0{n_days}b')
        binary_list = [int(bit) for bit in binary_str]

        for day_t in range(n_days):
            S_visit_comb_matrix[day_t][schedule] = binary_list[day_t]

    return(S_visit_comb_matrix)


def impose_schedules (sor_client_i, sorted_data, S_poss_assign_matrix, S_visit_comb_matrix):

    min_freq_i = int(sorted_data[sor_client_i][conf.FREQ_VISIT_INDEX])
    S_fesibility_matrix = np.dot(S_poss_assign_matrix, S_visit_comb_matrix)

    return(min_freq_i, S_fesibility_matrix)


def update_matrices (min_freq_i, S_fesibility_matrix, S_visit_comb_matrix, S_poss_assign_matrix):

    for schedule_s in range(S_fesibility_matrix.shape[1]):  # Loop through all the indexes of the columns of the matrix
        if not np.any(S_fesibility_matrix[:, schedule_s] == min_freq_i):    # if there is no element equal to min_freq_i
            # S_fesibility_matrix[:, schedule_s] = 0
            S_visit_comb_matrix[:, schedule_s] = 0  

    for vehicle_v in range(S_fesibility_matrix.shape[0]):   # Loop through all the indexes of the rows of the matrix
        if not np.any(S_fesibility_matrix[vehicle_v, :] == min_freq_i):     # if there is no element equal to min_freq_i
            # S_fesibility_matrix[vehicle_v, :] = 0
            S_poss_assign_matrix[vehicle_v, :] = 0 

    for day_t in range(S_visit_comb_matrix.shape[0]):  
        if not np.any(S_visit_comb_matrix[day_t, :] == 1):
            S_poss_assign_matrix[:, day_t] = 0

    return(S_fesibility_matrix, S_visit_comb_matrix, S_poss_assign_matrix)


def update_feasibility (min_freq_i, S_fesibility_matrix):

    for schedule_s in range(S_fesibility_matrix.shape[1]):
        for vehicle_v in range(S_fesibility_matrix.shape[0]):
            if S_fesibility_matrix[vehicle_v][schedule_s] < min_freq_i:
                S_fesibility_matrix[vehicle_v][schedule_s] = 0

    return(S_fesibility_matrix)


def calculate_distances_PERMUTATION (n_vehicles, n_days, S_poss_assign_matrix, S_assigned_cust_matrix, distance_matrix):

    S_distances_matrix = np.zeros((n_vehicles, n_days), dtype=float)

    for vehicle_k in range(n_vehicles):
        for day_t in range(n_days):
            if S_poss_assign_matrix[vehicle_k][day_t] != 0:
                # hai aggiunto [:]
                client_list = S_assigned_cust_matrix[vehicle_k][day_t][:]  # this list is based on real_client_index
                client_list = client_list[client_list != 0]

                min_distance = float('inf')
                best_route = []

                for perm in itertools.permutations(client_list):
                    route = [0] + list(perm) + [0]
                    distance = sum(distance_matrix[route[i]][route[i+1]] for i in range(len(route)-1))

                    if distance < min_distance:
                        min_distance = distance
                        # best_route = route
                        best_route = [client for client in route if client != 0]
            
                        S_distances_matrix[vehicle_k][day_t] = min_distance
                        # S_assigned_cust_matrix[vehicle_k][day_t] =  best_route   
                        # first_zero = np.where(S_assigned_cust_matrix[vehicle_k][day_t] == 0)[0]
                        # S_assigned_cust_matrix[vehicle_k, day_t, first_zero[0]] = best_route
                        S_assigned_cust_matrix[vehicle_k, day_t, :len(best_route)] = best_route


    return(S_distances_matrix, S_assigned_cust_matrix)

'''
def calculate_distances_CLOSNESS(n_vehicles, n_days, S_poss_assign_matrix,  S_assigned_cust_matrix, distance_matrix, closeness_matrix):

    S_distances_matrix = np.zeros((n_vehicles, n_days), dtype=int)

    for vehicle_k in range(n_vehicles):
        for day_t in range(n_days):
            if S_poss_assign_matrix[vehicle_k][day_t] != 0:
                # hai aggiunto [:]
                client_list = S_assigned_cust_matrix[vehicle_k][day_t][:]  # this list is based on real_client_index
                client_list = client_list[client_list != 0]
                client_list = list(client_list)

                route = [0] * (len(client_list))
                # first client:
                route[0] = next(c for c in closeness_matrix[0] if c in client_list)
                client_list.remove(route[0])
                # last client:
                if route[-1] == 0:
                    route[-1] = next((c for c in closeness_matrix[0] if c in client_list), 0)
                    client_list.remove(route[-1])
                # client_list.remove(route[-1])

                if len(client_list) != 0:
                    first_client = 1
                    last_client = (len(route)-2)
                    while client_list:
                        # add to the first available spot:
                        client_before = route[first_client-1]
                        route[first_client] = next(c for c in closeness_matrix[client_before] if c in client_list)
                        client_list.remove(route[first_client])
                        first_client += 1

                        if not client_list:
                            break
                        
                        # add to the last available spot:
                        client_after = route[last_client+1]
                        route[last_client] = next(c for c in closeness_matrix[client_after] if c in client_list)
                        client_list.remove(route[last_client])
                        last_client -=1

            # calculate route distance:
            route_distance = float('inf')
            # for i in range(len(route) - 1):
            #     from_node = route[i]
            #     to_node = route[i + 1]
            #     route_distance += distance_matrix[from_node, to_node]
            route = np.array(route, dtype=int)
            tot_route = [0] + list(route) + [0]
            route_distance = sum(distance_matrix[tot_route[i]][tot_route[i+1]] for i in range(len(tot_route)-1))
            S_distances_matrix[vehicle_k][day_t] = route_distance
            S_assigned_cust_matrix[vehicle_k, day_t, :len(route)] = route

            # S_distances_matrix[vehicle_k][day_t] = 0         

            print("hello")

    return(S_distances_matrix, S_assigned_cust_matrix)
'''

def calculate_distances_CLOSNESS_circle_route(n_vehicles, n_days, S_poss_assign_matrix, S_assigned_cust_matrix, distance_matrix, closeness_matrix):
    S_distances_matrix = np.zeros((n_vehicles, n_days), dtype=float)

    for vehicle_k in range(n_vehicles):
        for day_t in range(n_days):

            if S_poss_assign_matrix[vehicle_k][day_t] == 0:
                continue  # Nessun cliente da assegnare

            # Estrai i clienti assegnati, rimuovi zeri e converti in lista
            client_list = S_assigned_cust_matrix[vehicle_k][day_t]
            client_list = client_list[client_list != 0].astype(int).tolist()

            if len(client_list) == 0:
                continue  # Nessun cliente utile

            route = [0] * len(client_list)

            # Primo cliente: più vicino al deposito (nodo 0)
            first = next((c for c in closeness_matrix[0] if c in client_list), None)
            if first is None:
                continue
            route[0] = first
            client_list.remove(first)

            # Ultimo cliente: secondo più vicino al deposito
            if len(client_list) > 0:
                last = next((c for c in closeness_matrix[0] if c in client_list), None)
                if last is not None:
                    route[-1] = last
                    client_list.remove(last)

            # Inserisci i restanti clienti greedy, dal centro verso i lati
            first_client = 1
            last_client = len(route) - 2

            while client_list:
                # Inserimento a sinistra
                if first_client <= last_client:
                    prev = int(route[first_client - 1])
                    next_left = next((c for c in closeness_matrix[prev] if c in client_list), None)
                    if next_left is not None:
                        route[first_client] = next_left
                        client_list.remove(next_left)
                        first_client += 1
                    else:
                        break  # Nessun cliente vicino trovato

                # Inserimento a destra
                if client_list and first_client <= last_client:
                    after = int(route[last_client + 1])
                    next_right = next((c for c in closeness_matrix[after] if c in client_list), None)
                    if next_right is not None:
                        route[last_client] = next_right
                        client_list.remove(next_right)
                        last_client -= 1
                    else:
                        break

            # Chiudi il percorso aggiungendo il deposito all'inizio e alla fine
            route = [0] + [int(r) for r in route if r != 0] + [0]

            # Calcolo distanza totale del percorso
            try:
                route_distance = sum(distance_matrix[route[i], route[i + 1]] for i in range(len(route) - 1))
            except IndexError as e:
                print(f"❌ Errore nell'accesso alla distance_matrix: {e}")
                route_distance = 999999

            S_distances_matrix[vehicle_k, day_t] = route_distance

            # Salva il percorso nel tensor 3D
            S_assigned_cust_matrix[vehicle_k, day_t, :len(route)] = route

            # print(f"✔️ Veicolo {vehicle_k}, Giorno {day_t}, Percorso: {route}, Distanza: {route_distance}")

    return S_distances_matrix, S_assigned_cust_matrix

def calculate_distances_CLOSNESS_line_route(n_vehicles, n_days, S_poss_assign_matrix, S_assigned_cust_matrix, distance_matrix, closeness_matrix):
    S_distances_matrix = np.zeros((n_vehicles, n_days), dtype=float)

    for vehicle_k in range(n_vehicles):
        for day_t in range(n_days):

            if S_poss_assign_matrix[vehicle_k][day_t] == 0:
                continue  # Nessun cliente da assegnare

            # Estrai i clienti assegnati, rimuovi zeri e converti in lista
            client_list = S_assigned_cust_matrix[vehicle_k][day_t]
            client_list = client_list[client_list != 0].astype(int).tolist()

            if len(client_list) == 0:
                continue  # Nessun cliente utile

            route = [0] * len(client_list)

            # Primo cliente: più vicino al deposito (nodo 0)
            first = next((c for c in closeness_matrix[0] if c in client_list), None)
            if first is None:
                continue
            route[0] = first
            client_list.remove(first)

            # Inserisci i restanti clienti greedy
            idx = 1

            while client_list:
                # Inserimento 
                prev_cl = int(route[idx - 1])
                next_cl = next((c for c in closeness_matrix[prev_cl] if c in client_list), None)
                if next_cl is not None:
                    route[idx] = next_cl
                    client_list.remove(next_cl)
                    idx += 1
                else:
                    break  # Nessun cliente vicino trovato

            # Chiudi il percorso aggiungendo il deposito all'inizio e alla fine
            route = [0] + [int(r) for r in route if r != 0] + [0]

            # Calcolo distanza totale del percorso
            try:
                route_distance = sum(distance_matrix[route[i], route[i + 1]] for i in range(len(route) - 1))
            except IndexError as e:
                print(f"❌ Errore nell'accesso alla distance_matrix: {e}")
                route_distance = 999999

            S_distances_matrix[vehicle_k, day_t] = route_distance

            # Salva il percorso nel tensor 3D
            S_assigned_cust_matrix[vehicle_k, day_t, :len(route)] = route

            # print(f"✔️ Veicolo {vehicle_k}, Giorno {day_t}, Percorso: {route}, Distanza: {route_distance}")

    return S_distances_matrix, S_assigned_cust_matrix


def calculate_sched_dist (S_distances_matrix, S_visit_comb_matrix, S_fesibility_matrix):

    S_sched_dist_matrix = np.dot(S_distances_matrix, S_visit_comb_matrix)
    for schedule_s in range(S_fesibility_matrix.shape[1]):
        for vehicle_v in range(S_fesibility_matrix.shape[0]):
            if S_fesibility_matrix[vehicle_v][schedule_s] == 0:
                S_sched_dist_matrix[vehicle_v][schedule_s] = 0

    return(S_sched_dist_matrix)


def find_winning_comb_TEST (S_sched_dist_matrix):

    if np.all(S_sched_dist_matrix) == 0:
        winning_vehicle = random.randint(0, (len(S_sched_dist_matrix)-1))
        winning_schedule = random.randint(0, (len(S_sched_dist_matrix[0])-1))

    else:
        min_dist_comb = np.min(S_sched_dist_matrix[np.nonzero(S_sched_dist_matrix)])    # find the value min_dist_comb (avoid 0)
        row_column = np.where(S_sched_dist_matrix == min_dist_comb)     # identify row and column of combinations with sched_dist == min_dist_comb
        preferable_comb = list(zip(row_column[0], row_column[1]))       # save indices of the combinations with sched_dist == min_dist_comb

        random.seed(1234)
        winning_comb = np.array([list(random.choice(preferable_comb))])     # decide with a seed which combination is the winning one
        # winning_comb = np.array([list(random.choice(preferable_comb))])   # decide randomly which combination is the winning one

        winning_vehicle = winning_comb[0][0]
        winning_schedule = winning_comb[0][1]

    return(winning_vehicle, winning_schedule)


def find_winning_comb (S_sched_dist_matrix):

    
    min_dist_comb = np.min(S_sched_dist_matrix[np.nonzero(S_sched_dist_matrix)])    # find the value min_dist_comb (avoid 0)
    row_column = np.where(S_sched_dist_matrix == min_dist_comb)     # identify row and column of combinations with sched_dist == min_dist_comb
    preferable_comb = list(zip(row_column[0], row_column[1]))       # save indices of the combinations with sched_dist == min_dist_comb

    random.seed(1234)
    winning_comb = np.array([list(random.choice(preferable_comb))])     # decide with a seed which combination is the winning one
    # winning_comb = np.array([list(random.choice(preferable_comb))])   # decide randomly which combination is the winning one

    winning_vehicle = winning_comb[0][0]
    winning_schedule = winning_comb[0][1]

    return(winning_vehicle, winning_schedule)


def update_out_matrices (n_vehicles, n_days, winning_vehicle, winning_schedule, 
                         assigned_ordered_matrix, transp_demand_matrix, route_dist_matrix, 
                         S_visit_comb_matrix, S_assigned_cust_matrix, S_loads_matrix, S_distances_matrix):

    for vehicle_k in range(n_vehicles):
        for day_t in range(n_days):
            if vehicle_k == winning_vehicle and S_visit_comb_matrix[day_t][winning_schedule] == 1:

                assigned_ordered_matrix[vehicle_k][day_t] = S_assigned_cust_matrix[vehicle_k][day_t]
                transp_demand_matrix [vehicle_k][day_t] = S_loads_matrix[vehicle_k][day_t]
                route_dist_matrix[vehicle_k][day_t] = S_distances_matrix[vehicle_k][day_t]

    return(assigned_ordered_matrix, transp_demand_matrix, route_dist_matrix)


def add_depot(n_vehicles, n_days, assigned_ordered_matrix):

    for vehicle_k in range(n_vehicles):
        for day_t in range(n_days):
            # assigned_ordered_matrix[vehicle_k][day_t] = [0] + (assigned_ordered_matrix[vehicle_k][day_t] - [0])
            route = assigned_ordered_matrix[vehicle_k][day_t]
            # Filtra solo i valori non zero
            route_clean = route[route != 0]
            # Aggiungi 0 all'inizio e alla fine
            new_route = np.concatenate(([0], route_clean, [0]))
            # Sovrascrivi solo i primi elementi (occhio a non uscire dai limiti)
            assigned_ordered_matrix[vehicle_k, day_t, :len(new_route)] = new_route

    return(assigned_ordered_matrix)


def calculate_tot_dist (n_vehicles, n_days, route_dist_matrix, OBJ_tot_dist):

    for vehicle_k in range(n_vehicles):
        for day_t in range(n_days):
            OBJ_tot_dist += route_dist_matrix[vehicle_k][day_t]

    return(OBJ_tot_dist)


def two_opt_route(n_vehicles, n_days, distance_matrix, distance_matrix_adjusted, route_dist_matrix, assigned_ordered_matrix):

    for vehicle_k in range(n_vehicles):
        for day_t in range(n_days):
            all_clients = copy.copy(assigned_ordered_matrix[vehicle_k, day_t])
            number_clients = len((np.nonzero(all_clients))[0])
            route_clients = all_clients[0: (number_clients+2)]
            route_clients_str = list(str(int(x)) for x in route_clients)

            distance_matrix_route = np.zeros((len(route_clients)-1, len(route_clients)-1), dtype=float)
            for i in range(len(route_clients)-1):
                for j in range(len(route_clients)-1):
                    distance_matrix_route[i, j] = distance_matrix_adjusted[route_clients[i], route_clients[j]]

            new_routes = RouteFinder(distance_matrix_route, route_clients_str, iterations=10)
            best_distance, best_route = new_routes.solve()
            nt_array = np.array(best_route, dtype=int)
            # return to the original distance_matrix:
            route_distance = sum(distance_matrix[nt_array[i], nt_array[i + 1]] for i in range(len(nt_array) - 1))

            assigned_ordered_matrix[vehicle_k, day_t][0:(number_clients+2)] = nt_array
            route_dist_matrix[vehicle_k, day_t] = route_distance

    return (assigned_ordered_matrix, route_dist_matrix)



''' OTHER FUNCTIONS '''


