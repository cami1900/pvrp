import numpy as np
import matplotlib.pyplot as plt
import itertools
import random
import random2
import copy
import time

import algorithms.VND
import algorithms.assign_route
import algorithms.feasibility_function_POOP
import utils
import algorithms


def main():

    ''' USER INTERFACE -------------------------------------------------------------------------------------------------------'''
    
    file_path = "vrp_data/p12.txt"     # type name of file, ex: p02.txt
    distance_type = 1       # select: Euclidean = 1, Manhattan = 2

    filename = "out/results/vrp_tests/p12_1_999_3600.xlsx"
    imgname = "out/results/vrp_tests/p12_1_999_3600.png"

    # VND parameters
    repetitions_VND = [1, 0]    # first value indicate repetitons where worse solution is accepted (True), the second where False 
    time_limit_VND = 3600   # 2h*60min*60sec = 7200sec
    time_limit_neigh = 7200  # not used

    # neigh_order = ["move_kt", "t_swap_k", "f_swap_kt"]
    neigh_order = ["move_kt", "t_swap_k", "f_swap_kt"]

    # initial_neigh_VND = [0, worse_sol_neigh, worse_sol_neigh]
    max_neighbour = (len(neigh_order) -1)
    max_iteration_neigh = 500

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
   


    
    '''-----------------------------------------------------------------------------------------------------------------------'''
    
    seed = 42 
    random.seed(seed)
    np.random.seed(seed)
    random2.seed(seed)

    
    # start_time = time.process_time()

    '''DATA PREPARATION'''
    distance_type = 1
    (n_vehicles, n_days, vehicle_capacity, data, sorted_data, n_clients, max_clients_kd, distance_matrix, distance_matrix_adjusted, closeness_matrix) = \
        utils.data_preparation(file_path, distance_type)
    
    '''INITIAL SOLUTION'''
    solution_0 = algorithms.assign_route.assign_to_1_vehicle_algorithm(
        n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, sorted_data, distance_matrix, distance_matrix_adjusted, closeness_matrix)
    
    # check fesibility
    V_distances_matrix, V_loads_matrix, solution_0 = algorithms.feasibility_function_POOP.check_feasibility_1vehicle(
        n_vehicles, n_days, n_clients, data, max_clients_kd, vehicle_capacity, distance_matrix, 
        solution_0)    
    if np.any(solution_0.feasibility_vector) != 1 or np.any(solution_0.verification_vector) != 1:
        return f"Instance p02 - Soluzione iniziale non fattibile.\n"

   
   
    '''VND ALGORITHM'''
    
    current_solution = copy.deepcopy(solution_0)
    all_best_solutions_VND = np.zeros((len(worse_sol_acc_VND)+1), dtype=float)
    all_best_solutions_VND[0] = solution_0.OBJ_tot_dist
    best_solution = copy.deepcopy(solution_0)
    best_solution_OBJ = solution_0.OBJ_tot_dist
    all_solutions_VND = []
    all_solutions_VND.append(float(current_solution.OBJ_tot_dist))
    number_new_sol = 0
    tot_iteration_VND = 0

    start_time_VND = time.process_time()

    for repetition in range(len(worse_sol_acc_VND)):
        print(f"repetition {repetition}")
        # value_SEED = 0
        # random.seed(value_SEED)

        worse_sol_acceptance = worse_sol_acc_VND[repetition]
        initial_neighbour = 0

        ''' time exceeds time_limit_VND: break VND'''
        if (time.process_time() - start_time_VND) > time_limit_VND:
            repetition = len(worse_sol_acc_VND) + 1
            break

        (new_solution, new_sol_per_neigh, number_iterations_vector, time_vector, all_solutions_repetition) = algorithms.VND.VND_algorithm_condensed2_vrp(
            n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, data, sorted_data, distance_matrix, distance_matrix_adjusted, closeness_matrix, 
            current_solution, repetition,
            time_limit_VND, time_limit_neigh,
            neigh_order, initial_neighbour, max_neighbour, max_iteration_neigh, 
            two_opt_iteration, 
            worse_sol_acceptance, worse_sol_percentage)
        
        all_best_solutions_VND[repetition+1] = new_solution.OBJ_tot_dist
        if new_solution.OBJ_tot_dist < best_solution_OBJ:
            best_solution = copy.deepcopy(new_solution)
            best_solution_OBJ = new_solution.OBJ_tot_dist

        all_solutions_VND.append(all_solutions_repetition)
        # for sol in range(len(all_solutions_repetition)):
        #     solution_OBJ = all_solutions_repetition[sol]
        #     all_solutions_VND.append(float(solution_OBJ))

        add_new_sol = new_sol_per_neigh[0] + new_sol_per_neigh[1]
        number_new_sol += add_new_sol
        # print("number_new_sol", add_new_sol, len(all_solutions_repetition))

        for neigh in range(len(number_iterations_vector)):
            tot_iteration_VND += number_iterations_vector[neigh]
        
        current_solution = copy.deepcopy(new_solution)

        print("new_sol_per_neigh", new_sol_per_neigh)


    ''' RESULTS '''

    total_time_VND = time.process_time() - start_time_VND
    print("total_time", total_time_VND)

    # print("all_best_solutions_VND", all_best_solutions_VND)
    print("best_solution_OBJ", best_solution_OBJ)
    # print("best solution")
    # best_solution.print()
    print("\n\n")

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
