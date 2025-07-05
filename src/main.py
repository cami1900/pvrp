import numpy as np
import matplotlib.pyplot as plt
import itertools
import random
import algorithms.assign_route
import algorithms.feasibility_function
import algorithms.feasibility_function_POOP
import utils
import algorithms
import time


def main():

    ''' USER INTERFACE -------------------------------------------------------------------------------------------------------'''
    
    file_path = "data/p02.txt"     # type name of file, ex: p02.txt
    distance_type = 1       # select: Euclidean = 1, Manhattan = 2
    
    '''-----------------------------------------------------------------------------------------------------------------------'''
    


    ''' DATA PREPARATION '''
    (n_vehicles, n_days, vehicle_capacity, data, sorted_data, n_clients, max_clients_kd, distance_matrix, closeness_matrix) = \
        utils.data_preparation(file_path, distance_type)



    ''' ALGORITHM '''
    start_time_TOT = time.process_time()

    solution_0 = algorithms.assign_route.assign_to_1_vehicle_algorithm(
            n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, sorted_data, distance_matrix, closeness_matrix
        )
    print("\nAlgorithm time [seconds]", time.process_time() - start_time_TOT)

    if distance_type == 2:
        euclidean_distance_matrix = utils.euclidean_distance_calculator(data)
        total_euclidean_distance = utils.tot_euclidean_distance(solution_0.assigned_ordered_matrix, euclidean_distance_matrix)
        print("\nEquivalent total Euclidean distance:", total_euclidean_distance)
    
    # BASE SOLUTION
    solution_0.print()



    ''' CLUSTERS '''
    # Calculate centroid and radius of each group of customers
    centroids, radii = utils.calculate_grups_data(
        n_vehicles, n_days, data, solution_0.assigned_ordered_matrix, radius_mode='mean_dist', fixed_radius=10)
    # print("centroids:", centroids)
    # print("radius:", radii)
    # print("\n\n")



    ''' FEASIBILITY FUNCTION '''
    # routes_matrix, sub_routes_matrix, summed_powers, V_distances_matrix, V_loads_matrix = \
    #     algorithms.feasibility_function.check_feasibility_1vehicle(
    #         n_vehicles, n_days, n_clients, data, max_clients_kd, vehicle_capacity, solution_0.assigned_ordered_matrix,
    #           distance_matrix, solution_0.route_dist_matrix, solution_0.transp_demand_matrix
    #         )
    
    V_distances_matrix, V_loads_matrix, solution_0 = algorithms.feasibility_function_POOP.check_feasibility_1vehicle(
        n_vehicles, n_days, n_clients, data, max_clients_kd, vehicle_capacity, distance_matrix, solution_0)
    solution_0.feasibility_vector.print()
    solution_0.verification_vector.print()
    print("\n verify distances:\n", V_distances_matrix)
    print("\n verify loads:\n", V_loads_matrix)
    


    ''' PLOTS '''
    # utils.plot_manhattan_vehicles_routes(n_vehicles, n_days, data, assigned_ordered_matrix)
    utils.plot_euclidean_vehicles_routes(n_vehicles, n_days, data, solution_0.assigned_ordered_matrix)

    utils.plot_group_clients(n_vehicles, n_days, data, solution_0.assigned_ordered_matrix, centroids, radii)

    plt.show()
    # return

if __name__ == "__main__":
    main()
