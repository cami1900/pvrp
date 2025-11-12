
import numpy as np
import matplotlib.pyplot as plt
import copy
import random
import random2
import time
import traceback

import conf
# import algorithms
import algorithms.VND
# import algorithms.VND_new
from algorithms.VND_multiOBJ import AVND_multiOBJ_algorithm
from algorithms.assign_route import (assign_to_1_vehicle_algorithm, assign_not_assigned, solve_vrp_day)
import algorithms.feasibility_function_POOP
import algorithms.similarity_measures as sim_calc
from algorithms.similarity_measures import get_sim_functions
import utils
import classes


import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed


# Settings


''' SETTINGS -------------------------------------------------------------------------------------------------------'''

MAX_WORKERS = 8     # Maximum number of cores to use (change as desired) --> CLUSTER: max = 4

# Directory
input_dir_base = "data"
input_dir_new  = "data_new"     # To create a new dataset, create a folder and rename path
output_dir = "out/results/AVND_multiobj"       # Create new folder to avoid overwriting results and rename path

# instances
first_file = 1  #1
last_file = 32   #32

distance_type = 1       # select: Euclidean = 1, Manhattan = 2 (NOT use!!)

# VRP solver
max_iter_vrp = 500

# similarity
similarity_measures = ["sim_1", "sim_2", "sim_3"]
weights = [0.5, 0.5]

# VND parameters
repetitions_VND = [1, 0]    # first value indicate repetitons where worse solution is accepted (True), the second where False 
time_limit_VND = 5 #(2*60*60)   # 2h*60min*60sec = 7200sec
max_iteration_neigh = 100
ws_counter_limit = 20
worse_sol_percentage = 0.15

# neigh_order = ["k_move_t", "t_move_k", "move_kt", "k_swap_t", "t_swap_k", "f_swap_kt", "swap_kt", "t_swap_r_k", t_multiswap_k"]
neigh_order = ["k_move_t", "t_move_k", "move_kt", "k_swap_t", "t_swap_k", "f_swap_kt", "swap_kt", "t_swap_r_k"]

# A-VND parameters ---------------------------------- 
initial_score = 3
rewards_values = [8, 4, 2, 1] 

# Demand fluctuation parameters
total_mode = 0                 # 0 = totale costante, 1 = può variare entro capacità
fluct_mode = "compensated"     # "compensated", "mixed", "uniform"
client_affected_pct = 1        # % di clienti influenzati (0-1)
variance_pct = 0.5             # ampiezza fluttuazione (%(0-1) rispetto alla domanda)
distr_type = "gamma"         # "gamma" o "poisson"
margin_pct = 0.1               # % di margine (0-1)

''' ----------------------------------------------------------------------------------------------------------------'''


