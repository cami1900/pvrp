import numpy as np
import matplotlib.pyplot as plt
import itertools
import random
import random2
import copy
import time

import algorithms
import algorithms.VND as vnd_alg
import algorithms.assign_route as initial_sol_alg
import algorithms.feasibility_function_POOP as feasibility_alg
import utils




def main():

    ''' USER INTERFACE -------------------------------------------------------------------------------------------------------'''
    
    file_path = "data/p02.txt"     # type name of file, ex: p02.txt
    distance_type = 1       # select: Euclidean = 1, Manhattan = 2

    filename = "out/results/vrp_tests/p12_1_999_3600.xlsx"
    imgname = "out/results/vrp_tests/p12_1_999_3600.png"

    # VND parameters
    repetitions_VND = [1, 0]
    time_limit_VND = 3600   # 2h*60min*60sec = 7200sec
    time_limit_neigh = 7200  # not used

    # neigh_order = ["k_move_t", "k_swap_t", "move_kt", "f_swap_kt", "swap_kt"]
    # neigh_order = ["move_kt", "f_swap_kt"]
    neigh_order = ["t_swap_k"]
    neigh_order = ["move_kt", "t_swap_k", "f_swap_kt"]
    # initial_neigh_VND = [0, worse_sol_neigh, worse_sol_neigh]
    max_neighbour = (len(neigh_order) - 1)
    max_iteration_neigh = 500

    two_opt_iteration = 500    

    tot_rep_VND = (repetitions_VND[0] + repetitions_VND[1])
    worse_sol_acc_VND = np.empty(tot_rep_VND, dtype=bool)
    for rep in range(repetitions_VND[0]):
        worse_sol_acc_VND[rep] = False
    for rep in range(repetitions_VND[1]):
        worse_sol_acc_VND[rep + repetitions_VND[0]] = True
    # print(worse_sol_acc_VND)
    # worse_sol_acc_VND = [False, True, True, True, True, True, True, True, True, True]     # insert True if worse solution is accepted, False otherwise
    worse_sol_neigh = 1
    worse_sol_percentage = 0.15

    
    '''-----------------------------------------------------------------------------------------------------------------------'''
    
    seed = 42 
    random.seed(seed)
    np.random.seed(seed)
    random2.seed(seed)

    
    # start_time = time.process_time()

    '''DATA PREPARATION'''
    distance_type = 1
    (n_vehicles, n_days, vehicle_capacity, data, sorted_data, n_clients, max_clients_kd, distance_matrix, distance_matrix_adjusted, closeness_matrix) = \
        utils.data_preparation(file_path, distance_type)
    
    '''INITIAL SOLUTION'''
    solution_0 = initial_sol_alg.assign_to_1_vehicle_algorithm(
        n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, sorted_data, distance_matrix, distance_matrix_adjusted, closeness_matrix
    )
    # check fesibility
    V_distances_matrix, V_loads_matrix, solution_0 = feasibility_alg.check_feasibility_pvrp(
        n_vehicles, n_days, n_clients, data, max_clients_kd, vehicle_capacity, distance_matrix, 
        solution_0)    
    if np.any(solution_0.feasibility_vector) != 1 or np.any(solution_0.verification_vector) != 1:
        return f"Instance p02 - Soluzione iniziale non fattibile.\n"
    
    # print("\nINITIAL SOLUTION --------------------------------------")
    # solution_0.print()

    '''VND ALGORITHM'''
    initial_neighbour = 0
    current_solution = copy.deepcopy(solution_0)
    worse_sol_acceptance = False

    (vnd_solution_1, new_sol_per_neigh, number_iterations_vector, time_vector) = vnd_alg.VND_algorithm_condensed2_pvrp(
        n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, data, sorted_data, distance_matrix, distance_matrix_adjusted, closeness_matrix, 
        current_solution, 
        time_limit_VND, time_limit_neigh,
        neigh_order, initial_neighbour, max_neighbour, max_iteration_neigh, 
        two_opt_iteration, 
        worse_sol_acceptance)
    

    print("\nINITIAL SOLUTION --------------------------------------")
    print(solution_0.OBJ_tot_dist)

    print("\nBEST SOLUTION -----------------------------------------")
    print(vnd_solution_1.OBJ_tot_dist)
    vnd_solution_1.print()

    # ''' PLOTS '''
    # utils.plot_euclidean_vehicles_routes(n_vehicles, n_days, data, vnd_solution_1.assigned_ordered_matrix)
    # plt.show()

if __name__ == "__main__":
    main()
