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

from openpyxl import Workbook, load_workbook
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed


# Settings


''' SETTINGS -------------------------------------------------------------------------------------------------------'''

MAX_WORKERS = 4     # Maximum number of cores to use (change as desired) --> CLUSTER: max = 4

# Directory
input_dir_base = "data"
input_dir_new  = "data_new"     # To create a new dataset, create a folder and rename path
output_dir = "out/results/initial_solution"       # Create new folder to avoid overwriting results and rename path

# instances
first_file = 9  #1
last_file = 32   #32

distance_type = 1       # select: Euclidean = 1, Manhattan = 2 (NOT use!!)

# VRP solver
max_iter_vrp = 500

# similarity
similarity_measures = ["sim_1", "sim_2", "sim_3"]
weights = [0.5, 0.5]

# VND parameters
repetitions_VND = [1, 0]    # first value indicate repetitons where worse solution is accepted (True), the second where False 
time_limit_VND = 1.5*60*60 #(2*60*60)   # 2h*60min*60sec = 7200sec
max_iteration_neigh = 100
ws_counter_limit = 20
worse_sol_percentage = 0.15

# neigh_order = ["k_move_t", "t_move_k", "move_kt", "k_swap_t", "t_swap_k", "f_swap_kt", "swap_kt", "t_swap_r_k", t_multiswap_k"]
neigh_order = ["t_move_k", "move_t", 
               "t_swap_k", "f_swap_t", "swap_t", 
               "t_swap_r_k", "t_multiswap_k"]

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



    ''' ------------------------------ SAVE RESULTS ------------------------------- '''

    solution_txt = utils.save_initial_solution_in_txt(instance_number, n_vehicles, n_clients, n_days, vehicle_capacity, 
                             solution_0, solution_1, 
                             total_time)
    
    with open(output_path, 'w') as f:
        f.write(solution_txt)

    utils.plot_save_vehi_routes(n_vehicles, n_days, data, solution_1.assigned_ordered_matrix, path_img_v)
    utils.plot_save_day_routes(n_vehicles, n_days, data, solution_1.assigned_ordered_matrix, path_img_d)

    return solution_0, solution_1


def instance_solver(filename):

    # seed
    seed = 42 
    random.seed(seed)
    np.random.seed(seed)
    random2.seed(seed)

    ''' INSTANCE '''
    instance_number = int(filename[1:])  # 'p01' -> 1

    ''' PATHS '''
    # output_dir_instance = os.path.join(output_dir, filename)
    # os.makedirs(output_dir_instance, exist_ok=True)     # Crea automaticamente la directory (e sottocartelle se mancano)

    path_data_base = os.path.join(input_dir_base, filename + ".txt")
    path_results_base = os.path.join(output_dir, filename + "_base" + ".txt")
    path_img_v_base = os.path.join(output_dir, filename + "_img_v_base" + ".jpg")
    path_img_d_base = os.path.join(output_dir, filename + "_img_d_base" + ".jpg")

    
    ''' INSTANCE BASE '''
        # Prepare data
    (n_vehicles, n_days, vehicle_capacity,
      data, sorted_data, 
      n_clients, max_clients_kd, first_data_index,
        distance_matrix, distance_matrix_adjusted, closeness_matrix) = \
        utils.data_preparation(path_data_base, distance_type)
    print(f"{filename}: data prepared")
    
    # Solve instance base
    sol_base_0, sol_base_1 = initial_solution_solver(path_results_base, instance_number, data, sorted_data, path_img_v_base, path_img_d_base,
                    n_vehicles, n_clients, n_days, vehicle_capacity, max_clients_kd,
                    distance_matrix, distance_matrix_adjusted, closeness_matrix)
    print(f"{filename}: base solution found")


    # save results
        # dopo aver calcolato sol_base
    sol0_obj = sol_base_0.OBJ_tot_dist
    sol1_obj = sol_base_1.OBJ_tot_dist
    
    excel_path = os.path.join(output_dir, "initial_solutions.xlsx")
    save_results_excel(
        excel_path,
        instance_number,
        n_vehicles,
        n_days,
        n_clients,
        sol0_obj,
        sol1_obj
    )


    return filename


def save_results_excel(
        excel_path,
        instance_number,
        n_vehicles,
        n_days,
        n_clients,
        sol0_obj,
        sol1_obj
    ):
    """
    Salva una riga nel file Excel contenente i risultati dell'istanza.
    Se il file non esiste, crea automaticamente un nuovo Excel con intestazioni.

    Colonne:
    - instance number
    - number vehicles
    - number days
    - number clients
    - solution_0 objective value
    - solution_1 objective value
    """

    # Se il file non esiste → crealo con header
    if not os.path.exists(excel_path):
        wb = Workbook()
        ws = wb.active
        ws.title = "Results"

        ws.append([
            "Instance",
            "Vehicles",
            "Days",
            "Clients",
            "Objective Solution 0",
            "Objective Solution 1"
        ])

        wb.save(excel_path)

    # Apri file esistente
    wb = load_workbook(excel_path)
    ws = wb.active

    # Aggiungi nuova riga
    ws.append([
        instance_number,
        n_vehicles,
        n_days,
        n_clients,
        sol0_obj,
        sol1_obj
    ])

    wb.save(excel_path)




def main_OLD():

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


def main():
    os.makedirs(output_dir, exist_ok=True)
    excel_path = os.path.join(output_dir, "initial_solutions.xlsx")

    instance_files = [f"p{str(i).zfill(2)}" for i in range(first_file, last_file+1)]

    for file in instance_files:
        try:
            instance_solver(file)
            print(f"{file} completata.")
        except Exception as e:
            print(f"Errore in {file}: {e}")
            traceback.print_exc()

    print("\nElaborazione completata.")


if __name__ == "__main__":
    main()