def initial_solution_solver(output_path, instance_number, data, sorted_data, path_img_v, path_img_d,
                    n_vehicles, n_clients, n_days, vehicle_capacity, max_clients_kd,
                    distance_matrix, distance_matrix_adjusted, closeness_matrix):

    start_time = time.process_time()

    '''INITIAL SOLUTION'''
    solution_0 = assign_to_1_vehicle_algorithm(
        n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, sorted_data, distance_matrix, distance_matrix_adjusted, closeness_matrix)
    # print(f"solution_0 trovata--> not_assigned_list = {solution_0.not_assigned_list} \nverifico feasibility:")
    
    # if there are not_assigned clients, try to assign
    # if np.any(solution_0.not_assigned_list != 0):
    #     (solution_0, error_index) = assign_not_assigned(
    #         n_vehicles, n_days, distance_matrix, closeness_matrix, vehicle_capacity,
    #           data, solution_0)
    #     # if a client canNOT be assigned: save data and break the instance
    #     if not error_index:  
    #         print(f"Warning: Not all customers can be assigned to the instance {instance_number}!")
    #     return f"Instance p{instance_number} - error: not all customers assignable.\n"

    ''' check fesibility '''
    V_distances_matrix, V_loads_matrix, solution_0 = algorithms.feasibility_function_POOP.check_feasibility_1vehicle(
        n_vehicles, n_days, n_clients, data, max_clients_kd, vehicle_capacity, distance_matrix, 
        solution_0)
    if np.any(solution_0.feasibility_vector) != 1 or np.any(solution_0.verification_vector) != 1:
        return f"Instance p{instance_number} - unable to determine a feasible initial solution.\n"

    print(f"p{instance_number}: initial solution done")


    ''' SOLVE VRP '''
    solution_1 = solve_vrp_day(
        n_vehicles, n_days, n_clients, vehicle_capacity, max_clients_kd, data, distance_matrix, 
        max_iter_vrp,
        solution_0)

    ''' check fesibility '''
    V_distances_matrix, V_loads_matrix, solution_1 = algorithms.feasibility_function_POOP.check_feasibility_pvrp(
        n_vehicles, n_days, n_clients, data, max_clients_kd, vehicle_capacity, distance_matrix, 
        solution_1)    
    if np.any(solution_1.feasibility_vector) != 1 or np.any(solution_1.verification_vector) != 1:
        return f"Instance p{instance_number} - unable to determine a feasible initial solution.\n"

    print(f"p{instance_number}: vrp solution done")

    total_time = time.process_time() - start_time

    # '''VND ALGORITHM'''

    # max_neighbour = (len(neigh_order) -1)

    # tot_rep_VND = (repetitions_VND[0] + repetitions_VND[1])
    # worse_sol_acc_VND = np.empty(tot_rep_VND, dtype=bool)
    # for rep in range(repetitions_VND[0]):
    #     worse_sol_acc_VND[rep] = False
    # for rep in range(repetitions_VND[1]):
    #     worse_sol_acc_VND[rep + repetitions_VND[0]] = True

    # # start_time = time.process_time()

    # current_solution = copy.deepcopy(solution_0)
    # best_solution = copy.deepcopy(solution_0)

    # (optimised_solution, solution_history, neigh_out_parameters) = algorithms.VND_new.AVND_algorithm(
    #     n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, data, sorted_data, distance_matrix, distance_matrix_adjusted, closeness_matrix, 
    #     current_solution, best_solution, 
    #     time_limit_VND, 
    #     neigh_order, max_neighbour, max_iteration_neigh, ws_counter_limit, 
    #     worse_sol_percentage, 
    #     initial_score, rewards_values,
    #     instance_number)

    # total_time = time.process_time() - start_time

    ''' ------------------------------ SAVE RESULTS ------------------------------- '''

    solution_txt = utils.save_initial_solution_in_txt(instance_number, n_vehicles, n_clients, n_days, vehicle_capacity, 
                             solution_0, solution_1, 
                             total_time)
    
    with open(output_path, 'w') as f:
        f.write(solution_txt)

    utils.plot_save_vehi_routes(n_vehicles, n_days, data, solution_1.assigned_ordered_matrix, path_img_v)
    utils.plot_save_day_routes(n_vehicles, n_days, data, solution_1.assigned_ordered_matrix, path_img_d)

    return solution_1


def multi_obj_solver(output_path,
                     n_vehicles, n_days,  n_clients, max_clients_kd, vehicle_capacity, data, sorted_data,
                     distance_matrix, distance_matrix_adjusted, closeness_matrix,
                     instance_number,
                     sim_type, weights, solution_1,
                     path_graph_i_new_opt, path_graph_t_new_opt,
                     path_img_v_new_opt, path_img_d_new_opt):

    ''' prepare data '''
    max_neighbour = (len(neigh_order) -1)

    tot_rep_VND = (repetitions_VND[0] + repetitions_VND[1])
    worse_sol_acc_VND = np.empty(tot_rep_VND, dtype=bool)
    for rep in range(repetitions_VND[0]):
        worse_sol_acc_VND[rep] = False
    for rep in range(repetitions_VND[1]):
        worse_sol_acc_VND[rep + repetitions_VND[0]] = True


    ''' update initial solution '''     # change class Solution
    # Calculate similarity
    if sim_type in ["sim_1", "sim_2", "sim_3"]:
        def_funcs, update_func, measure_func = get_sim_functions(sim_type, sim_calc)

        sim_matrix = def_funcs(n_vehicles, n_days, solution_1.assigned_ordered_matrix)
        
    # Calculate OBJ value 
    tot_dist = solution_1.OBJ_tot_dist
    sim_value  = 1.0
    OBJ_value = 1.0  
    
    # save solution
    current_solution = classes.Solution_multiOBJ(OBJ_value, tot_dist, sim_value,
                                                 solution_1.assigned_ordered_matrix, solution_1.not_assigned_list, 
                                                 solution_1.transp_demand_matrix, solution_1.route_dist_matrix,
                                                 sim_matrix)
    best_solution = copy.deepcopy(current_solution)


    ''' AVND with multi-OBJ '''

    (best_solution, solution_history, neigh_out_parameters) = AVND_multiOBJ_algorithm(
        n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, data, sorted_data, 
        distance_matrix, distance_matrix_adjusted, closeness_matrix, 
        current_solution, best_solution, 
        time_limit_VND, 
        neigh_order, max_neighbour, max_iteration_neigh, ws_counter_limit, 
        worse_sol_percentage, 
        initial_score, rewards_values,
        instance_number,
        sim_type, weights)
    

    ''' save results '''
    solution_txt = utils.save_opt_solution_in_txt(instance_number, n_vehicles, n_clients, n_days, vehicle_capacity, 
                                                    best_solution, 
                                                    solution_history, neigh_out_parameters, 
                                                    neigh_order, max_iteration_neigh, time_limit_VND)
    with open(output_path, 'w') as f:
        f.write(solution_txt)

    utils.plot_save_iteration_graph(solution_history, path_graph_i_new_opt)
    utils.plot_save_time_graph(solution_history, path_graph_t_new_opt)

    utils.plot_save_vehi_routes(n_vehicles, n_days, data, solution_1.assigned_ordered_matrix, path_img_v_new_opt)
    utils.plot_save_day_routes(n_vehicles, n_days, data, solution_1.assigned_ordered_matrix, path_img_d_new_opt)

    return 


