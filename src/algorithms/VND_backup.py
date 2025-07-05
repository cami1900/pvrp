import matplotlib.pyplot as plt
import numpy as np
import itertools 
import array as arr
import random
import copy
import algorithms.VND
import algorithms.assign_route
import algorithms.feasibility_function_POOP
import conf
import algorithms
import classes


''' VND ALGORITHM '''


def VND_algorithm(n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, data, sorted_data, distance_matrix, closeness_matrix, current_solution):

    neighbour = 0
    n_neighbour = 3
    # max_iteration_neigh = np.array([2, 2, 2, 2])
    max_iteration_neigh = np.array([20, 20, 20, 2])

    
    iteration = 0
    value_SEED = 0
    random.seed(value_SEED)

    clients_NO_max_frequ = filter_clients_NO_max_frequ(sorted_data, n_days, n_clients)


    while neighbour <= n_neighbour:

        if neighbour == 0:
            if iteration > max_iteration_neigh[neighbour]:
                iteration = 0
                neighbour += 1
                continue

            print(f"\n\nneighbour {neighbour} iteration {iteration}")
            value_SEED += 5
            # define new solution
            (initial_comb, final_comb, new_solution) = \
                k_move_t(
                    n_vehicles, n_days, vehicle_capacity, data, sorted_data, distance_matrix, closeness_matrix, current_solution, value_SEED, neighbour, clients_NO_max_frequ)
            initial_comb.print()
            final_comb.print()
            new_solution.print()

            # if the OBJ of new solution is better than the one of current solution: 
            if new_solution.OBJ_tot_dist <= current_solution.OBJ_tot_dist:
                # verify is new solution is feasible
                V_distances_matrix, V_loads_matrix, new_solution = \
                    algorithms.feasibility_function_POOP.check_feasibility_1vehicle(
                        n_vehicles, n_days, n_clients, data, max_clients_kd, vehicle_capacity, distance_matrix, new_solution)
                # if new solution is feasible:
                if new_solution.feasibility_vector.verify() == True:
                    current_solution = copy.copy(new_solution)  # udate current solution
                    current_solution.print()
                    iteration = 0
                iteration +=1
            else:
                iteration += 1
                continue

        if neighbour == 1:
            if iteration > max_iteration_neigh[neighbour]:
                iteration = 0
                # value_SEED = 0
                neighbour += 1
                continue

            print(f"\n\nneighbour {neighbour} iteration {iteration}")
            value_SEED += 5
            # define new solution
            (initial_comb, final_comb, new_solution) = \
                k_swap_t(
                    n_vehicles, n_days, vehicle_capacity, data, sorted_data, distance_matrix, closeness_matrix, current_solution, value_SEED, neighbour, clients_NO_max_frequ)
            initial_comb.print()
            final_comb.print()
            new_solution.print()

            # if the OBJ of new solution is better than the one of current solution: 
            if new_solution.OBJ_tot_dist <= current_solution.OBJ_tot_dist:
                # verify is new solution is feasible
                V_distances_matrix, V_loads_matrix, new_solution = \
                    algorithms.feasibility_function_POOP.check_feasibility_1vehicle(
                        n_vehicles, n_days, n_clients, data, max_clients_kd, vehicle_capacity, distance_matrix, new_solution)
                # if new solution is feasible:
                if new_solution.feasibility_vector.verify() == True:
                    current_solution = copy.copy(new_solution)  # udate current solution
                    current_solution.print()
                    iteration = 0
                    neighbour = 0
                iteration +=1
            else:
                iteration += 1
                continue
            
        if neighbour == 2:
            if iteration > max_iteration_neigh[neighbour]:
                iteration = 0
                neighbour += 1
                continue

            print(f"\n\nneighbour {neighbour} iteration {iteration}")
            value_SEED += 5
            # define new solution
            (initial_comb, final_comb, new_solution) = \
                move_kt(
                    n_vehicles, n_days, vehicle_capacity, data, sorted_data, distance_matrix, closeness_matrix, current_solution, value_SEED, neighbour, clients_NO_max_frequ)
            initial_comb.print()
            final_comb.print()
            new_solution.print()

            # if the OBJ of new solution is better than the one of current solution: 
            if new_solution.OBJ_tot_dist <= current_solution.OBJ_tot_dist:
                # verify is new solution is feasible
                V_distances_matrix, V_loads_matrix, new_solution = \
                    algorithms.feasibility_function_POOP.check_feasibility_1vehicle(
                        n_vehicles, n_days, n_clients, data, max_clients_kd, vehicle_capacity, distance_matrix, new_solution)
                # if new solution is feasible:
                if new_solution.feasibility_vector.verify() == True:
                    current_solution = copy.copy(new_solution)  # udate current solution
                    current_solution.print()
                    iteration = 0
                    neighbour = 0
                iteration +=1
            else:
                iteration += 1
                continue
            
        if neighbour == 3:
            if iteration > max_iteration_neigh[neighbour]:
                iteration = 0
                neighbour += 1
                continue

            print(f"\n\nneighbour {neighbour} iteration {iteration}")
            value_SEED += 5
            # define new solution
            (initial_comb, final_comb, new_solution) = \
                f_swap_kt(
                    n_vehicles, n_days, vehicle_capacity, data, sorted_data, distance_matrix, closeness_matrix, current_solution, value_SEED, neighbour, clients_NO_max_frequ)
            initial_comb.print()
            final_comb.print()
            new_solution.print()

            # if the OBJ of new solution is better than the one of current solution: 
            if new_solution.OBJ_tot_dist <= current_solution.OBJ_tot_dist:
                # verify is new solution is feasible
                V_distances_matrix, V_loads_matrix, new_solution = \
                    algorithms.feasibility_function_POOP.check_feasibility_1vehicle(
                        n_vehicles, n_days, n_clients, data, max_clients_kd, vehicle_capacity, distance_matrix, new_solution)
                # if new solution is feasible:
                if new_solution.feasibility_vector.verify() == True:
                    current_solution = copy.copy(new_solution)  # udate current solution
                    current_solution.print()
                    iteration = 0
                    neighbour = 0
                iteration +=1
            else:
                iteration += 1
                continue
        

    return current_solution



