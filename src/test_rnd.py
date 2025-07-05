import random
import numpy as np
import algorithms.assign_route
import utils
import conf
import algorithms
import copy


# def fun1(seed):
#     x = random.random()
#     y = random.random()
#     return x, y


# def fun2(seed):
#     x = random.random()
#     y = random.random()
#     return x, y



# if __name__ == "__main__":
#     seed = 5

#     random.seed(seed)

#     x, y = fun1(seed)
#     print(f"x: {x}")
#     print(f"y: {y}")


#     x, y = fun2(seed)
#     print(f"x: {x}")
#     print(f"y: {y}")

'''-------------------------------------------------------------------------------------------------------------------------'''

# array = np.random.choice(np.arange(10, dtype=np.int32), size=(5, 5), replace=True)
# count = np.count_nonzero(array == 6)

# print(array)
# print(count)

'''-------------------------------------------------------------------------------------------------------------------------'''

# file_path = "data/p02.txt"
# distance_type = 1

# (n_vehicles, n_days, vehicle_capacity, data, sorted_data, n_clients, max_clients_kd, distance_matrix, closeness_matrix) = \
#     utils.data_preparation(file_path, distance_type)

# client = 11
# freq_required = data[client, conf.FREQ_VISIT_INDEX]
# clients_sorted_ndex = [np.where((sorted_data[:, conf.FREQ_VISIT_INDEX] == freq_required) )][0][0]
# clients_same_freq = sorted_data[clients_sorted_ndex, conf.CLIENT_ID_INDEX]

# print("\n\n", clients_same_freq)

'''-------------------------------------------------------------------------------------------------------------------------'''

# my_array = np.array([1, 2, 3, 4, 5])

# def check_notwo(my_array, number):
#     if my_array[number] == 2:

#         return False
#     print("ok", number)
#     return number, True

# for number in range(len(my_array)):
#     if not check_notwo(my_array, number):
#         continue
#     print("value", my_array[number])

'''-------------------------------------------------------------------------------------------------------------------------'''

file_path = "data/p04.txt"
distance_type = 1

(n_vehicles, n_days, vehicle_capacity, data, sorted_data, n_clients, max_clients_kd, distance_matrix, closeness_matrix) = \
    utils.data_preparation(file_path, distance_type)
solution_0 = algorithms.assign_route.assign_to_1_vehicle_algorithm(
            n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, sorted_data, distance_matrix, closeness_matrix
        )
    
solution_0.print()
current_solution = copy.copy(solution_0)


# route = [0, 1, 2, 3, 4, 5, 6]

# for i in range(0, len(route)-2):
#     for j in range(i+2, len(route)-1):
#         new_route = route[:]
#         # print(new_route[i:j])   # stops at j-1 (j NOT included)
#         print("\n\n")
#         print(i, j)
#         new_route[i+1:j+1] = route[j:i:-1]  # stops at i (i-1 NOT included)
#         print(new_route)

# for i in range(0, len(route)-2):
#     print(i)

route = solution_0.assigned_ordered_matrix[0][0]
clients_route = len((np.nonzero(route))[0])

route = route[0:(clients_route+2)]


best = route
cost_best = solution_0.route_dist_matrix[0][0]
improved = True
while improved:
    improved = False
    for i in range(0, len(route)-2):
        for j in range(i+2, len(route)-1):
            # if j-i == 1: continue # changes nothing, skip then
            new_route = route[:]
            new_route[i+1:j+1] = route[j:i:-1] # this is the 2woptSwap
            print("new_route", new_route)
            # new_cost = distance_matrix
            new_cost = sum(distance_matrix[route[i], route[i + 1]] for i in range(len(route) - 1))
            if new_cost < cost_best:  # what should cost be?
                    best = new_route
                    cost_best = new_cost
                    improved = True
                    print("new_cost", new_cost)
    route = best


