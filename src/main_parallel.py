import numpy as np
import matplotlib.pyplot as plt
import copy
import random
import random2
import time


import algorithms.VND
import algorithms.assign_route
import algorithms.feasibility_function_POOP
import utils
import algorithms
import classes


import os
from concurrent.futures import ProcessPoolExecutor, as_completed


# Settings
MAX_WORKERS = 8  # Numero massimo di core da usare (modifica a piacere)
input_dir = "data"     # Cartella con i file p01, p02, ..., p32
output_dir = "out/results/results_43_500"  # Cartella dove verranno salvati i risultati


def solver(file_path, instance_number):

    seed = 42 
    random.seed(seed)
    np.random.seed(seed)
    random2.seed(seed)

    start_time = time.process_time()

    '''DATA PREPARATION'''
    distance_type = 1
    (n_vehicles, n_days, vehicle_capacity, data, sorted_data, n_clients, max_clients_kd, distance_matrix, distance_matrix_adjusted, closeness_matrix) = \
        utils.data_preparation(file_path, distance_type)
    
    '''INITIAL SOLUTION'''
    solution_0 = algorithms.assign_route.assign_to_1_vehicle_algorithm(
        n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, sorted_data, distance_matrix, distance_matrix_adjusted, closeness_matrix
    )
    # check fesibility
    V_distances_matrix, V_loads_matrix, solution_0 = algorithms.feasibility_function_POOP.check_feasibility_1vehicle(
        n_vehicles, n_days, n_clients, data, max_clients_kd, vehicle_capacity, distance_matrix, 
        solution_0)    
    if np.any(solution_0.feasibility_vector) != 1 or np.any(solution_0.verification_vector) != 1:
        return f"Instance {instance_number} - Soluzione iniziale non fattibile.\n"

    '''VND ALGORITHM'''
    current_solution = copy.deepcopy(solution_0)

    max_neighbour = 4
    max_iteration_neigh = 500
    max_iteration_vector = np.array([max_iteration_neigh]*(max_neighbour+1))
    time_limit_VND = 7200   # 2h*60min*60sec = 7200sec
    time_limit_neigh = 7200  # 12min*60 sec = 900sec (=1/10)

    if instance_number == 3 or instance_number == 6 or instance_number == 9:
        max_neighbour = 1
    
    (new_vnd_best_solution, new_sol_per_neigh) = algorithms.VND.VND_algorithm_condensed(n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, data, sorted_data, distance_matrix, closeness_matrix, 
                                                               current_solution, max_neighbour, max_iteration_vector, time_limit_VND, time_limit_neigh)

    total_time = time.process_time() - start_time

    results_txt = utils.save_results_in_txt(instance_number, n_vehicles, n_clients, n_days, vehicle_capacity, solution_0, new_vnd_best_solution, new_sol_per_neigh, total_time,
                                            max_neighbour, max_iteration_neigh, time_limit_VND, time_limit_neigh)

    return results_txt


def solve_instance(filename):

    input_path = os.path.join(input_dir, filename + ".txt")
    output_path = os.path.join(output_dir, filename + ".txt")
    instance_number = int(filename[1:])  # 'p01' -> 1

    result = solver(input_path, instance_number)

    with open(output_path, 'w') as f:
        f.write(result)

    return filename


def main():

    os.makedirs(output_dir, exist_ok=True)
    instance_files = [f"p{str(i).zfill(2)}" for i in range(1, 33)]

    print(f"Avvio elaborazione parallela con {MAX_WORKERS} worker...\n")

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(solve_instance, file): file for file in instance_files}

        for future in as_completed(futures):
            instance = futures[future]
            try:
                future.result()
                print(f"{instance} completata.")
            except Exception as e:
                print(f"Errore in {instance}: {e}")

    print("\nElaborazione completata.")


if __name__ == "__main__":
    main()
