from py2opt142.py2opt.routefinder import RouteFinder

import algorithms.assign_route
import utils
import algorithms
from algorithms.assign_route import calculate_tot_dist 
import conf
import numpy as np
import copy
import matplotlib.pyplot as plt

from algorithms.route_optimizer import TSP
import logging


'''DATA PREPARATION'''

# file_path = "data/p0_trial.txt"
file_index = 2
file_path = f"data/p02.txt"
distance_type = 1



'''INITIAL SOLUTION'''
        # Prepare data
(n_vehicles, n_days, vehicle_capacity,
    data, sorted_data, n_clients, max_clients_kd, first_data_index,
    distance_matrix, distance_matrix_adjusted, closeness_matrix) = \
    utils.data_preparation(file_path, distance_type)


''' INITIAL SOLUTION '''
solution_0 = algorithms.assign_route.assign_to_1_vehicle_algorithm(
        n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, sorted_data, distance_matrix, distance_matrix_adjusted, closeness_matrix)


''' OPTIMIZER '''

logger = logging.getLogger("pvrp_tsp")
tsp = TSP(None, logger)

# for vehicle in range(n_vehicles):
#     for day in range(n_days):
#         route = copy.deepcopy(solution_0.assigned_ordered_matrix[vehicle, day])

solution_1 = copy.deepcopy(solution_0)
route = solution_1.assigned_ordered_matrix[0, 0]
original_length = len(route)
idx = np.where(route == 0)[0][2]    # remove final zeros
route = route[:idx]
print(route)

# extract coordinates:
coords = np.array([data[data[:,conf.CLIENT_ID_INDEX] == cid, 
                        conf.X_COORD_INDEX:(conf.Y_COORD_INDEX+1)][0] for cid in route])
print(coords)

# find optimal route:
    # 3-opt per miglioramento locale
opt_route, dist = tsp.opt_3_local_search(coords.tolist())
    # Aggiorna la soluzione nella classe (necessario per 2-opt)
tsp.random_solution = opt_route
    # 2-opt refinement
refined_route_coords = tsp.perform_2_opt_swap_NO_depot()
print(refined_route_coords)


# return to id_client
    # Crea un dizionario coordinate → ID
coord_to_id = {tuple(row[1:3]): int(row[0]) for row in data}
    # Converti le coordinate ottimizzate in ID
optimized_ids = [coord_to_id[tuple(coord)] for coord in np.array(refined_route_coords)]
optimized_route = np.array(optimized_ids)

optimized_cost = tsp.calc_tour_cost(np.array([coord_to_id[tuple(coord)] for coord in refined_route_coords]))
# calcola quanti zeri servono per riempire
padding_length = original_length - len(optimized_route)
# ricrea la route con padding
final_route = np.concatenate([optimized_route, np.zeros(padding_length, dtype=int)])
print(optimized_route)
print("Costo ottimizzato:", optimized_cost)
solution_1.assigned_ordered_matrix[0, 0] = final_route


(OBJ_tot_dist_optimized) = calculate_tot_dist(n_vehicles, n_days, solution_0.route_dist_matrix, solution_0.OBJ_tot_dist)
print(solution_0.OBJ_tot_dist)
print(OBJ_tot_dist_optimized)

