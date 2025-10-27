from py2opt.routefinder import RouteFinder
from py2opt142.py2opt.routefinder import RouteFinder

import algorithms.assign_route
import utils
import algorithms
import conf
import numpy as np
import copy
import matplotlib.pyplot as plt


# cities_names = ['A', 'B', 'C', 'D']
# print(f"\n {type(cities_names)} \n")
# dist_mat = [[0, 70, 15, 35], [70, 0, 57, 42], [15, 57, 0, 61], [35, 42, 61, 0]]
# route_finder = RouteFinder(dist_mat, cities_names, iterations=5)
# best_distance, best_route = route_finder.solve()

# print(best_distance)
# print(best_route)



'''DATA PREPARATION'''

# file_path = "data/p0_trial.txt"
file_index = 2
file_path = f"data/p02.txt"
distance_type = 1

(n_vehicles, n_days, vehicle_capacity, data, sorted_data, n_clients, max_clients_kd, distance_matrix, closeness_matrix) = \
    utils.data_preparation(file_path, distance_type)

''' test '''
# all_clients = data[:, conf.CLIENT_ID_INDEX]
# print(all_clients)

# all_clients = list(str(int(x)) for x in all_clients)
# print(all_clients)
# print(type(all_clients))


# new_routes = RouteFinder(distance_matrix, all_clients, iterations=7)

# best_distance, best_route = new_routes.solve()

# print(best_distance)
# print(best_route)

# int_array = np.array(best_route, dtype=int)
# print(int_array)
# sort_check = np.sort(int_array)
# print(sort_check)

'''INITIAL SOLUTION'''

solution_0 = algorithms.assign_route.assign_to_1_vehicle_algorithm(
        n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, sorted_data, distance_matrix, closeness_matrix
    )
# solution_0.print()

all_clients = copy.copy(solution_0.assigned_ordered_matrix[0, 0])
number_clients = len((np.nonzero(all_clients))[0])
route_clients = all_clients[0: (number_clients+2)]
print(all_clients)

route_clients_str = list(str(int(x)) for x in route_clients)
print(route_clients_str)
print(type(route_clients_str))

distance_matrix_route = np.zeros((len(route_clients)-1, len(route_clients)-1), dtype=float)
for i in range(len(route_clients)-1):
    for j in range(len(route_clients)-1):
        distance_matrix_route[i, j] = distance_matrix[route_clients[i], route_clients[j]]

print(distance_matrix_route)

new_routes = RouteFinder(distance_matrix_route, route_clients_str, iterations=7)

best_distance, best_route = new_routes.solve()

print(best_distance)
print(best_route)

int_array = np.array(best_route, dtype=int)
print(int_array)
sort_check = np.sort(int_array)
print(sort_check)

new_assigned_ordered_matrix = copy.copy(solution_0.assigned_ordered_matrix)
new_assigned_ordered_matrix[0, 0][0:(number_clients+2)] = best_route
new_assigned_ordered_matrix[0, 1][0:(number_clients+2)] = best_route
new_assigned_ordered_matrix[0, 2][0:(number_clients+2)] = best_route
new_assigned_ordered_matrix[0, 3][0:(number_clients+2)] = best_route
new_assigned_ordered_matrix[0, 4][0:(number_clients+2)] = best_route

solution_1 = copy.deepcopy(solution_0)
solution_1.assigned_ordered_matrix = new_assigned_ordered_matrix



''' PLOTS '''

utils.plot_euclidean_vehicles_routes(n_vehicles, n_days, data, solution_0.assigned_ordered_matrix)
utils.plot_euclidean_vehicles_routes(n_vehicles, n_days, data, solution_1.assigned_ordered_matrix)

# utils.plot_group_clients(n_vehicles, n_days, data, solution_0.assigned_ordered_matrix, centroids, radii)

plt.show()

