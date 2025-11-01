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

import numpy as np

def route_length(route, coords):
    """Calcola la lunghezza totale del percorso."""
    total = 0.0
    for i in range(len(route) - 1):
        a, b = route[i], route[i + 1]
        total += np.linalg.norm(coords[a] - coords[b])
    return total


def two_opt(route, coords):
    """Applica l'algoritmo 2-opt per ottimizzare la route (il deposito resta fisso)."""
    best_route = route.copy()
    best_distance = route_length(best_route, coords)
    improved = True

    while improved:
        improved = False
        for i in range(1, len(route) - 2):
            for j in range(i + 1, len(route) - 1):
                # Genera una nuova route invertendo il segmento [i:j]
                new_route = best_route.copy()
                new_route[i:j] = best_route[j-1:i-1:-1]
                new_distance = route_length(new_route, coords)
                if new_distance < best_distance:
                    best_route = new_route
                    best_distance = new_distance
                    improved = True
        route = best_route

    return best_route, best_distance


def three_opt(route, coords):
    """Applica l'algoritmo 3-opt per ottimizzare la route (il deposito resta fisso)."""
    best_route = route.copy()
    best_distance = route_length(best_route, coords)
    improved = True

    while improved:
        improved = False
        for i in range(1, len(route) - 4):
            for j in range(i + 1, len(route) - 3):
                for k in range(j + 1, len(route) - 2):
                    segments = [
                        best_route[0:i],
                        best_route[i:j],
                        best_route[j:k],
                        best_route[k:]
                    ]

                    # Tutte le possibili combinazioni (alcune inversioni)
                    options = [
                        segments[0] + segments[1] + segments[2] + segments[3],
                        segments[0] + segments[1][::-1] + segments[2] + segments[3],
                        segments[0] + segments[1] + segments[2][::-1] + segments[3],
                        segments[0] + segments[2][::-1] + segments[1][::-1] + segments[3],
                        segments[0] + segments[2] + segments[1] + segments[3],
                        segments[0] + segments[2][::-1] + segments[1] + segments[3],
                    ]

                    for new_route in options:
                        new_distance = route_length(new_route, coords)
                        if new_distance < best_distance:
                            best_route = new_route
                            best_distance = new_distance
                            improved = True
        route = best_route

    return best_route, best_distance


''' DATA '''
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

# select route
original_route = solution_0.assigned_ordered_matrix[0, 0]
optimized_route = solution_1.assigned_ordered_matrix[0, 0]
original_distance = solution_0.route_dist_matrix[0][0]
idx = np.where(original_route == 0)[0][2]    # remove final zeros
route = original_route[:idx]
print(route)

# extract coordinates:
original_coords = np.array([data[data[:,conf.CLIENT_ID_INDEX] == cid, 
                        conf.X_COORD_INDEX:(conf.Y_COORD_INDEX+1)][0] for cid in route])
print("original_coords", original_coords)

# find optimal route:
    # 3-opt per miglioramento locale
opt3_route_coord, dist = tsp.opt_3_local_search(original_coords.tolist())
    # Aggiorna la soluzione nella classe (necessario per 2-opt)
tsp.random_solution = opt3_route_coord
    # 2-opt refinement
opt2_route_coord = tsp.perform_2_opt_swap_NO_depot()



# return to id_client
    # Crea un dizionario coordinate → ID
coord_to_id = {tuple(row[1:3]): int(row[0]) for row in data}
    # Converti le coordinate ottimizzate in ID
optimized_ids = [coord_to_id[tuple(coord)] for coord in np.array(opt2_route_coord)]
print("optimized_ids", optimized_ids, type(optimized_ids))
# optimized_route = np.array(optimized_ids)
# print("optimized_route", optimized_route, type(optimized_route))

print("original_route", original_route)
print("optimized_route", optimized_route)
for client in range(len(optimized_ids)):
    optimized_route[client] = optimized_ids[client]
print("optimized_route", optimized_route)
print("sol_0", solution_0.assigned_ordered_matrix[0, 0])
print("sol_1", solution_1.assigned_ordered_matrix[0, 0])

optimized_distance = sum(distance_matrix[optimized_route[i], optimized_route[i + 1]] for i in range(len(optimized_route) - 1))
print(f"original_distance: {original_distance}, optimized_distance: {optimized_distance}")
solution_1.route_dist_matrix[0][0] = optimized_distance
solution_1.OBJ_tot_dist = 0
# # calcola quanti zeri servono per riempire
# padding_length = original_length - len(optimized_route)
# # ricrea la route con padding
# final_route = np.concatenate([optimized_route, np.zeros(padding_length, dtype=int)])

# solution_1.assigned_ordered_matrix[0, 0] = final_route


(OBJ_tot_dist_optimized) = calculate_tot_dist(n_vehicles, n_days, solution_1.route_dist_matrix, solution_1.OBJ_tot_dist)
print(solution_0.OBJ_tot_dist)
print(OBJ_tot_dist_optimized)

