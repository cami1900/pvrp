import numpy as np
import matplotlib.pyplot as plt
import copy
import random
import random2
import algorithms.VND
import algorithms.VND_backup
import algorithms.assign_route
import algorithms.feasibility_function_POOP
import utils
import algorithms
import classes




def main():

    '''DATA PREPARATION'''

    # # file_path = "data/p0_trial.txt"
    # file_index = 2
    file_path = f"vrp_data/p02.txt"
    distance_type = 1

    (n_vehicles, n_days, vehicle_capacity, data, sorted_data, n_clients, max_clients_kd, distance_matrix, distance_matrix_adjusted, closeness_matrix) = \
        utils.data_preparation(file_path, distance_type)



    '''INITIAL SOLUTION'''
    seed = 42 
    random.seed(seed)
    np.random.seed(seed)
    random2.seed(seed)
    
    # solution_0 = algorithms.assign_route.assign_to_1_vehicle_algorithm(
    #         n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, sorted_data, distance_matrix, closeness_matrix
    #     )
    solution_0 = algorithms.assign_route.assign_to_1_vehicle_algorithm(
        n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, sorted_data, distance_matrix, distance_matrix_adjusted, closeness_matrix
    )
    # solution_0.print()

    V_distances_matrix, V_loads_matrix, solution_0 = algorithms.feasibility_function_POOP.check_feasibility_1vehicle(
        n_vehicles, n_days, n_clients, data, max_clients_kd, vehicle_capacity, distance_matrix, 
        solution_0)    
    solution_0.feasibility_vector.print()
    solution_0.verification_vector.print()


    '''VND ALGORITHM'''

    current_solution = copy.deepcopy(solution_0)

    max_neighbour = 4
    # max_iteration_neigh = 500
    max_iteration_vector = np.array([0, 0, 500, 500, 0])
    time_limit_VND = 7200   # 2h*60min*60sec = 7200sec
    time_limit_neigh = 7200  # 12min*60 sec = 900sec (=1/10)
    two_opt_iteration = 500

    
    (new_vnd_best_solution, new_sol_per_neigh, number_iterations_vector, time_vector) = algorithms.VND.VND_algorithm_condensed(n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, data, sorted_data, distance_matrix, distance_matrix_adjusted, closeness_matrix, 
                                                               current_solution, max_neighbour, max_iteration_vector, time_limit_VND, time_limit_neigh, two_opt_iteration)

    # tipe_per_iteration = time_vector/number_iterations_vector
    tipe_per_iteration = np.zeros(max_neighbour+1, dtype=float)
    print(tipe_per_iteration)
    for neigh in range(max_neighbour+1):
        if number_iterations_vector[neigh] != 0:
            tipe_per_iteration[neigh] = time_vector[neigh]/number_iterations_vector[neigh]

    new_vnd_best_solution.print()
    print("\nnew_sol_per_neigh", new_sol_per_neigh)
    print("\nnumber_iterations_vector", number_iterations_vector)
    print("\ntime_vector", time_vector)
    print("\ntipe_per_iteration", tipe_per_iteration)
    print("\n\n")



    ''' PLOTS '''
    # utils.plot_manhattan_vehicles_routes(n_vehicles, n_days, data, assigned_ordered_matrix)
    utils.plot_euclidean_vehicles_routes(n_vehicles, n_days, data, solution_0.assigned_ordered_matrix)
    utils.plot_euclidean_vehicles_routes(n_vehicles, n_days, data, new_vnd_best_solution.assigned_ordered_matrix)

    # # utils.plot_group_clients(n_vehicles, n_days, data, solution_0.assigned_ordered_matrix, centroids, radii)

    plt.show()
    # # return


if __name__ == "__main__":
    main()