def VND_algorithm_PROVA(n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, data, sorted_data, distance_matrix, closeness_matrix, current_solution):

    neighbour = 0
    n_neighbour = 1
    iteration_n0 = 20
    iteration_n1 = 20
    
    iteration = 0
    value_SEED = 0
    random.seed(value_SEED)

    clients_NO_max_frequ = filter_clients_NO_max_frequ(sorted_data, n_days, n_clients)



    while neighbour <= n_neighbour:
        if neighbour == 0:
            if iteration > iteration_n0:
                iteration = 0
                # value_SEED = 0
                neighbour += 1
                continue

            # print("iteration", iteration)
            value_SEED += 5
            # define new solution
            (initial_comb, final_comb, new_solution) = \
                k_move_t(n_vehicles, n_days, vehicle_capacity, data, sorted_data, distance_matrix, closeness_matrix, current_solution, value_SEED, neighbour, clients_NO_max_frequ)

            # update current solution
            (current_solution, iteration) = \
                update_current_solution(n_vehicles, n_days, n_clients, data, max_clients_kd, vehicle_capacity, distance_matrix, current_solution, new_solution, iteration)
            

        if neighbour == 1:
            if iteration > iteration_n1:
                iteration = 0
                # value_SEED = 0
                neighbour += 1
                continue

            # for iteration in range(iteration_n1):
            # print("iteration", iteration)
            value_SEED += 5
            # print("value_SEED", value_SEED)
            # define new solution
            (initial_comb, final_comb, new_solution) = \
                k_swap_t(n_vehicles, n_days, vehicle_capacity, data, sorted_data, distance_matrix, closeness_matrix, current_solution, value_SEED, neighbour, clients_NO_max_frequ)
            
            # update current solution
            (current_solution, iteration) = \
                update_current_solution(n_vehicles, n_days, n_clients, data, max_clients_kd, vehicle_capacity, distance_matrix, current_solution, new_solution, iteration)
            



    return current_solution




''' NEIGHBORHOODS '''

