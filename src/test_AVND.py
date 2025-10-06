import numpy as np
import matplotlib.pyplot as plt
import itertools
import random
import random2
import copy
import time
import pandas as pd

import algorithms
from algorithms.AVND import AVND_algorithm
import algorithms.VND as vnd_alg
import algorithms.assign_route as initial_sol_alg
import algorithms.feasibility_function_POOP as feasibility_alg
import utils

def main():

    ''' USER INTERFACE -------------------------------------------------------------------------------------------------------'''
    
    file_path = "data/p02.txt"     # type name of file, ex: p02.txt
    distance_type = 1       # select: Euclidean = 1, Manhattan = 2

    out_file_path = "out/results/pvrp_tests/p02_1800_20_200.xlsx"

    # VND parameters
    time_limit_VND = 1800   # 30min*60sec = 1800sec

    # neigh_order = ["k_move_t", "k_swap_t", "move_kt", "f_swap_kt", "swap_kt", "t_swap_k"]
    neigh_order = ["move_kt", "t_swap_k", "swap_kt", "f_swap_kt"]
    max_neighbour = (len(neigh_order) - 1)
    max_iteration_neigh = 200

    worse_sol_percentage = 0.15
    ws_counter_limit = 20

    initial_score = 2
    rewards_values = np.array([3, 2, 1, 0])


    '''-----------------------------------------------------------------------------------------------------------------------'''
    
    seed = 42 
    random.seed(seed)
    np.random.seed(seed)
    random2.seed(seed)


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
    
    print("\nINITIAL SOLUTION --------------------------------------")
    print(solution_0.OBJ_tot_dist)
    # solution_0.print()


    ''' AVND ALGORITHM '''
    current_solution = copy.deepcopy(solution_0)
    best_solution = copy.deepcopy(solution_0)

    (best_solution, solution_history) = AVND_algorithm(
        n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, data, sorted_data, distance_matrix, distance_matrix_adjusted, closeness_matrix, 
        current_solution, best_solution,
        time_limit_VND,
        neigh_order, max_neighbour, max_iteration_neigh, ws_counter_limit, 
        worse_sol_percentage, 
        initial_score, rewards_values)

    ''' RESULTS '''
    # print("\nINITIAL SOLUTION --------------------------------------")
    # print(solution_0.OBJ_tot_dist)

    print("\nBEST SOLUTION -----------------------------------------")
    print(best_solution.OBJ_tot_dist)
    # best_solution.print()


    ''' save in excel '''
    # colonne base
    columns = ["Best Solution", "Current Solution", "Neighborhood", "Total Run", "Elapsed Time"]
    # aggiungi colonne per gli score
    columns.extend([f"Score_{name}" for name in neigh_order])

    # crate dataframe
    df = pd.DataFrame(solution_history, columns=columns)

    #save in excel
    df.to_excel(out_file_path, index=False)


if __name__ == "__main__":
    main()
    