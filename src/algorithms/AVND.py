import time
import numpy as np
import random
import copy

import algorithms.VND as VND_funct
import algorithms


def AVND_algorithm(
        n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, data, sorted_data, distance_matrix, distance_matrix_adjusted, closeness_matrix, 
        current_solution, best_solution, 
        time_limit_VND, 
        neigh_order, max_neighbour, max_iteration_neigh, ws_counter_limit, 
        worse_sol_percentage, 
        initial_score, rewards_values):
    
    ''' STEP 0: prepare parameters -------------------------------------------------------------------------------------------------------------------------------'''
    
    # filter clients with non-maximum frequency
    clients_NO_max_frequ = 0

    # initialise parameters
    neighbour = 0   # or initial_neighbour (input)
    iteration = 0
    ws_counter = 0

    # store data
    new_sol_per_neigh = np.zeros((max_neighbour+1), dtype=int)
    number_iterations_vector = np.zeros(max_neighbour+1, dtype=int)
    time_vector = np.zeros(max_neighbour+1, dtype=float)
    solution_history = []

    # algorithm
    score_neigh = np.zeros((max_neighbour+1), dtype=float)
    probability_neigh = np.zeros((max_neighbour+1), dtype=float)
    for neigh in range(len(score_neigh)):
        score_neigh[neigh] = initial_score
        probability_neigh[neigh] = 1/(max_neighbour+1)
    
    # time
    start_time_VND = time.process_time()
    start_time_neigh = time.process_time()


    ''' VND ALGORITHM: -------------------------------------------------------------------------------------------------------------------------------------------'''

    while (time.process_time() - start_time_VND) < time_limit_VND:


        ''' choose neighborhood '''
        neighbour = choose_neigh(probability_neigh, neigh_order)


        ''' run neighborhood '''
        iteration = 0
        ws_counter = 0
        total_run = 0
        reward_points = 0
        

        while iteration <= max_iteration_neigh:

            # print(neigh_order[neighbour], iteration)

            ''' new solution (NS) ''' 
            (initial_comb, final_comb, new_solution, error_index) = \
                VND_funct.define_neighboring_solution(
                    n_vehicles, n_days, vehicle_capacity, data, sorted_data, distance_matrix, closeness_matrix, 
                    copy.deepcopy(current_solution), neigh_order, neighbour, clients_NO_max_frequ) # ho rimosso clients_NO_max_frequ
            if error_index == False:    # solution has not been defined
                    continue
            
            ''' feasibility check '''
            # verify is new solution is feasible
            V_distances_matrix, V_loads_matrix, new_solution = \
                algorithms.feasibility_function_POOP.check_feasibility_pvrp(
                    n_vehicles, n_days, n_clients, data, max_clients_kd, vehicle_capacity, distance_matrix, new_solution)
            if new_solution.feasibility_vector.verify() == True:

                ''' verify NS status '''
                # if NS is better than BS (0):
                if new_solution.OBJ_tot_dist < best_solution.OBJ_tot_dist: 
                    # print("NS is better than BS")

                    # udate best solution
                    best_solution = copy.deepcopy(new_solution)
                    current_solution = copy.deepcopy(new_solution)

                    # save data in counter
                    new_sol_per_neigh[neighbour] += 1

                    # update parameters
                    reward_points += rewards_values[0]
                    iteration = max_iteration_neigh+1
                    total_run += 1

                # if NS in better than CS (1):
                elif new_solution.OBJ_tot_dist < current_solution.OBJ_tot_dist: 
                    # print("NS is better than CS")

                    # udate current solution
                    current_solution = copy.deepcopy(new_solution)

                    # save data in counter
                    new_sol_per_neigh[neighbour] += 1

                    # update parameters
                    reward_points += rewards_values[1]
                    iteration = max_iteration_neigh+1
                    total_run += 1

                elif ws_counter == ws_counter_limit:
                    OBJ_limit_value = (current_solution.OBJ_tot_dist + worse_sol_percentage * current_solution.OBJ_tot_dist)
                    # print("NS is accepted")

                    # if NS is accepted (2):
                    if new_solution.OBJ_tot_dist < OBJ_limit_value:   

                        # udate current solution
                        current_solution = copy.deepcopy(new_solution)

                        # update parameters
                        reward_points += rewards_values[2]
                        iteration += 1
                        ws_counter = 0
                        total_run += 1
                
                else:
                    # print("NS is discarted")
                    # update parameters
                    reward_points += rewards_values[3]
                    iteration += 1
                    ws_counter += 1
                    total_run += 1

            else:
                # print("NS is not feasible")
                # update parameters
                reward_points += rewards_values[3]
                iteration += 1
                ws_counter += 1
                total_run += 1


        ''' update scores '''
        actual_score = copy.copy(score_neigh[neighbour])
        # print(actual_score, reward_points, total_run)
        score_neigh[neighbour] = actual_score + ((reward_points - actual_score) / total_run)
        # print(score_neigh[neighbour])
        score_neigh[neighbour] = max(score_neigh[neighbour], 0.001)
        # print(score_neigh[neighbour])


        ''' update solution history '''
        elapsed_time = time.process_time() - start_time_VND

        solution_history.append((
            best_solution.OBJ_tot_dist,
            current_solution.OBJ_tot_dist,
            neigh_order[neighbour],
            total_run,
            elapsed_time,
            *score_neigh
        ))


        ''' update probabilities '''
        total_scores = 0
        print(f"score_neigh: {score_neigh}")
        for neigh in range(len(score_neigh)):
            total_scores += score_neigh[neigh]
        for neigh in range(len(probability_neigh)):
            # print(f"***** {neigh} *****")
            # print(f"score_neigh[neigh]: {score_neigh[neigh]}")
            # print(f"total_scores: {total_scores}")
            # print("")
            probability_neigh[neigh] = score_neigh[neigh] / total_scores
            # time.sleep(1)
                        

    return (best_solution, solution_history)



def choose_neigh(probability_neigh, neigh_order):

    neighbour = 0
    random_value = random.uniform(0, 1)
    probability_value = 0
    for neigh in range(len(probability_neigh)):
        probability_value += probability_neigh[neigh]
        if random_value <= probability_value:
            neighbour = neigh
            break

    return neighbour