def k_move_t(n_vehicles, n_days, vehicle_capacity, data, sorted_data, distance_matrix, closeness_matrix, current_solution, value_SEED, neighbour, clients_NO_max_frequ):

    # neighbour = 0

    # Inintial combination:
    initial_comb = def_initial_comb(neighbour, n_vehicles, n_days, data, sorted_data, current_solution, value_SEED, clients_NO_max_frequ)

    # Final combination: select new day excluding day_t1
    final_comb = def_final_comb(neighbour, n_vehicles, n_days, vehicle_capacity, data, current_solution, initial_comb, value_SEED)
    
    # New solution:
    new_solution = move_operation(n_vehicles, n_days, data, distance_matrix, closeness_matrix, current_solution, initial_comb, final_comb)


    # if np.all(final_comb.schedule) != 0:
    #     # The neighborhood operation is carried out
    #     new_solution = algorithms.VND.move_operation(n_vehicles, n_days, data, distance_matrix, closeness_matrix, current_solution, initial_comb, final_comb)
    # else: 
    #     new_solution = 0
    # # The neighborhood operation is carried out
    # new_solution = algorithms.VND.move_operation(n_vehicles, n_days, data, distance_matrix, closeness_matrix, current_solution, initial_comb, final_comb)

    return (initial_comb, final_comb, new_solution)



def k_swap_t(n_vehicles, n_days, vehicle_capacity, data, sorted_data, distance_matrix, closeness_matrix, current_solution, value_SEED, neighbour, clients_NO_max_frequ):

    # Combination 1 and 2 at the inital state:
    initial_comb = def_initial_comb(neighbour, n_vehicles, n_days, data, sorted_data, current_solution, value_SEED, clients_NO_max_frequ)
    initial_comb.print()
    
    # Combination 1 and 2 at the final state:
    final_comb = def_final_comb(neighbour, n_vehicles, n_days, vehicle_capacity, data, current_solution, initial_comb, value_SEED)

    # New solution:
    new_solution = swap_operation(n_vehicles, n_days, data, distance_matrix, closeness_matrix, current_solution, initial_comb, final_comb)

    return (initial_comb, final_comb, new_solution)



def move_kt(n_vehicles, n_days, vehicle_capacity, data, sorted_data, distance_matrix, closeness_matrix, current_solution, value_SEED, neighbour, clients_NO_max_frequ):

    # Inintial combination:
    initial_comb = def_initial_comb(neighbour, n_vehicles, n_days, data, sorted_data, current_solution, value_SEED, clients_NO_max_frequ)

    # Final combination: select new day excluding day_t1
    final_comb = def_final_comb(neighbour, n_vehicles, n_days, vehicle_capacity, data, current_solution, initial_comb, value_SEED)

    # New solution:
    new_solution = move_operation(n_vehicles, n_days, data, distance_matrix, closeness_matrix, current_solution, initial_comb, final_comb)

    return (initial_comb, final_comb, new_solution)



def f_swap_kt(n_vehicles, n_days, vehicle_capacity, data, sorted_data, distance_matrix, closeness_matrix, current_solution, value_SEED, neighbour, clients_NO_max_frequ):

    # Combination 1 and 2 at the inital state:
    initial_comb = def_initial_comb(neighbour, n_vehicles, n_days, data, sorted_data, current_solution, value_SEED, clients_NO_max_frequ)
    
    # Combination 1 and 2 at the final state:
    final_comb = def_final_comb(neighbour, n_vehicles, n_days, vehicle_capacity, data, current_solution, initial_comb, value_SEED)

    initial_comb.print()
    final_comb.print()

    # New solution:
    new_solution = swap_operation(n_vehicles, n_days, data, distance_matrix, closeness_matrix, current_solution, initial_comb, final_comb)

    return (initial_comb, final_comb, new_solution)


''' FUNCTIONS '''

