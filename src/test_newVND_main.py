
import numpy as np
import matplotlib.pyplot as plt
import itertools
import random
import random2
import copy
import time
import json
import os 

import algorithms
import algorithms.VND
import algorithms.VND_new
import algorithms.assign_route
import algorithms.feasibility_function_POOP
import algorithms.similarity_measures
import utils


# def save_solution(sol, file_path_out):
#     os.makedirs(os.path.dirname(file_path_out), exist_ok=True)

#     data = sol.__dict__.copy()

#     # Converte tutti gli ndarray in liste
#     for key, value in data.items():
#         if isinstance(value, np.ndarray):
#             data[key] = value.tolist()

#     with open(file_path_out, "w") as f:
#         json.dump(data, f, indent=4)


def main():

    ''' USER INTERFACE -------------------------------------------------------------------------------------------------------'''
    
    file_path = "data/p02.txt"     # type name of file, ex: p02.txt
    distance_type = 1       # select: Euclidean = 1, Manhattan = 2

    # assicurati che la cartella esista
    os.makedirs("out/results/similarity_test", exist_ok=True)
    file_path_out = "out/results/similarity_test/solution_base.txt"

    filename = "out/results/vrp_tests/p12_1_999_3600.xlsx"
    imgname = "out/results/vrp_tests/p12_1_999_3600.png"

    # VND parameters
    repetitions_VND = [1, 0]    # first value indicate repetitons where worse solution is accepted (True), the second where False 
    time_limit_VND = 30   # 2h*60min*60sec = 7200sec
    time_limit_neigh = 7200  # not used

    # neigh_order = ["k_move_t", "t_move_k", "move_kt", "k_swap_t", "t_swap_k", "f_swap_kt", "swap_kt", "t_multiswap_k"]
    neigh_order = ["k_move_t", "t_move_k", "move_kt", "k_swap_t", "t_swap_k", "f_swap_kt", "swap_kt"]

    # initial_neigh_VND = [0, worse_sol_neigh, worse_sol_neigh]
    max_neighbour = (len(neigh_order) -1)
    max_iteration_neigh = 200

    two_opt_iteration = 500    

    # worse solution parameters
    worse_sol_neigh = 1
    worse_sol_percentage = 0.15
    # ----------------------------------------------------#
    tot_rep_VND = (repetitions_VND[0] + repetitions_VND[1])
    worse_sol_acc_VND = np.empty(tot_rep_VND, dtype=bool)
    for rep in range(repetitions_VND[0]):
        worse_sol_acc_VND[rep] = False
    for rep in range(repetitions_VND[1]):
        worse_sol_acc_VND[rep + repetitions_VND[0]] = True
   
    # A-VND parameters ---------------------------------- #
    ws_counter_limit = 200
    initial_score = 3
    rewards_values = [8, 4, 2, 1] 

    
    '''-----------------------------------------------------------------------------------------------------------------------'''
    
    seed = 42 
    random.seed(seed)
    np.random.seed(seed)
    random2.seed(seed)

    
    # start_time = time.process_time()

    '''DATA PREPARATION'''
    print("Preparing data...")
    (n_vehicles, n_days, vehicle_capacity, data, sorted_data, n_clients, max_clients_kd, distance_matrix, distance_matrix_adjusted, closeness_matrix) = \
        utils.data_preparation(file_path, distance_type)
    print("Preparing data completed.")
    
    '''INITIAL SOLUTION'''
    print("Preparing initial solution...")
    solution_0 = algorithms.assign_route.assign_to_1_vehicle_algorithm(
        n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, sorted_data, distance_matrix, distance_matrix_adjusted, closeness_matrix)
    print("Preparing initial solution. completed.")
    
    # check fesibility
    print("Preparing check feasibility...")
    V_distances_matrix, V_loads_matrix, solution_0 = algorithms.feasibility_function_POOP.check_feasibility_1vehicle(
        n_vehicles, n_days, n_clients, data, max_clients_kd, vehicle_capacity, distance_matrix, 
        solution_0)    
    if np.any(solution_0.feasibility_vector) != 1 or np.any(solution_0.verification_vector) != 1:
        return f"Instance p02 - Soluzione iniziale non fattibile.\n"
    print("Check feasibility completed.")

    sim_1_initial= algorithms.similarity_measures.def_sim_1_matrix(n_vehicles, n_days, solution_0)
   
   
    '''VND ALGORITHM'''
    
    # all_best_solutions_VND = np.zeros((len(worse_sol_acc_VND)+1), dtype=float)
    # all_best_solutions_VND[0] = solution_0.OBJ_tot_dist
    current_solution = copy.deepcopy(solution_0)
    best_solution = copy.deepcopy(solution_0)
    # best_solution_OBJ = solution_0.OBJ_tot_dist
    # all_solutions_VND = []
    # all_solutions_VND.append(float(current_solution.OBJ_tot_dist))
    number_new_sol = 0
    tot_iteration_VND = 0

    '--------------------------------------------------------------------------------'
    

    start_time_VND = time.process_time()

    print("**************************")
    print("  Starting algorithm...   ")
    print("**************************")

    (base_solution, solution_history, neigh_out_parameters) = algorithms.VND_new.AVND_algorithm(
        n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, data, sorted_data, distance_matrix, distance_matrix_adjusted, closeness_matrix, 
        current_solution, best_solution, 
        time_limit_VND, 
        neigh_order, max_neighbour, max_iteration_neigh, ws_counter_limit, 
        worse_sol_percentage, 
        initial_score, rewards_values)

    print("**************************")
    print("   algorithm finished.    ")
    print("**************************")

    ''' NEW PROBLEM '''
    
    time_limit_VND = 60   # 2h*60min*60sec = 7200sec
    start_time_VND = time.process_time()

    print("**************************")
    print("  Starting algorithm...   ")
    print("**************************")

    (new_solution, solution_history, neigh_out_parameters) = algorithms.VND_new.AVND_algorithm(
        n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, data, sorted_data, distance_matrix, distance_matrix_adjusted, closeness_matrix, 
        current_solution, best_solution, 
        time_limit_VND, 
        neigh_order, max_neighbour, max_iteration_neigh, ws_counter_limit, 
        worse_sol_percentage, 
        initial_score, rewards_values)

    print("**************************")
    print("   algorithm finished.    ")
    print("**************************")


    ''' SIMILARITY '''

    # first similarity measure
    sim_1_base = algorithms.similarity_measures.def_sim_1_matrix(n_vehicles, n_days, base_solution)
    sim_1_new = algorithms.similarity_measures.def_sim_1_matrix(n_vehicles, n_days, new_solution)
    (sim_1_value, sim_1_vehicle_pairings) = algorithms.similarity_measures.measure_sim_1(n_vehicles, sim_1_base, sim_1_new)

    # second similarity measure
    sim_2_base = algorithms.similarity_measures.def_sim_2_matrix(n_vehicles, n_days, base_solution)
    sim_2_new = algorithms.similarity_measures.def_sim_2_matrix(n_vehicles, n_days, new_solution)
    (sim_2_value, sim_2_vehicle_pairings) = algorithms.similarity_measures.measure_sim_2(n_vehicles, n_days, sim_2_base, sim_2_new)

    # third similarity measure
    sim_3_base = algorithms.similarity_measures.def_sim_3_matrix(n_vehicles, n_days, base_solution)
    sim_3_new = algorithms.similarity_measures.def_sim_3_matrix(n_vehicles, n_days, new_solution)
    (sim_3_value, sim_3_vehicle_pairings) = algorithms.similarity_measures.measure_sim_3(n_vehicles, n_days, sim_3_base, sim_3_new)


    ''' RESULTS '''

    # total_time_VND = time.process_time() - start_time_VND
    # print("total_time", total_time_VND)

    # print("all_best_solutions_VND", all_best_solutions_VND)
    # print("initial solution OBJ", solution_0.OBJ_tot_dist)
    # print("best solution OBJ", best_solution.OBJ_tot_dist)
    # print(f"neigh_out_parameters: \n{neigh_out_parameters}\n\n")
    base_solution.print()
    print("\n\n")
    new_solution.print()
    print("\n\n")
    print(f"sim_1: {sim_1_value}, pairings: {sim_1_vehicle_pairings}")
    print(f"sim_2: {sim_2_value}, pairings: {sim_2_vehicle_pairings}")
    print(f"sim_3: {sim_3_value}, pairings: {sim_3_vehicle_pairings}")



    # ''' SAVE SOLUTION '''
    # save_solution(best_solution, file_path_out)



    # utils.save_vnd_results_in_excel(
    #     filename, 
    #     repetitions_VND, time_limit_VND, neigh_order, max_iteration_neigh, worse_sol_neigh, worse_sol_percentage,
    #     total_time_VND, tot_iteration_VND, solution_0.OBJ_tot_dist, best_solution_OBJ, all_solutions_VND)
    
    # print("number_new_sol", number_new_sol, len(all_solutions_VND))
    # print("all_solutions_VND", all_solutions_VND)


    ''' CLUSTERS '''
    # Calculate centroid and radius of each group of customers
    # centroids, radii = utils.calculate_grups_data(
    #     n_vehicles, n_days, data, solution_0.assigned_ordered_matrix, radius_mode='mean_dist', fixed_radius=10)
    # print("centroids:", centroids)
    # print("radius:", radii)
    # print("\n\n")



    ''' FEASIBILITY FUNCTION '''
    # routes_matrix, sub_routes_matrix, summed_powers, V_distances_matrix, V_loads_matrix = \
    #     algorithms.feasibility_function.check_feasibility_1vehicle(
    #         n_vehicles, n_days, n_clients, data, max_clients_kd, vehicle_capacity, solution_0.assigned_ordered_matrix,
    #           distance_matrix, solution_0.route_dist_matrix, solution_0.transp_demand_matrix
    #         )
    
    # V_distances_matrix, V_loads_matrix, solution_0 = algorithms.feasibility_function_POOP.check_feasibility_1vehicle(
    #     n_vehicles, n_days, n_clients, data, max_clients_kd, vehicle_capacity, distance_matrix, solution_0)
    # solution_0.feasibility_vector.print()
    # solution_0.verification_vector.print()
    # print("\n verify distances:\n", V_distances_matrix)
    # print("\n verify loads:\n", V_loads_matrix)
    


    # ''' PLOTS '''
    # # utils.plot_manhattan_vehicles_routes(n_vehicles, n_days, data, assigned_ordered_matrix)
    # utils.plot_euclidean_vehicles_routes(n_vehicles, n_days, data, solution_0.assigned_ordered_matrix)

    # utils.plot_group_clients(n_vehicles, n_days, data, solution_0.assigned_ordered_matrix, centroids, radii)


    # utils.plot_VND_graph(all_solutions_VND, imgname)
    # plt.show()
    

    # plt.show()
    # return

if __name__ == "__main__":
    main()