def similarity_solver(output_path, instance_number, n_vehicles, n_days, base_solution, new_solution):

    ''' SIMILARITY '''

    # first similarity measure
    sim_1_base = sim_calc.def_sim_1_matrix(n_vehicles, n_days, base_solution.assigned_ordered_matrix)
    sim_1_new = sim_calc.def_sim_1_matrix(n_vehicles, n_days, new_solution.assigned_ordered_matrix)
    (sim_1_value, sim_1_combinations_matrix, sim_1_vehicle_pairings, sim_1_measures) = \
        sim_calc.measure_sim_1(n_vehicles, n_days, sim_1_base, sim_1_new)

    # second similarity measure
    sim_2_base = sim_calc.def_sim_2_matrix(n_vehicles, n_days, base_solution.assigned_ordered_matrix)
    sim_2_new = sim_calc.def_sim_2_matrix(n_vehicles, n_days, new_solution.assigned_ordered_matrix)
    (sim_2_value, sim_2_combinations_matrix, sim_2_vehicle_pairings, sim_2_measures) = \
        sim_calc.measure_sim_2(n_vehicles, n_days, sim_2_base, sim_2_new)

    # third similarity measure
    sim_3_base = sim_calc.def_sim_3_matrix(n_vehicles, n_days, base_solution.assigned_ordered_matrix)
    sim_3_new = sim_calc.def_sim_3_matrix(n_vehicles, n_days, new_solution.assigned_ordered_matrix)
    (sim_3_value, sim_3_combinations_matrix, sim_3_vehicle_pairings, sim_3_measures) =\
          sim_calc.measure_sim_3(n_vehicles, n_days, sim_3_base, sim_3_new)

    # save data
    similarity_txt = utils.save_sim_measures_in_txt(instance_number,
                              sim_1_value, sim_1_combinations_matrix, sim_1_vehicle_pairings, sim_1_measures,
                              sim_2_value, sim_2_combinations_matrix, sim_2_vehicle_pairings, sim_2_measures,
                              sim_3_value, sim_3_combinations_matrix, sim_3_vehicle_pairings, sim_3_measures)
    with open(output_path, 'w') as f:
        f.write(similarity_txt)

    return