def def_initial_comb(neighbour, n_vehicles, n_days, data, sorted_data, current_solution, value_SEED, clients_NO_max_frequ):

    # pick random vehicle, day, client and define its current schedule
    vehicle_i = random.randint(0, n_vehicles-1)
    day_i = random.randint(0, n_days-1)
    '''
    client_list = copy.copy(current_solution.assigned_ordered_matrix[vehicle_i, day_i])
    client_list = client_list[client_list != 0]
    client_list = np.intersect1d(client_list, filtred_clients)
    real_client_index = random.choice(client_list)
    '''
 
    real_client_index = pick_client(n_days, data, current_solution, vehicle_i, day_i, clients_NO_max_frequ, 0)
    print("real_client_index", real_client_index)

    schedule_i = define_initial_schedule(n_days, current_solution, vehicle_i, real_client_index)

    # NEIGHBOUR: 
    #
    # k_move_t 
    if neighbour == 0:
        initial_comb = classes.Move_combination('initial', vehicle_i, day_i, schedule_i, real_client_index)
        # return initial_comb
    #
    # k_swap_t
    if neighbour == 1:
        # Initial combination 1:
        initial_comb_1 = classes.Move_combination('initial_1', vehicle_i, day_i, schedule_i, real_client_index)

        # Initial combination 2:
        # pick a random day and client, and define its current schedule
        day_i2 = random.choice([i for i in range(n_days-1) if i != initial_comb_1.day])
        '''
        client_list = copy.copy(current_solution.assigned_ordered_matrix[vehicle_i, day_i2])
        where = np.where(client_list == initial_comb_1.client)[0]
        client_list[where] = 0
        client_list = client_list[client_list != 0]
        client_list = np.intersect1d(client_list, filtred_clients)
        real_client_index_2 = random.choice(client_list)
        '''
        
        real_client_index_2 = pick_client(n_days, data, current_solution, vehicle_i, day_i2, clients_NO_max_frequ, initial_comb_1.client)
        schedule_i2 = define_initial_schedule(n_days, current_solution, vehicle_i, real_client_index_2)

        initial_comb_2 = classes.Move_combination('initial_2', vehicle_i, day_i2, schedule_i2, real_client_index_2)

        # Initial combination (comb. 1 and comb.2):
        initial_comb = classes.SwapCombination('initial', initial_comb_1, initial_comb_2)
        # return initial_comb
    #
    # move_kt
    if neighbour == 2:
        initial_comb = classes.Move_combination('initial', vehicle_i, day_i, schedule_i, real_client_index)
        # return initial_comb
    #
    # f_swap_kt
    if neighbour == 3:
        # Initial combination 1:
        real_client_index = pick_client(n_days, data, current_solution, vehicle_i, day_i, 0, 0) # we are allowed to pick clients with freq = n_days
        schedule_i = define_initial_schedule(n_days, current_solution, vehicle_i, real_client_index)

        initial_comb_1 = classes.Move_combination('initial', vehicle_i, day_i, schedule_i, real_client_index)
        initial_comb_1.print()

        # Initial combination 2:
        # pick a random day and vehicle, search for a client with the same frequency and define its current schedule
        vehicle_i2 = random.choice([i for i in range(n_vehicles-1) if i != initial_comb_1.vehicle])
        day_i2 = random.randint(0, n_days-1)
        clients_same_freq = filter_clients_same_frequ(data, sorted_data, initial_comb_1)
        print("clients_same_freq", clients_same_freq)
        real_client_index_2 = pick_client(n_days, data, current_solution, vehicle_i2, day_i2, clients_same_freq, 0)
        schedule_i2 = define_initial_schedule(n_days, current_solution, vehicle_i2, real_client_index_2)

        initial_comb_2 = classes.Move_combination('initial_2', vehicle_i2, day_i2, schedule_i2, real_client_index_2)

        # Initial combination (comb. 1 and comb.2):
        initial_comb = classes.SwapCombination('initial', initial_comb_1, initial_comb_2)
        # return initial_comb

    return initial_comb



def def_final_comb(neighbour, n_vehicles, n_days, vehicle_capacity, data, current_solution, initial_comb, value_SEED):

    # NEIGHBOUR: 
    # 
    # k_move_t 
    if neighbour == 0:
        # pick new random day and define client's new schedule
        day_f = random.choice([t for t in range(0, n_days) if t != initial_comb.day])
        schedule_f = define_new_schedule_day(n_days, data, day_f, initial_comb.client, initial_comb.schedule)
        # Initial combination:
        final_comb = classes.Move_combination('final', initial_comb.vehicle, day_f, schedule_f, initial_comb.client)
        # return final_comb
    #
    # k_swap_t
    if neighbour == 1:
        # pick a random schedule for comb_1 and comb_2, based on the day of the other client
        schedule_f1 = define_new_schedule_day(n_days, data, initial_comb.comb_2.day, initial_comb.comb_1.client, initial_comb.comb_1.schedule)
        schedule_f2 = define_new_schedule_day(n_days, data, initial_comb.comb_1.day, initial_comb.comb_2.client, initial_comb.comb_2.schedule)
        # Final combination:
        final_comb_1 = classes.Move_combination('final_1', initial_comb.comb_1.vehicle, initial_comb.comb_2.day, schedule_f1, initial_comb.comb_1.client)
        final_comb_2 = classes.Move_combination('final_2', initial_comb.comb_2.vehicle, initial_comb.comb_1.day, schedule_f2, initial_comb.comb_2.client)
        final_comb = classes.SwapCombination('final', final_comb_1, final_comb_2)
        # return final_comb
    #
    # move_kt
    if neighbour == 2:
        # pick a random vehicle, define di available days and define client's new schedule
        vehicle_f = random.choice([k for k in range(0, n_vehicles) if k != initial_comb.vehicle])
        available_days = define_available_days(n_days, vehicle_capacity, data, vehicle_f, initial_comb, current_solution)
        schedule_f = define_new_schedule_load(n_days, data, available_days, initial_comb.client)
        final_comb = classes.Move_combination('final', vehicle_f, available_days, schedule_f, initial_comb.client)
    #
    # f_swap_kt
    if neighbour == 3:
        # invert vehicle and schedule (and day) of the two clients
        # Final combination:
        final_comb_1 = classes.Move_combination('final_1', initial_comb.comb_2.vehicle, initial_comb.comb_2.day, initial_comb.comb_2.schedule, initial_comb.comb_1.client)
        final_comb_2 = classes.Move_combination('final_2', initial_comb.comb_1.vehicle, initial_comb.comb_1.day, initial_comb.comb_1.schedule, initial_comb.comb_2.client)
        final_comb = classes.SwapCombination('final', final_comb_1, final_comb_2)
        # return final_comb
    

    return final_comb



def move_operation(n_vehicles, n_days, data, distance_matrix, closeness_matrix, current_solution, initial_comb, final_comb):

    # creation of new_Solution class attributes 
    '''
    new_assigned_ordered_matrix = copy.deepcopy(current_solution.assigned_ordered_matrix)    
    new_not_assigned_list = copy.deepcopy(current_solution.not_assigned_list)
    new_transp_demand_matrix = copy.deepcopy(current_solution.transp_demand_matrix)
    new_route_dist_matrix = copy.deepcopy(current_solution.route_dist_matrix)
    new_OBJ_tot_dist = 0
    '''
    (new_assigned_ordered_matrix, new_not_assigned_list, new_transp_demand_matrix, new_route_dist_matrix, new_OBJ_tot_dist) = crete_new_sol_attributes(current_solution)

    # Remove and add client to the Assigned customer matrix and the Transported demand matrix
    '''
    for day in range(n_days):

        if initial_comb.schedule[day] == 1:
            client_sequence = new_assigned_ordered_matrix[initial_comb.vehicle, day]
            idx = np.where(client_sequence == initial_comb.client)[0][0]    # Trova la posizione in cui compare il cliente da rimuovere
            client_sequence[idx:-1] = client_sequence[idx+1:] # move to left
            client_sequence[-1] = 0  # azzera l'ultimo

            new_transp_demand_matrix[initial_comb.vehicle, day] -= data[initial_comb.client, conf.DEMAND_INDEX]

        if final_comb.schedule[day] == 1:
            client_sequence = new_assigned_ordered_matrix[final_comb.vehicle, day]
            idx = np.where(client_sequence == 0)[0][1]  # Trova la posizione in cui compare il cliente da rimuovere
            client_sequence[idx] = final_comb.client    # inserisce il nuovo cliente

            new_transp_demand_matrix[final_comb.vehicle, day] += data[final_comb.client, conf.DEMAND_INDEX]
    '''
    (new_assigned_ordered_matrix, new_transp_demand_matrix) = remove_add_client(n_days, data, initial_comb, final_comb, new_assigned_ordered_matrix, new_transp_demand_matrix)

    # Reorganize the clients (best route) and update the Route distances matrix
    '''
    assign_matrix = np.zeros((n_vehicles, n_days), dtype=int)
    for day in range(n_days):    
        if initial_comb.schedule[day] == 1 or final_comb.schedule[day] == 1:
            assign_matrix[initial_comb.vehicle, day] = 1
            new_route_dist_matrix[initial_comb.vehicle, day] = 0
    (distances_matrix, new_assigned_ordered_matrix) = algorithms.assign_route.calculate_distances_CLOSNESS(n_vehicles, n_days, assign_matrix, new_assigned_ordered_matrix, distance_matrix, closeness_matrix)
    new_route_dist_matrix += distances_matrix
    '''
    new_route_dist_matrix = find_best_route(n_vehicles, n_days, distance_matrix, closeness_matrix, initial_comb, final_comb, new_route_dist_matrix, new_assigned_ordered_matrix)

    # Calculate the OBJECTIVE value
    new_OBJ_tot_dist = algorithms.assign_route.calculate_tot_dist (n_vehicles, n_days, new_route_dist_matrix, new_OBJ_tot_dist)

    # Save new solution:
    new_solution = classes.Solution(new_OBJ_tot_dist, new_assigned_ordered_matrix, new_not_assigned_list, new_transp_demand_matrix, new_route_dist_matrix)

    return new_solution