def instance_solver(filename):

    # seed
    seed = 42 
    random.seed(seed)
    np.random.seed(seed)
    random2.seed(seed)

    ''' INSTANCE '''
    instance_number = int(filename[1:])  # 'p01' -> 1

    ''' PATHS '''
    output_dir_instance = os.path.join(output_dir, filename)
    os.makedirs(output_dir_instance, exist_ok=True)     # Crea automaticamente la directory (e sottocartelle se mancano)

    path_data_base = os.path.join(input_dir_base, filename + ".txt")
    path_results_base = os.path.join(output_dir_instance, filename + "_base" + ".txt")
    path_img_v_base = os.path.join(output_dir_instance, filename + "_img_v_base" + ".jpg")
    path_img_d_base = os.path.join(output_dir_instance, filename + "_img_d_base" + ".jpg")

    path_data_new  = os.path.join(input_dir_new,  filename + ".txt")
    path_results_new = os.path.join(output_dir_instance, filename + "_new" + ".txt")
    path_img_v_new = os.path.join(output_dir_instance, filename + "_img_v_new" + ".jpg")
    path_img_d_new = os.path.join(output_dir_instance, filename + "_img_b_new" + ".jpg")

    
    ''' INSTANCE BASE '''
        # Prepare data
    (n_vehicles, n_days, vehicle_capacity,
      data, sorted_data, 
      n_clients, max_clients_kd, first_data_index,
        distance_matrix, distance_matrix_adjusted, closeness_matrix) = \
        utils.data_preparation(path_data_base, distance_type)
    print(f"{filename}: data prepared")
    
    # Solve instance base
    sol_base = initial_solution_solver(path_results_base, instance_number, data, sorted_data, path_img_v_base, path_img_d_base,
                    n_vehicles, n_clients, n_days, vehicle_capacity, max_clients_kd,
                    distance_matrix, distance_matrix_adjusted, closeness_matrix)
    print(f"{filename}: base solution found")


    ''' INSTANCE NEW '''
    # Create new instances (demand fluctuation)
    # data_new = utils.create_new_dataset(
    #     path_data_base, path_data_new,
    #     data, first_data_index, vehicle_capacity, n_vehicles, n_days,
    #     distance_type,
    #     total_mode, fluct_mode, client_affected_pct, variance_pct, distr_type, margin_pct,
    #     )
    # sorted_data_new = utils.sort_data(data_new)

    # Prepare data
    (n_vehicles, n_days, vehicle_capacity,
      data_new, sorted_data_new, 
      n_clients, max_clients_kd, first_data_index,
        distance_matrix, distance_matrix_adjusted, closeness_matrix) = \
        utils.data_preparation(path_data_new, distance_type)
    print(f"{filename}: data prepared")
    
    
    print(f"{filename}: new data prepared")

    # Solve instance new
    sol_new  = initial_solution_solver(path_results_new, instance_number, data_new, sorted_data_new, path_img_v_new, path_img_d_new,
                    n_vehicles, n_clients, n_days, vehicle_capacity, max_clients_kd,
                    distance_matrix, distance_matrix_adjusted, closeness_matrix)
    print(f"{filename}: new solution found")


    ''' AVND multi-objective '''

    for sim_type in similarity_measures:
        path_results_new_opt = os.path.join(output_dir_instance, filename + "_" + sim_type + ".txt")
        path_graph_i_new_opt = os.path.join(output_dir_instance, filename + "_" + sim_type + "_graph_i" + ".jpg")
        path_graph_t_new_opt = os.path.join(output_dir_instance, filename + "_" + sim_type + "_graph_t" + ".jpg")
        path_img_v_new_opt = os.path.join(output_dir_instance, filename + "_" + sim_type + "_img_v" + ".jpg")
        path_img_d_new_opt = os.path.join(output_dir_instance, filename + "_" + sim_type + "_img_bt" + ".jpg")

        multi_obj_solver(path_results_new_opt,
                     n_vehicles, n_days,  n_clients, max_clients_kd, vehicle_capacity, data, sorted_data,
                     distance_matrix, distance_matrix_adjusted, closeness_matrix,
                     instance_number,
                     sim_type, weights, sol_new,
                     path_graph_i_new_opt, path_graph_t_new_opt,
                     path_img_v_new_opt, path_img_d_new_opt)

        # Se la funzione ha restituito una stringa di errore, esci subito
        if isinstance(sol_new, str):
            print(sol_new.strip())
            return  # <-- fermati, non calcolare la similarità
        
        path_results_similarity = os.path.join(output_dir_instance, filename + "_" + sim_type + ".txt")

        ''' SIMILARITY '''
        # Solve similarity
        similarity_solver(path_results_similarity, instance_number, n_vehicles, n_days, sol_base, sol_new)
        print(f"{filename}: similarity measures calculated")

    return filename



def main():

    # --- Print current configuration ---
    print("\n==================== CURRENT CONFIGURATION ====================")
    print(f"MAX_WORKERS: {MAX_WORKERS}")
    print(f"Input directory (base): {input_dir_base}")
    print(f"Input directory (new): {input_dir_new}")
    print(f"Output directory: {output_dir}")
    print(f"Distance type: {'Euclidean' if distance_type == 1 else 'Manhattan'}")
    print(f"VND repetitions (accept worse, reject worse): {repetitions_VND}")
    print(f"VND time limit: {time_limit_VND} sec")
    print(f"Max neighborhood iterations: {max_iteration_neigh}, ws_counter_limit={ws_counter_limit}")
    print(f"Worse solution acceptance percentage: {worse_sol_percentage}")
    print(f"Neighborhood order: {neigh_order}")
    print(f"A-VND parameters -> initial_score={initial_score}, rewards_values={rewards_values}")
    print(f"Demand fluctuation: mode={fluct_mode}, distribution type={distr_type}")
    print(f"Affected clients: {client_affected_pct*100:.0f}%, Variance: {variance_pct*100:.0f}%, Margin: {margin_pct*100:.0f}%")
    print("=================================================================\n")

    # --- User confirmation ---
    proceed = input("⚙️  Do you want to continue with the execution? (yes/no): ").strip().lower()
    if proceed not in ['y', 'yes']:
        print("⛔ Execution aborted by user.")
        sys.exit(0)

    # --- Execution ---
    os.makedirs(output_dir, exist_ok=True)
    instance_files = [f"p{str(i).zfill(2)}" for i in range(first_file, last_file+1)]

    print(f"Avvio elaborazione parallela con {MAX_WORKERS} worker...\n")

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(instance_solver, file): file for file in instance_files}

        for future in as_completed(futures):
            instance = futures[future]
            try:
                future.result()
                print(f"{instance} completata.")
            except Exception as e:
                print(f"Errore in {instance}: {e}")
                traceback.print_exc()

    print("\nElaborazione completata.")


if __name__ == "__main__":
    main()