def swap_operation(n_vehicles, n_days, data, distance_matrix, closeness_matrix, current_solution, initial_comb, final_comb):

    # creation of new_Solution class attributes
    (new_assigned_ordered_matrix, new_not_assigned_list, new_transp_demand_matrix, new_route_dist_matrix, new_OBJ_tot_dist) = crete_new_sol_attributes(current_solution)

    # Remove and add client to the Assigned customer matrix and the Transported demand matrix
    (new_assigned_ordered_matrix, new_transp_demand_matrix) = remove_add_client(n_days, data, initial_comb.comb_1, final_comb.comb_1, new_assigned_ordered_matrix, new_transp_demand_matrix)
    (new_assigned_ordered_matrix, new_transp_demand_matrix) = remove_add_client(n_days, data, initial_comb.comb_2, final_comb.comb_2, new_assigned_ordered_matrix, new_transp_demand_matrix)

    # Reorganize the clients (best route) and update the Route distances matrix
    new_route_dist_matrix = find_best_route(n_vehicles, n_days, distance_matrix, closeness_matrix, initial_comb.comb_1, final_comb.comb_1, new_route_dist_matrix, new_assigned_ordered_matrix)
    new_route_dist_matrix = find_best_route(n_vehicles, n_days, distance_matrix, closeness_matrix, initial_comb.comb_2, final_comb.comb_2, new_route_dist_matrix, new_assigned_ordered_matrix)

    # Calculate the OBJECTIVE value
    new_OBJ_tot_dist = algorithms.assign_route.calculate_tot_dist (n_vehicles, n_days, new_route_dist_matrix, new_OBJ_tot_dist)

    # Save new solution:
    new_solution = classes.Solution(new_OBJ_tot_dist, new_assigned_ordered_matrix, new_not_assigned_list, new_transp_demand_matrix, new_route_dist_matrix)

    return new_solution



''' OTHER FUNCTIONS '''

def pick_client(n_days, data, current_solution, vehicle_i, day_i, clients_filtred, avoid_client):

    client_list = copy.copy(current_solution.assigned_ordered_matrix[vehicle_i, day_i])
    print(f"vehicle_i {vehicle_i}, day_i {day_i}")
    print("client_list", client_list)

    # avoid client:
    if avoid_client != 0:
        where = np.where(client_list == avoid_client)[0]
        client_list[where] = 0
        print("client_list", client_list)
    # remove zeros:
    client_list = client_list[client_list != 0]
    print("client_list", client_list)
    # filter clients by frequency (!= n_days) or all_clients (=0)
    if np.all(clients_filtred) != 0:
        client_list = np.intersect1d(client_list, clients_filtred)
        print("client_list", client_list)

    print("client_list", client_list)

    # choose a random client
    if np.size(client_list) == 0:
        print("\n\n____________________________empty__________________________\n\n")
        real_client_index = 0

    real_client_index = random.choice(client_list)
    
    return real_client_index


def filter_clients_NO_max_frequ(sorted_data, n_days, n_clients):

    max_freq = n_days
    # first_client = np.array[np.where((sorted_data[:, conf.FREQ_VISIT_INDEX] != max_freq) & (sorted_data[:, conf.FREQ_VISIT_INDEX] != 0))][0][0]
    first_client = [np.where((sorted_data[:, conf.FREQ_VISIT_INDEX] != max_freq) & (sorted_data[:, conf.FREQ_VISIT_INDEX] != 0))][0][0][0]
    # first_client = (sorted_data[:, conf.FREQ_VISIT_INDEX]).any((sorted_data[:, conf.FREQ_VISIT_INDEX] != max_freq) and (sorted_data[:, conf.FREQ_VISIT_INDEX] != 0))
    # print("\n\nfirst_client", first_client)
    clients_NO_max_frequ = np.zeros((n_clients-first_client), dtype=int)
    clients_NO_max_frequ = sorted_data[(first_client):, conf.CLIENT_ID_INDEX]
    clients_NO_max_frequ = [int(x) for x in clients_NO_max_frequ]

    return clients_NO_max_frequ


def filter_clients_same_frequ(data, sorted_data, initial_comb_1):

    freq_required = data[initial_comb_1.client, conf.FREQ_VISIT_INDEX]
    clients_sorted_ndex = [np.where((sorted_data[:, conf.FREQ_VISIT_INDEX] == freq_required) )][0][0]
    clients_same_freq = sorted_data[clients_sorted_ndex, conf.CLIENT_ID_INDEX]
    clients_same_freq = [int(x) for x in clients_same_freq]

    return clients_same_freq


def define_initial_schedule(n_days, current_solution, vehicle_i, real_client_index):

    schedule_i = np.zeros(n_days)
    days_si = np.where(current_solution.assigned_ordered_matrix[vehicle_i] == real_client_index)[0]
    for day in days_si:
        schedule_i[day] = 1

    return schedule_i


def define_new_schedule_day(n_days, data, desired_day, client, avoid_schedule):

    # transform day in binary
    bin_day = np.zeros(n_days)
    bin_day[desired_day] = 1
    # pick new random schedule (!= schedule_s1)
    n_visit_comb_i = int(data[client][conf.N_VISIT_INDEX])
    possible_schedules_i = np.zeros((n_visit_comb_i, n_days), dtype=int)
    
    for schedule in range(n_visit_comb_i):
        schedule_val = int(data[client][conf.VISIT_START_INDEX + schedule]) # schedule in decimal value
        schedule_s = np.array([int(b) for b in format(schedule_val, f'0{n_days}b')], dtype=int) # schedule in binary value
        if not np.array_equal(schedule_s, avoid_schedule): # Check that the schedule is not the current one
            check_day_t2 = np.add(schedule_s, bin_day)
            if np.any(check_day_t2[:] == 2): # Check day_t2 is in the schedule
                possible_schedules_i[schedule] = schedule_s
    # possible_schedules_i = [schedule for schedule in possible_schedules_i if np.any(schedule != 0)]   # NON SERVE, LO VERIFI ALLA RIGA DOPO
    if np.any(possible_schedules_i != 0 ):
        possible_schedules_i = [schedule for schedule in possible_schedules_i if np.any(schedule != 0)]
        # random.seed(value_SEED)
        new_schedule = random.choice(possible_schedules_i)
    else:
        new_schedule = np.zeros(n_days)

    return new_schedule


def crete_new_sol_attributes(current_solution):

    new_assigned_ordered_matrix = copy.deepcopy(current_solution.assigned_ordered_matrix)  
    new_not_assigned_list = copy.deepcopy(current_solution.not_assigned_list)
    new_transp_demand_matrix = copy.deepcopy(current_solution.transp_demand_matrix)
    new_route_dist_matrix = copy.deepcopy(current_solution.route_dist_matrix)
    new_OBJ_tot_dist = 0

    return (new_assigned_ordered_matrix, new_not_assigned_list, new_transp_demand_matrix, new_route_dist_matrix, new_OBJ_tot_dist)


def remove_add_client(n_days, data, initial_comb, final_comb, new_assigned_ordered_matrix, new_transp_demand_matrix):

    for day in range(n_days):

        if initial_comb.schedule[day] == 1:
            client_sequence = new_assigned_ordered_matrix[initial_comb.vehicle, day]
            idx = np.where(client_sequence == initial_comb.client)[0][0]    # Trova la posizione in cui compare il cliente da rimuovere
            client_sequence[idx:-1] = client_sequence[idx+1:] # move to left
            client_sequence[-1] = 0  # azzera l'ultimo

            new_transp_demand_matrix[initial_comb.vehicle, day] -= data[initial_comb.client, conf.DEMAND_INDEX]

        if final_comb.schedule[day] == 1:
            client_sequence = new_assigned_ordered_matrix[final_comb.vehicle, day]
            idx = np.where(client_sequence == 0)[0][1]  # Trova la posizione in cui compare il cliente da rimuovere
            client_sequence[idx] = final_comb.client    # inserisce il nuovo cliente

            new_transp_demand_matrix[final_comb.vehicle, day] += data[final_comb.client, conf.DEMAND_INDEX]

    return (new_assigned_ordered_matrix, new_transp_demand_matrix)


def find_best_route(n_vehicles, n_days, distance_matrix, closeness_matrix, initial_comb, final_comb, new_route_dist_matrix, new_assigned_ordered_matrix):

    assign_matrix = np.zeros((n_vehicles, n_days), dtype=int)
    for day in range(n_days):    
        if initial_comb.schedule[day] == 1 or final_comb.schedule[day] == 1:
            assign_matrix[initial_comb.vehicle, day] = 1
            new_route_dist_matrix[initial_comb.vehicle, day] = 0
    (distances_matrix, new_assigned_ordered_matrix) = algorithms.assign_route.calculate_distances_CLOSNESS(n_vehicles, n_days, assign_matrix, new_assigned_ordered_matrix, distance_matrix, closeness_matrix)
    new_route_dist_matrix += distances_matrix

    return new_route_dist_matrix


def update_current_solution(n_vehicles, n_days, n_clients, data, max_clients_kd, vehicle_capacity, distance_matrix, current_solution, new_solution, iteration):

    # if the OBJ of new solution is better than the one of current solution: 
    if new_solution.OBJ_tot_dist <= current_solution.OBJ_tot_dist:
        # verify is new solution is feasible
        V_distances_matrix, V_loads_matrix, new_solution = \
            algorithms.feasibility_function_POOP.check_feasibility_1vehicle(
                n_vehicles, n_days, n_clients, data, max_clients_kd, vehicle_capacity, distance_matrix, new_solution)
        # if new solution is feasible:
        if new_solution.feasibility_vector.verify() == True:
            current_solution = copy.copy(new_solution)  # udate current solution
            current_solution.print()
            iteration = 0
        iteration +=1
    
    else:
                iteration += 1
                # continue

    return (current_solution, iteration)


def define_available_days(n_days, vehicle_capacity, data, vehicle_f, initial_comb, current_solution):

    available_days = np.zeros(n_days, dtype=int)
    # available_days = arr.array([0]*n_days)
    # available_days.count
    for day in range(n_days):
        if (current_solution.transp_demand_matrix[vehicle_f, day] + data[initial_comb.client, conf.DEMAND_INDEX]) <= vehicle_capacity:
            available_days[day] = 1

    return available_days


def define_new_schedule_load(n_days, data, available_days, client):

    # pick new random schedule (!= schedule_s1)
    n_visit_comb_i = int(data[client][conf.N_VISIT_INDEX])
    possible_schedules_i = np.zeros((n_visit_comb_i, n_days), dtype=int)
    
    for schedule in range(n_visit_comb_i):
        schedule_val = int(data[client][conf.VISIT_START_INDEX + schedule])
        schedule_s = np.array([int(b) for b in format(schedule_val, f'0{n_days}b')], dtype=int)
        # schedule_s = arr.array([int(b) for b in format(schedule_val, f'0{n_days}b')], dtype=int)
        check_available_days = np.add(schedule_s, available_days)
        real_schedule_s_frequency = np.count_nonzero(check_available_days == 2)
        # check_available_days = arr.array(schedule_s + available_days)
        # real_schedule_s_frequency = check_available_days.count(2)
        if real_schedule_s_frequency == data[client][conf.FREQ_VISIT_INDEX]:
            possible_schedules_i[schedule] = schedule_s
    
    if np.any(possible_schedules_i != 0 ):
        possible_schedules_i = [schedule for schedule in possible_schedules_i if np.any(schedule != 0)]
        # random.seed(value_SEED)
        new_schedule = random.choice(possible_schedules_i)
    else:
        new_schedule = np.zeros(n_days)

    return new_schedule

