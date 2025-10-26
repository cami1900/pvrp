
# LIBRARIES
import random
import copy
import numpy as np
import time

# FILES
import classes
import algorithms
import algorithms.VND as VND_funct
import conf



''' A-VND '''


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
    best_sol_per_neigh = np.zeros((max_neighbour+1), dtype=int)
    neigh_out_parameters = np.zeros((7, max_neighbour+1), dtype=float)
    time_vector = np.zeros(max_neighbour+1, dtype=float)
    solution_history = []

    # algorithm
    score_neigh = np.zeros((max_neighbour+1), dtype=float)
    probability_neigh = np.zeros((max_neighbour+1), dtype=float)
    for neigh in range(len(score_neigh)):
        score_neigh[neigh] = initial_score
        probability_neigh[neigh] = 1/(max_neighbour+1)
    if n_vehicles == 1:
        for neigh in range(len(score_neigh)):
            if (neigh_order[neigh] == "t_move_k" or
                neigh_order[neigh] == "move_kt" or
                neigh_order[neigh] == "t_swap_k" or
                neigh_order[neigh] == "f_swap_kt" or
                neigh_order[neigh] == "swap_kt" ):
                score_neigh[neigh] = 0
    
    # time
    start_time_VND = time.process_time()
    start_time_neigh = time.process_time()

    # save initial data
    solution_history.append((
    best_solution.OBJ_tot_dist,
    current_solution.OBJ_tot_dist,
    0,
    0,
    0,
    *score_neigh
    ))


    ''' VND ALGORITHM: -------------------------------------------------------------------------------------------------------------------------------------------'''

    # print("\n START ALGORITHM A-VND")

    while (time.process_time() - start_time_VND) < time_limit_VND:

        ''' choose neighborhood '''
        neighbour = choose_neigh(probability_neigh, neigh_order)
        # print("neighbour", neighbour)

        ''' run neighborhood '''
        iteration = 0
        ws_counter = 0
        total_run = 0
        reward_points = 0
        # attualmente "iteration" e "total_run" sono equivalenti
        # se si volesse rimanere dentro il neighborhood e azzerare le iterations, allora avranno valori differenti
        

        while iteration <= max_iteration_neigh:
            # print(f"\nneighbour: {neighbour}, iteration: {iteration}")

            # define_neighboring_solution(neighbour, n_vehicles, n_days, vehicle_capacity, data, sorted_data, distance_matrix, closeness_matrix, 
            # current_solution, neigh_order, clients_NO_max_frequ)
            ''' new solution (NS) ''' 
            (initial_comb, final_comb, new_solution, error_index) = \
                define_neighboring_solution(
                    neighbour, 
                    n_vehicles, n_days, vehicle_capacity, data, sorted_data, distance_matrix, closeness_matrix, 
                    current_solution, neigh_order, clients_NO_max_frequ) # ho rimosso clients_NO_max_frequ
            
            if error_index == False:    # solution has not been defined
                    reward_points += rewards_values[3]
                    iteration += 1
                    ws_counter += 1
                    total_run += 1
                    # print("NO feasible solution determined")
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
                    # print("NS is better than BS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    # print(f"best_sol_OBJ: {best_solution.OBJ_tot_dist} < new_sol_OBJ : {new_solution.OBJ_tot_dist}")

                    # udate best solution
                    best_solution = copy.deepcopy(new_solution)
                    current_solution = copy.deepcopy(new_solution)

                    # save data in counter
                    new_sol_per_neigh[neighbour] += 1
                    best_sol_per_neigh[neighbour] += 1

                    # update parameters
                    reward_points += rewards_values[0]
                    # iteration = max_iteration_neigh + 1
                    iteration += 1
                    total_run += 1

                # if NS in better than CS (1):
                elif new_solution.OBJ_tot_dist < current_solution.OBJ_tot_dist: 
                    # print("NS is better than CS +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                    # print(f"curr_sol_OBJ: {current_solution.OBJ_tot_dist} > new_sol_OBJ : {new_solution.OBJ_tot_dist}")

                    # udate current solution
                    current_solution = copy.deepcopy(new_solution)

                    # save data in counter
                    new_sol_per_neigh[neighbour] += 1

                    # update parameters
                    reward_points += rewards_values[1]
                    # iteration = max_iteration_neigh + 1
                    iteration += 1
                    total_run += 1

                elif ws_counter == ws_counter_limit:
                    OBJ_limit_value = (current_solution.OBJ_tot_dist * (1 + worse_sol_percentage))
                    # print("NS is accepted --------------------------------------------------------------------------------")
                    # print(f"curr_sol_OBJ: {current_solution.OBJ_tot_dist} < new_sol_OBJ : {new_solution.OBJ_tot_dist}")

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
                # if not new_solution.feasibility_vector.constr_1:
                #     raise ValueError("❌ Primo vincolo di fattibilità violato: arresto calcolo. ---------------------------------------------------")

                # print(f"NS is not feasible")

                # new_solution.feasibility_vector.print()
                # print("ROUTES MATRIX:", new_solution.assigned_ordered_matrix)
                # print(f"initial_combos \ncomb_1: c{initial_comb.comb_1.client} v{initial_comb.comb_1.vehicle}, d{initial_comb.comb_1.day} \ncomb_2: c{initial_comb.comb_2.client} v{initial_comb.comb_2.vehicle}, d{initial_comb.comb_2.day}")
                # print(f"final_combos \ncomb_1: c{initial_comb.comb_1.client} v{final_comb.comb_1.vehicle}, d{final_comb.comb_1.day} \ncomb_2: c{initial_comb.comb_2.client} v{final_comb.comb_2.vehicle}, d{final_comb.comb_2.day}")
                # print(new_solution.assigned_ordered_matrix)
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

        ''' save otuput data '''
        neigh_out_parameters[0, neighbour] += iteration
        neigh_out_parameters[1, neighbour] = new_sol_per_neigh[neighbour]
        neigh_out_parameters[2, neighbour] = best_sol_per_neigh[neighbour]
        neigh_out_parameters[3, neighbour] += elapsed_time
        neigh_out_parameters[4, neighbour] = neigh_out_parameters[3, neighbour]/neigh_out_parameters[0, neighbour]
        neigh_out_parameters[5, neighbour] = neigh_out_parameters[1, neighbour]/neigh_out_parameters[0, neighbour]
        neigh_out_parameters[6, neighbour] = neigh_out_parameters[2, neighbour]/neigh_out_parameters[0, neighbour]


        ''' update probabilities '''
        total_scores = 0
        # print(f"score_neigh: {score_neigh}")
        for neigh in range(len(score_neigh)):
            total_scores += score_neigh[neigh]
        for neigh in range(len(probability_neigh)):
            # print(f"***** {neigh} *****")
            # print(f"score_neigh[neigh]: {score_neigh[neigh]}")
            # print(f"total_scores: {total_scores}")
            # print("")
            probability_neigh[neigh] = score_neigh[neigh] / total_scores
            # time.sleep(1)
                        

    return (best_solution, solution_history, neigh_out_parameters)


# FUNCTIONS:

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


''' M-VND '''


def MVND_algorithm(worse_sol_acc_VND, neigh_order, max_neighbour, max_iteration_neigh, two_opt_iteration, worse_sol_percentage,
                   start_time_VND, time_limit_VND, time_limit_neigh,
                   n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, data, sorted_data, distance_matrix, distance_matrix_adjusted, closeness_matrix, 
                   all_best_solutions_VND, all_solutions_VND,
                   current_solution):


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

        (new_solution, new_sol_per_neigh, number_iterations_vector, time_vector, all_solutions_repetition) = VND_algorithm(
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

        add_new_sol = 0 
        for neigh in range(len(new_sol_per_neigh)):
            add_new_sol += new_sol_per_neigh[neigh]
        number_new_sol += add_new_sol
        # add_new_sol = new_sol_per_neigh[0] + new_sol_per_neigh[1]
        # number_new_sol += add_new_sol
        # print("number_new_sol", add_new_sol, len(all_solutions_repetition))

        for neigh in range(len(number_iterations_vector)):
            tot_iteration_VND += number_iterations_vector[neigh]
        
        current_solution = copy.deepcopy(new_solution)

        print("new_sol_per_neigh", new_sol_per_neigh)

    return


''' BASE VND '''


def VND_algorithm(
        n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, data, sorted_data, distance_matrix, distance_matrix_adjusted, closeness_matrix, 
        current_solution, repetition,
        time_limit_VND, time_limit_neigh,
        neigh_order, initial_neighbour, max_neighbour, max_iteration_neigh, 
        two_opt_iteration, 
        worse_sol_acceptance, worse_sol_percentage):
    '''  '''

    # neigh_order = ["move_kt", "f_swap_kt", "swap_kt"]
    # neigh_order = ["move_kt", "f_swap_kt", "t_swap_k"]
    # max_neighbour = 2

    ''' STEP 0: prepare parameters -------------------------------------------------------------------------------------------------------------------------------'''
    
    # filter clients with non-maximum frequency
    clients_NO_max_frequ = 0

    # initialise parameters
    neighbour = initial_neighbour
    iteration = 0
    # value_SEED = 0
    # random.seed(value_SEED)
    start_time_neigh = time.process_time()
    start_time_VND = time.process_time()

    # 2-opt vector: defines in which iterations the 2-opt has to be performed
    two_opt_vector = np.zeros(int(max_iteration_neigh/two_opt_iteration-1), dtype=int)
    multiplier = 1
    for i in range(len(two_opt_vector)):
        two_opt_vector[i] = two_opt_iteration*multiplier
        multiplier += 1

    # store data
    new_sol_per_neigh = np.zeros((max_neighbour+1), dtype=int)
    number_iterations_vector = np.zeros(max_neighbour+1, dtype=int)
    time_vector = np.zeros(max_neighbour+1, dtype=float)
    all_solutions = []
    # all_solutions.append(float(current_solution.OBJ_tot_dist))

    # print("neigh_order:", neigh_order, type(neigh_order))
    # print("neighbour:", neighbour, type(neighbour))
    
    ''' VND ALGORITHM: -------------------------------------------------------------------------------------------------------------------------------------------'''
    while neighbour <= max_neighbour:

        ''' time exceeds time_limit_VND: break VND'''
        if (time.process_time() - start_time_VND) > time_limit_VND:
            neighbour = max_neighbour + 1
            break

        ''' iteration exceeds iteration_limit_neigh: go to next neighbourhood '''
        if iteration >= max_iteration_neigh or (time.process_time() - start_time_neigh) > time_limit_neigh:

            ''' 2-opt between neighbourhoods '''
            # (current_solution.assigned_ordered_matrix, current_solution.route_dist_matrix) = \
            #     algorithms.assign_route.two_opt_route(
            #         n_vehicles, n_days, distance_matrix, distance_matrix_adjusted, current_solution.route_dist_matrix, current_solution.assigned_ordered_matrix)
            
            # save data in counter
            number_iterations_vector[neighbour] += iteration
            time_vector[neighbour] += (time.process_time()- start_time_neigh)

            # go to the next neighbour (reset)
            iteration = 0
            neighbour += 1
            start_time = time.process_time()
            continue

        ''' 2-opt every X iterations'''
        # if np.any(two_opt_vector == iteration):
            # (current_solution.assigned_ordered_matrix, current_solution.route_dist_matrix) = \
            #     algorithms.assign_route.two_opt_route(
            #         n_vehicles, n_days, distance_matrix, distance_matrix_adjusted, current_solution.route_dist_matrix, current_solution.assigned_ordered_matrix)

        ''' new solution ''' 
        # neighbour, n_vehicles, n_days, vehicle_capacity, data, sorted_data, distance_matrix, closeness_matrix, current_solution, neigh_order, clients_NO_max_frequ
        (initial_comb, final_comb, new_solution, error_index) = \
            define_neighboring_solution(
                neighbour,n_vehicles, n_days, vehicle_capacity, data, sorted_data, distance_matrix, closeness_matrix, 
                copy.deepcopy(current_solution), neigh_order, clients_NO_max_frequ) # ho rimosso clients_NO_max_frequ
        if error_index == False:    # solution has not been defined
                continue

        ''' print *********************************************************************************************'''
        print("iteration", iteration)
        # print("initial combination")
        # initial_comb.print()
        # print("final combination")
        # final_comb.print()
        # print("new solution ass_ordered", new_solution.assigned_ordered_matrix)
        # print("new solution OBJ", new_solution.OBJ_tot_dist)
        # new_solution.print()

        ''' worse solution acceptance criteria '''
        # if a worse solution can be accepted:
        ws_neigh = random.randrange(0, max_neighbour+1)
        if worse_sol_acceptance == True and neighbour == ws_neigh:
            OBJ_limit_value = (current_solution.OBJ_tot_dist + worse_sol_percentage * current_solution.OBJ_tot_dist)

            if new_solution.OBJ_tot_dist < OBJ_limit_value:
                # verify is new solution is feasible
                V_distances_matrix, V_loads_matrix, new_solution = \
                    algorithms.feasibility_function_POOP.check_feasibility_pvrp(
                        n_vehicles, n_days, n_clients, data, max_clients_kd, vehicle_capacity, distance_matrix, new_solution)
                
                if new_solution.feasibility_vector.verify() == True:

                    # udate current solution
                    current_solution = copy.deepcopy(new_solution)

                    # save data in counter
                    new_sol_per_neigh[neighbour] += 1
                    number_iterations_vector[neighbour] += iteration
                    time_vector[neighbour] += (time.process_time()- start_time_neigh)

                    number_iteration = 0
                    for neigh in range(len(number_iterations_vector)):
                        number_iteration += number_iterations_vector[neigh]
                    all_solutions.append((int(repetition),  int(number_iteration), float(new_solution.OBJ_tot_dist)))

                    # return to the neighbour 0 (reset)
                    iteration = 0
                    neighbour = 0
                    start_time_neigh = time.process_time()
                    worse_sol_acceptance = False
                    # print("worse solution found", worse_sol_acceptance)
                # else:
                iteration += 1

            else:
                iteration += 1
                continue

            
        ''' better solution acceptance criteria '''
        # if the OBJ of new solution is better than the one of current solution and feasible, update current solution: 
        if new_solution.OBJ_tot_dist < current_solution.OBJ_tot_dist:

            print("better OBJ value found")

            # verify is new solution is feasible
            V_distances_matrix, V_loads_matrix, new_solution = \
                algorithms.feasibility_function_POOP.check_feasibility_pvrp(
                    n_vehicles, n_days, n_clients, data, max_clients_kd, vehicle_capacity, distance_matrix, new_solution)
            
            # if new solution is feasible:
            if new_solution.feasibility_vector.verify() == True:

                print("new solution is feasible")

                # udate current solution
                current_solution = copy.deepcopy(new_solution)
                
                # save data in counter
                new_sol_per_neigh[neighbour] += 1
                number_iterations_vector[neighbour] += iteration
                time_vector[neighbour] += (time.process_time()- start_time_neigh)

                number_iteration = 0
                for neigh in range(len(number_iterations_vector)):
                    number_iteration += number_iterations_vector[neigh]
                all_solutions.append((int(repetition),  int(number_iteration), float(new_solution.OBJ_tot_dist)))

                # return to the neighbour 0 (reset)
                iteration = 0
                neighbour = 0
                start_time_neigh = time.process_time()
            
            # else:
            iteration += 1
            
        else:
            iteration += 1
            continue
    
    return (current_solution, new_sol_per_neigh, number_iterations_vector, time_vector, all_solutions)



''' NEIGHBORHOODS '''

def define_neighboring_solution(neighbour, n_vehicles, n_days, vehicle_capacity, data, sorted_data, distance_matrix, closeness_matrix, current_solution, neigh_order, clients_NO_max_frequ):

    ''' step 1'''
    # define the main combination --> initial_comb, final_comb
    
    (initial_comb_main, error_index) = def_initial_comb(neighbour, n_vehicles, n_days, data, sorted_data, current_solution, neigh_order, clients_NO_max_frequ)
    if error_index == False:
        final_comb_main = 0
        new_solution = 0
        return (initial_comb_main, final_comb_main, new_solution, False)

    final_comb_main = def_final_comb(neighbour, n_vehicles, n_days, neigh_order, initial_comb_main)

    # print("initial combination")
    # initial_comb_main.print()
    # print("final combination")
    # final_comb_main.print()
    
    ''' step 2'''
    # check if there is enough remainig capacity:
        # not feasible
            # -->> return error_index = False (STOP)

    capacity_index = check_capacity_op(vehicle_capacity, data, neighbour, neigh_order, current_solution, initial_comb_main, final_comb_main)
    if capacity_index == False:
        new_solution = 0
        return (initial_comb_main, final_comb_main, new_solution, False)

    # check if the operation is feasible --> new schedule:
        # feasible 
            # -->> perform the operation (END)
        # not feasible 
            # -->> perform the operation, remove linked_com and apply the algorithm

    (schedule_index, possible_schedules, linked_combinations) = check_schedule(n_days, n_vehicles, data, neighbour, neigh_order, current_solution, initial_comb_main, final_comb_main)
    # print("\n\nlinked_combinations: **********************\n", linked_combinations)
    # feasible
    if schedule_index == True:
        new_solution = do_operation(neighbour, neigh_order, n_vehicles, n_days, data, distance_matrix, closeness_matrix, current_solution, initial_comb_main, final_comb_main)
        # print("schedule feasible: OP --> END!")
        return (initial_comb_main, final_comb_main, new_solution, True)
        # (END)

    # unfeasible
    new_solution = do_operation(neighbour, neigh_order, n_vehicles, n_days, data, distance_matrix, closeness_matrix, current_solution, initial_comb_main, final_comb_main)
    # print("schedule unfeasible: OP + algoritmo")
    # print("CURRENT SOLUTION")
    # client_combos = find_client_combos(neigh_order, neighbour, n_days, n_vehicles, data, current_solution, initial_comb_main)
    # print("NEW SOLUTION")
    # client_combos = find_client_combos(neigh_order, neighbour, n_days, n_vehicles, data, new_solution, initial_comb_main)
    # print("linked combintions:", linked_combinations)
    # print(f"{new_solution.assigned_ordered_matrix[initial_comb_main.vehicle, initial_comb_main.day]}")
    
    # print(f"devo rimuovere le linked combinations --> {linked_combinations}")
    new_solution = remove_linked_comb(data, neigh_order, neighbour, initial_comb_main, final_comb_main, new_solution, linked_combinations)
    # print("ho rimosso le linked combinations")
    # client_combos = find_client_combos(neigh_order, neighbour, n_days, n_vehicles, data, new_solution, initial_comb_main)

    ''' step 3 '''
    # apply the algorithm to reassign the linked_comb (goal: respect the schedule)

    ' step 3.1 '
    # given the main_final_comb (main_day = 1, other_days = 0), define possible_schedules
    (possible_schedules, schedule_index) = update_poss_schedules(neigh_order, neighbour, possible_schedules, final_comb_main)

    if schedule_index == False:
        new_solution = 0
        return (initial_comb_main, final_comb_main, new_solution, False)

    # based on possible_schedules, (poss_days, poss_vehicles) define possible_combinations
    (possible_combinations, combination_index) = def_poss_combinations(neigh_order, neighbour, n_days, n_vehicles, final_comb_main, possible_schedules)

    if combination_index == False:
        new_solution = 0
        return (initial_comb_main, final_comb_main, new_solution, False)
    
    ' step 3.2 '
    # for each possible_combinations: check the capacity constraint
        # feasible -->> save combination (day = 1)
    (possible_combinations, combination_index) = check_capacity_comb(neigh_order, neighbour, data, vehicle_capacity, possible_combinations, new_solution, final_comb_main)

    if combination_index == False:
        new_solution = 0
        # print("impossibile trovare new_combos per le linked_combos (capacity)")
        return (initial_comb_main, final_comb_main, new_solution, False)

    ' step 3.3 '
    # given the days == 1, update possible_schedules
    (valid_schedules, schedule_index) = def_valid_schedules(neigh_order, neighbour, n_days, possible_combinations, possible_schedules)

    if schedule_index == False:
        new_solution = 0
        # print("le poss_combos per le linked_combos non rispettano la schedule (schedule)")
        return (initial_comb_main, final_comb_main, new_solution, False)

    # choose a random schedule
    selected_schedule = def_selected_schedule(neigh_order, neighbour, valid_schedules)

    ' step 3.4 '
    # given the schedule, update possible_combinations --> valid_combinations
    # choose randomly a combination for each day of the schedule (!= day_main)
    selected_combinations = def_selected_combinations(neigh_order, neighbour, n_days, selected_schedule, possible_combinations, final_comb_main)
    
    ' step 3.5 '
    # assign client and optimize routes:
    new_solution = complete_new_solution(neigh_order, neighbour, data,  n_vehicles, n_days, distance_matrix, closeness_matrix, new_solution, selected_combinations, linked_combinations, initial_comb_main)
    # print("ho completato la nuova soluzione --> END.")
    # client_combos = find_client_combos(neigh_order, neighbour, n_days, n_vehicles, data, new_solution, initial_comb_main)
    # (END)

    return (initial_comb_main, final_comb_main, new_solution, True)


# MAIN FUNCTIONS


def def_initial_comb(neighbour, n_vehicles, n_days, data, sorted_data, current_solution, neigh_order, clients_NO_max_frequ):

    # pick random vehicle, day, client and define its current schedule
    vehicle_i = random.randint(0, n_vehicles-1)
    day_i = random.randint(0, n_days-1)

    # NEIGHBOUR: 

    ''' MOVE '''
    # k_move_t 
    if neigh_order[neighbour] == "k_move_t":
        (real_client_index, error_index) = pick_client(current_solution, vehicle_i, day_i, 0, 0)

        ## si potrebbe togliere!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        schedule_i = np.zeros(n_days)
        schedule_i[day_i] = 1

        initial_comb_main = classes.Move_combination('initial', vehicle_i, day_i, schedule_i, real_client_index)
        # return initial_comb
    #
    # t_move_k
    if neigh_order[neighbour] == "t_move_k":
        (real_client_index, error_index) = pick_client(current_solution, vehicle_i, day_i, 0, 0)

        ## si potrebbe togliere!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        schedule_i = np.zeros(n_days)
        schedule_i[day_i] = 1

        initial_comb_main = classes.Move_combination('initial', vehicle_i, day_i, schedule_i, real_client_index)
        # return initial_comb
    #
    # move_kt
    if neigh_order[neighbour] == "move_kt":
        (real_client_index, error_index) = pick_client(current_solution, vehicle_i, day_i, 0, 0)

        ## si potrebbe togliere!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        schedule_i = np.zeros(n_days)
        schedule_i[day_i] = 1

        initial_comb_main = classes.Move_combination('initial', vehicle_i, day_i, schedule_i, real_client_index)
        # return initial_comb
        
    ''' SWAP 1x1 '''
    # k_swap_t
    if neigh_order[neighbour] == "k_swap_t":
        # Initial combination 1:
        (real_client_index, error_index) = pick_client(current_solution, vehicle_i, day_i, 0, 0)

        ## si potrebbe togliere!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        schedule_i = np.zeros(n_days)
        schedule_i[day_i] = 1

        initial_comb_1 = classes.Move_combination('initial_1', vehicle_i, day_i, schedule_i, real_client_index)

        # Initial combination 2:
        day_i2 = random.choice([i for i in range(n_days) if i != initial_comb_1.day])
        
        (real_client_index_2, error_index) = pick_client(current_solution, vehicle_i, day_i2, 0, initial_comb_1.client)

        ## si potrebbe togliere!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        schedule_i2 = np.zeros(n_days)
        schedule_i2[day_i2] = 1

        initial_comb_2 = classes.Move_combination('initial_2', vehicle_i, day_i2, schedule_i2, real_client_index_2)

        # Initial combination (comb. 1 and comb.2):
        initial_comb_main = classes.SwapCombination('initial', initial_comb_1, initial_comb_2)
        # return initial_comb
    #
    # t_swap_k
    if neigh_order[neighbour] == "t_swap_k":
        # Initial combination 1:
        (real_client_index, error_index) = pick_client(current_solution, vehicle_i, day_i, 0, 0)

        ## si potrebbe togliere!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        schedule_i = np.zeros(n_days)
        schedule_i[day_i] = 1

        initial_comb_1 = classes.Move_combination('initial_1', vehicle_i, day_i, schedule_i, real_client_index)

        # Initial combination 2:
        vehicle_i2 = random.choice([i for i in range(n_vehicles) if i != initial_comb_1.vehicle])
        
        (real_client_index_2, error_index) = pick_client(current_solution, vehicle_i2, day_i, 0, 0)

        ## si potrebbe togliere!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        schedule_i2 = np.zeros(n_days)
        schedule_i2[day_i] = 1

        initial_comb_2 = classes.Move_combination('initial_2', vehicle_i2, day_i, schedule_i2, real_client_index_2)

        # Initial combination (comb. 1 and comb.2):
        initial_comb_main = classes.SwapCombination('initial', initial_comb_1, initial_comb_2)
        # return initial_comb
    #
    # f_swap_kt
    if neigh_order[neighbour] == "f_swap_kt":
        # Initial combination 1:
        (real_client_index, error_index) = pick_client(current_solution, vehicle_i, day_i, 0, 0) # we are allowed to pick clients with freq = n_days
        
        # si potrebbe togliere!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        schedule_i = np.zeros(n_days)
        schedule_i[day_i] = 1

        initial_comb_1 = classes.Move_combination('initial_1', vehicle_i, day_i, schedule_i, real_client_index)
        
        # Initial combination 2:
        day_i2 = random.choice([i for i in range(n_days) if i != initial_comb_1.day])
        vehicle_i2 = random.choice([i for i in range(n_vehicles) if i != initial_comb_1.vehicle])

        clients_same_freq = filter_clients_same_frequ(data, sorted_data, initial_comb_1)
        (real_client_index_2, error_index) = pick_client(current_solution, vehicle_i2, day_i2, clients_same_freq, initial_comb_1.client)
        if error_index == False:
            initial_comb = 0
            return (initial_comb, False)
        
        ## si potrebbe togliere!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        schedule_i2 = np.zeros(n_days)
        schedule_i2[day_i2] = 1

        initial_comb_2 = classes.Move_combination('initial_2', vehicle_i2, day_i2, schedule_i2, real_client_index_2)

        # Initial combination (comb. 1 and comb.2):
        initial_comb_main = classes.SwapCombination('initial', initial_comb_1, initial_comb_2)
        # return initial_comb
    #
    # swap_kt
    if neigh_order[neighbour] == "swap_kt":
        # Initial combination 1:
        (real_client_index, error_index) = pick_client(current_solution, vehicle_i, day_i, 0, 0) # we are allowed to pick clients with freq = n_days

        ## si potrebbe togliere!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        schedule_i = np.zeros(n_days)
        schedule_i[day_i] = 1

        initial_comb_1 = classes.Move_combination('initial', vehicle_i, day_i, schedule_i, real_client_index)

        # Initial combination 2:
        vehicle_i2 = random.choice([i for i in range(n_vehicles) if i != initial_comb_1.vehicle])
        day_i2 = random.choice([i for i in range(n_days) if i != initial_comb_1.day])

        (real_client_index_2, error_index) = pick_client(current_solution, vehicle_i2, day_i2, 0, initial_comb_1.client)

        ## si potrebbe togliere!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        schedule_i2 = np.zeros(n_days)
        schedule_i2[day_i2] = 1

        initial_comb_2 = classes.Move_combination('initial_2', vehicle_i2, day_i2, schedule_i2, real_client_index_2)

        # Initial combination (comb. 1 and comb.2):
        initial_comb_main = classes.SwapCombination('initial', initial_comb_1, initial_comb_2)
        # return initial_comb
    
    ''' MULTI SWAP '''
    # t_multiswap_k
    if neigh_order[neighbour] == "t_multiswap_k":
        # print("\n\nciao")

        # Initial combination 1:
        (real_client_index_1, number_clients_1, error_index) = pick_set_clients(n_days, data, current_solution, vehicle_i, day_i, 0, 0)
        if error_index == False:
            initial_comb = 0
            return (initial_comb, False)
        schedule_i = np.zeros(n_days)
        schedule_i[day_i] = 1

        initial_comb_1 = classes.Move_combination('initial', vehicle_i, day_i, schedule_i, real_client_index_1)
        
        # Initial combination 2:
        vehicle_i2 = random.choice([i for i in range(n_vehicles) if i != initial_comb_1.vehicle])
        (real_client_index_2, number_clients_2, error_index) = pick_set_clients(n_days, data, current_solution, vehicle_i2, day_i, 0, number_clients_1)
        if error_index == False:
            initial_comb = 0
            return (initial_comb, False)

        initial_comb_2 = classes.Move_combination('initial_2', vehicle_i2, day_i, schedule_i, real_client_index_2)

        # Initial combination (comb. 1 and comb.2):
        initial_comb_main = classes.SwapCombination('initial', initial_comb_1, initial_comb_2)
    
    ''' ROUTE '''
    #

    return (initial_comb_main, True)


def def_final_comb(neighbour, n_vehicles, n_days, neigh_order, initial_comb):

    # NEIGHBOUR: 

    ''' MOVE '''
    # k_move_t 
    if neigh_order[neighbour] == "k_move_t":
        # pick new random day and define client's new schedule
        day_f = random.choice([t for t in range(0, n_days) if t != initial_comb.day])

        ## si potrebbe togliere!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        schedule_f = np.zeros(n_days)
        schedule_f[day_f] = 1

        # Final combination:
        final_comb = classes.Move_combination('final', initial_comb.vehicle, day_f, schedule_f, initial_comb.client)
        # return final_comb
    #
    # t_move_k
    if neigh_order[neighbour] == "t_move_k":
        # pick new random day and define client's new schedule
        vehicle_f = random.choice([t for t in range(0, n_vehicles) if t != initial_comb.vehicle])

        ## si potrebbe togliere!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        schedule_f = np.zeros(n_days)
        schedule_f[initial_comb.day] = 1

        # Initial combination:
        final_comb = classes.Move_combination('final', vehicle_f, initial_comb.day, schedule_f, initial_comb.client)
        # return final_comb
    #
    # move_kt
    if neigh_order[neighbour] == "move_kt":
        # pick a random vehicle and a random day 
        vehicle_f = random.choice([k for k in range(0, n_vehicles) if k != initial_comb.vehicle])
        day_f = random.choice([t for t in range(0, n_days) if t != initial_comb.day])

        ## si potrebbe togliere!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        schedule_f = np.zeros(n_days)
        schedule_f[day_f] = 1

        # define the available days and define client's new schedule
        # available_days = define_available_days(n_days, vehicle_capacity, data, vehicle_f, initial_comb, current_solution.transp_demand_matrix)
        # schedule_f = define_new_schedule_load(n_days, data, available_days, initial_comb.client)

        final_comb = classes.Move_combination('final', vehicle_f, day_f, schedule_f, initial_comb.client)

    ''' SWAP 1x1 '''
    # k_swap_t
    if neigh_order[neighbour] == "k_swap_t":

        # pick a random schedule for comb_1 and comb_2, based on the day of the other client
        # schedule_f1 = define_new_schedule_day(n_days, data, initial_comb.comb_2.day, initial_comb.comb_1.client, initial_comb.comb_1.schedule)
        # schedule_f2 = define_new_schedule_day(n_days, data, initial_comb.comb_1.day, initial_comb.comb_2.client, initial_comb.comb_2.schedule)
        
        # Final combination:
        final_comb_1 = classes.Move_combination('final_1', initial_comb.comb_1.vehicle, initial_comb.comb_2.day, initial_comb.comb_2.schedule, initial_comb.comb_1.client)
        final_comb_2 = classes.Move_combination('final_2', initial_comb.comb_2.vehicle, initial_comb.comb_1.day, initial_comb.comb_1.schedule, initial_comb.comb_2.client)
        final_comb = classes.SwapCombination('final', final_comb_1, final_comb_2)
        # return final_comb
    #
    # t_swap_k
    if neigh_order[neighbour] == "t_swap_k":
        # Final combination:
        final_comb_1 = classes.Move_combination('final_1', initial_comb.comb_2.vehicle, initial_comb.comb_1.day, initial_comb.comb_1.schedule, initial_comb.comb_1.client)
        final_comb_2 = classes.Move_combination('final_2', initial_comb.comb_1.vehicle, initial_comb.comb_2.day, initial_comb.comb_2.schedule, initial_comb.comb_2.client)
        final_comb = classes.SwapCombination('final', final_comb_1, final_comb_2)
        # return final_comb
    #
    # f_swap_kt
    if neigh_order[neighbour] == "f_swap_kt":
        # invert vehicle and schedule (and day) of the two clients
        # Final combination:
        final_comb_1 = classes.Move_combination('final_1', initial_comb.comb_2.vehicle, initial_comb.comb_2.day, initial_comb.comb_2.schedule, initial_comb.comb_1.client)
        final_comb_2 = classes.Move_combination('final_2', initial_comb.comb_1.vehicle, initial_comb.comb_1.day, initial_comb.comb_1.schedule, initial_comb.comb_2.client)
        final_comb = classes.SwapCombination('final', final_comb_1, final_comb_2)
        # return final_comb
    #
    # swap_kt
    if neigh_order[neighbour] == "swap_kt":
        
        
        # remove clients:
        # (new_assigned_ordered_matrix, new_not_assigned_list, new_transp_demand_matrix, new_route_dist_matrix, new_OBJ_tot_dist) = crete_new_sol_attributes(current_solution)
        # for day in range(n_days):
        #     (new_assigned_ordered_matrix, new_transp_demand_matrix) = remove_client(n_days, data, initial_comb.comb_1, 0, new_assigned_ordered_matrix, new_transp_demand_matrix, day)
        #     (new_assigned_ordered_matrix, new_transp_demand_matrix) = remove_client(n_days, data, initial_comb.comb_2, 0, new_assigned_ordered_matrix, new_transp_demand_matrix, day)
        # define the available days based on the other client vehicle and define clients new schedules
        # available_days_1 = define_available_days(n_days, vehicle_capacity, data, initial_comb.comb_2.vehicle, initial_comb.comb_1, new_transp_demand_matrix)
        # available_days_2 = define_available_days(n_days, vehicle_capacity, data, initial_comb.comb_1.vehicle, initial_comb.comb_2, new_transp_demand_matrix)
        # schedule_f1 = define_new_schedule_load(n_days, data, available_days_1, initial_comb.comb_1.client)
        # schedule_f2 = define_new_schedule_load(n_days, data, available_days_2, initial_comb.comb_2.client)

        # Final combination:
        final_comb_1 = classes.Move_combination('final_1', initial_comb.comb_2.vehicle, initial_comb.comb_2.day, initial_comb.comb_2.schedule, initial_comb.comb_1.client)
        final_comb_2 = classes.Move_combination('final_2', initial_comb.comb_1.vehicle, initial_comb.comb_1.day, initial_comb.comb_1.schedule, initial_comb.comb_2.client)
        final_comb = classes.SwapCombination('final', final_comb_1, final_comb_2)
        # final_comb_1.print()
        # final_comb_2.print()
        # return final_comb

    ''' MULTI SWAP '''
    #
    #t_multiswap_k
    if neigh_order[neighbour] == "t_multiswap_k":
        # print("ciao")
        # Final combination:
        final_comb_1 = classes.Move_combination('final_1', initial_comb.comb_2.vehicle, initial_comb.comb_1.day, initial_comb.comb_1.schedule, initial_comb.comb_1.client)
        final_comb_2 = classes.Move_combination('final_2', initial_comb.comb_1.vehicle, initial_comb.comb_2.day, initial_comb.comb_2.schedule, initial_comb.comb_2.client)
        final_comb = classes.SwapCombination('final', final_comb_1, final_comb_2)

    return final_comb


def check_capacity_op(vehicle_capacity, data, neighbour, neigh_order, current_solution, initial_comb_main, final_comb_main):
    
    #    ''' MOVE '''
    if (neigh_order[neighbour] == "k_move_t" or 
        neigh_order[neighbour] == "t_move_k" or
        neigh_order[neighbour] == "move_kt"):
        # if client already assigned, the operation will not be performed
        client_list_final = current_solution.assigned_ordered_matrix[final_comb_main.vehicle, final_comb_main.day]
        if  np.isin(initial_comb_main.client, client_list_final):
            return (False)
        
        new_capacity = (current_solution.transp_demand_matrix[final_comb_main.vehicle, final_comb_main.day] + 
                        data[initial_comb_main.client, conf.DEMAND_INDEX])
        
        if new_capacity > vehicle_capacity:
            return (False)

    #    ''' SWAP 1x1 '''
    elif (neigh_order[neighbour] == "k_swap_t" or 
        neigh_order[neighbour] == "t_swap_k" or
        neigh_order[neighbour] == "f_swap_kt" or
        neigh_order[neighbour] == "swap_kt"):

        new_capacity_1 = (current_solution.transp_demand_matrix[final_comb_main.comb_1.vehicle, final_comb_main.comb_1.day] - 
                        data[initial_comb_main.comb_2.client, conf.DEMAND_INDEX] +
                        data[initial_comb_main.comb_1.client, conf.DEMAND_INDEX])
        
        new_capacity_2 = (current_solution.transp_demand_matrix[final_comb_main.comb_2.vehicle, final_comb_main.comb_2.day] - 
                        data[initial_comb_main.comb_1.client, conf.DEMAND_INDEX] +
                        data[initial_comb_main.comb_2.client, conf.DEMAND_INDEX])
        
        if new_capacity_1 > vehicle_capacity or new_capacity_2 > vehicle_capacity:
            return (False)

    # if neigh_order[neighbour] == "t_multiswap_k"???????????????????

    return(True)
    

def check_schedule(n_days, n_vehicles, data, neighbour, neigh_order, current_solution, initial_comb_main, final_comb_main):
    
    #    ''' MOVE '''
    if (neigh_order[neighbour] == "k_move_t" or 
        neigh_order[neighbour] == "move_kt"):

        possible_schedules = def_possible_schedules(n_days, data, initial_comb_main)
        (new_schedule, linked_combinations) = def_new_schedule(n_days, n_vehicles, data, current_solution, initial_comb_main, final_comb_main)

        if any(np.array_equal(new_schedule, sched) for sched in possible_schedules):
            return (True, possible_schedules, linked_combinations)

    #    ''' SWAP 1x1 '''
    elif (neigh_order[neighbour] == "k_swap_t" or 
          neigh_order[neighbour] == "f_swap_kt" or 
          neigh_order[neighbour] == "swap_kt" ):

        possible_schedules_1 = def_possible_schedules(n_days, data, initial_comb_main.comb_1)
        possible_schedules_2 = def_possible_schedules(n_days, data, initial_comb_main.comb_2)
        possible_schedules = [possible_schedules_1, possible_schedules_2]

        (new_schedule_1, linked_combinations_1) = def_new_schedule(n_days, n_vehicles, data, current_solution, initial_comb_main.comb_1, final_comb_main.comb_1)
        (new_schedule_2, linked_combinations_2) = def_new_schedule(n_days, n_vehicles, data, current_solution, initial_comb_main.comb_2, final_comb_main.comb_2)
        linked_combinations = [linked_combinations_1, linked_combinations_2]

        if (any(np.array_equal(new_schedule_1, sched) for sched in possible_schedules_1) and 
            any(np.array_equal(new_schedule_2, sched) for sched in possible_schedules_2)):
            return (True, possible_schedules, linked_combinations)
        
    # NO schedule breakage
    elif (neigh_order[neighbour] == "t_move_k" or 
          neigh_order[neighbour] == "t_swap_k" or 
          neigh_order[neighbour] == "t_multiswap_k"):
        
        possible_schedules = 0
        linked_combinations = 0
        
        return (True, possible_schedules, linked_combinations)

    return (False, possible_schedules, linked_combinations)


def do_operation(neighbour, neigh_order, n_vehicles, n_days, data, distance_matrix, closeness_matrix, current_solution, initial_comb, final_comb):
    
    #    ''' MOVE '''
    if (neigh_order[neighbour] == "k_move_t" or 
        neigh_order[neighbour] == "t_move_k" or
        neigh_order[neighbour] == "move_kt"):

        # New solution:
        new_solution = move_operation(n_vehicles, n_days, data, distance_matrix, closeness_matrix, current_solution, initial_comb, final_comb)
        

    #    ''' SWAP 1x1 '''
    elif (neigh_order[neighbour] == "k_swap_t" or 
        neigh_order[neighbour] == "t_swap_k" or
        neigh_order[neighbour] == "f_swap_kt" or
        neigh_order[neighbour] == "swap_kt"):

        # New solution:
        new_solution = swap_operation(n_vehicles, n_days, data, distance_matrix, closeness_matrix, current_solution, initial_comb, final_comb)    
        

    # elif neigh_order[neighbour] == "f_swap_kt":

    #     # New solution:
    #     new_solution = swap_operation(n_vehicles, n_days, data, distance_matrix, closeness_matrix, current_solution, initial_comb, final_comb) 
    #     # # Optimize routes:
    #     # (new_solution.route_dist_matrix, new_solution.assigned_ordered_matrix) = optimize_single_route(n_vehicles, n_days, distance_matrix, closeness_matrix, new_solution.route_dist_matrix, new_solution.assigned_ordered_matrix, final_comb.comb_1.vehicle, final_comb.comb_1.day)
    #     # (new_solution.route_dist_matrix, new_solution.assigned_ordered_matrix) = optimize_single_route(n_vehicles, n_days, distance_matrix, closeness_matrix, new_solution.route_dist_matrix, new_solution.assigned_ordered_matrix, final_comb.comb_2.vehicle, final_comb.comb_2.day)

    #     # Move linked combinations:
    #     # identifica dove sono --> lo sai già dal schedule_check
    #     (new_schedule_1, linked_combinations_1) = def_new_schedule(n_days, n_vehicles, data, current_solution, initial_comb.comb_1, final_comb.comb_1)
    #     (new_schedule_2, linked_combinations_2) = def_new_schedule(n_days, n_vehicles, data, current_solution, initial_comb.comb_2, final_comb.comb_2)

    #     if len(linked_combinations_1) != len(linked_combinations_2):
    #         new_solution = 0
    #         error_index = False
    #         return new_solution
            
    #     for comb in range(len(linked_combinations_1)):
            
    #         (vehicle_comb1, day_comb1) = linked_combinations_1[comb]
    #         (vehicle_comb2, day_comb2) = linked_combinations_2[comb]

    #         print(f"comb_1: v{vehicle_comb1}, d{day_comb1}")
    #         print(f"comb_2: v{vehicle_comb2}, d{day_comb2}")

    #         (new_solution.assigned_ordered_matrix, new_solution.transp_demand_matrix) = remove_client_NEW(data, new_solution.assigned_ordered_matrix, new_solution.transp_demand_matrix, 
    #                                                                                     day_comb1, vehicle_comb1, initial_comb.comb_1.client)
    #         (new_solution.assigned_ordered_matrix, new_solution.transp_demand_matrix) = remove_client_NEW(data, new_solution.assigned_ordered_matrix, new_solution.transp_demand_matrix, 
    #                                                                                     day_comb2, vehicle_comb2, initial_comb.comb_2.client)
    #         (new_solution.assigned_ordered_matrix, new_solution.transp_demand_matrix) = add_client_NEW(data, new_solution.assigned_ordered_matrix, new_solution.transp_demand_matrix, 
    #                                                                                     day_comb2, vehicle_comb2, initial_comb.comb_1.client)
    #         (new_solution.assigned_ordered_matrix, new_solution.transp_demand_matrix) = add_client_NEW(data, new_solution.assigned_ordered_matrix, new_solution.transp_demand_matrix, 
    #                                                                                     day_comb1, vehicle_comb1, initial_comb.comb_2.client)
        
    #     # Optimize routes and update distances:
    #     for comb in range(len(linked_combinations_1)):
    #         (vehicle_comb1, day_comb1) = linked_combinations_1[comb]
    #         (vehicle_comb2, day_comb2) = linked_combinations_2[comb]
    #         # Optimize routes:
    #         # (n_vehicles, n_days, distance_matrix, closeness_matrix, new_route_dist_matrix, new_assigned_ordered_matrix, vehicle, day)
    #         (new_solution.route_dist_matrix, new_solution.assigned_ordered_matrix) = optimize_single_route(n_vehicles, n_days, distance_matrix, closeness_matrix, 
    #                                                                                      new_solution.route_dist_matrix, new_solution.assigned_ordered_matrix, 
    #                                                                                      vehicle_comb1, day_comb1)
    #         (new_solution.route_dist_matrix, new_solution.assigned_ordered_matrix) = optimize_single_route(n_vehicles, n_days, distance_matrix, closeness_matrix, 
    #                                                                                      new_solution.route_dist_matrix, new_solution.assigned_ordered_matrix, 
    #                                                                                      vehicle_comb2, day_comb2)


    #     # Update the OBJECTIVE value
    #     new_solution.OBJ_tot_dist = algorithms.assign_route.calculate_tot_dist (n_vehicles, n_days, new_solution.route_dist_matrix, new_solution.OBJ_tot_dist)

    #     # # Save new solution:
    #     # new_solution = classes.Solution(new_OBJ_tot_dist, new_assigned_ordered_matrix, new_not_assigned_list, new_transp_demand_matrix, new_route_dist_matrix)

    #     # new_solution.assigned_ordered_matrix = new_assigned_ordered_matrix
    #     # new_solution.transp_demand_matrix = new_transp_demand_matrix


    return new_solution


def remove_linked_comb(data, neigh_order, neighbour, initial_comb, final_comb, new_solution, linked_combinations):

    new_assigned_ordered_matrix = new_solution.assigned_ordered_matrix
    new_transp_demand_matrix = new_solution.transp_demand_matrix

#    ''' MOVE '''
    if (neigh_order[neighbour] == "k_move_t" or 
        neigh_order[neighbour] == "move_kt"):
        # print("sto rimuovendo le linked combinations...")
        # print("linked_combinations:", linked_combinations)
        # for item in linked_combinations:
        #     print(item, type(item))

        for comb_vehicle, comb_day in linked_combinations:
            # print(f"linked_comb: v{comb_vehicle}, d{comb_day}, c{initial_comb.client}")
            # if comb_vehicle == final_comb.vehicle and comb_day == final_comb.day:
            #     continue
            (new_assigned_ordered_matrix, new_transp_demand_matrix) = remove_client_NEW(data, new_assigned_ordered_matrix, new_transp_demand_matrix, 
                                                                                        comb_day, comb_vehicle, initial_comb.client)
            # print(f"client removed: {new_assigned_ordered_matrix[comb_vehicle, comb_day]}")
    
    #    ''' SWAP 1x1 '''
    elif (neigh_order[neighbour] == "k_swap_t" or
          neigh_order[neighbour] == "f_swap_kt" or 
          neigh_order[neighbour] == "swap_kt"):
        # print(f"client{initial_comb.comb_1.client}, linked_combos: {linked_combinations[0]}")
        # print(f"client{initial_comb.comb_2.client}, linked_combos: {linked_combinations[1]}")
        for comb_vehicle, comb_day in linked_combinations[0]:
            # if comb_vehicle == final_comb.comb_1.vehicle and comb_day == final_comb.comb_1.day:
            #     continue
            (new_assigned_ordered_matrix, new_transp_demand_matrix) = remove_client_NEW(data, new_assigned_ordered_matrix, new_transp_demand_matrix, 
                                                                                        comb_day, comb_vehicle, initial_comb.comb_1.client)
        for comb_vehicle, comb_day in linked_combinations[1]:
            # if comb_vehicle == final_comb.comb_2.vehicle and comb_day == final_comb.comb_2.day:
            #     continue
            (new_assigned_ordered_matrix, new_transp_demand_matrix) = remove_client_NEW(data, new_assigned_ordered_matrix, new_transp_demand_matrix, 
                                                                                        comb_day, comb_vehicle, initial_comb.comb_2.client)

    new_solution.assigned_ordered_matrix = new_assigned_ordered_matrix
    new_solution.transp_demand_matrix = new_transp_demand_matrix

    return new_solution


def update_poss_schedules(neigh_order, neighbour, all_possible_schedules, final_comb):

    #    ''' MOVE '''
    if (neigh_order[neighbour] == "k_move_t" or 
        neigh_order[neighbour] == "move_kt"):

        possible_schedules = find_schedules(all_possible_schedules, final_comb.schedule)

        if not possible_schedules:
            return(possible_schedules, False)

    #    ''' SWAP 1x1 '''
    elif (neigh_order[neighbour] == "k_swap_t" or 
          neigh_order[neighbour] == "f_swap_kt" or 
          neigh_order[neighbour] == "swap_kt" ):

        possible_schedules_1 = find_schedules(all_possible_schedules[0], final_comb.comb_1.schedule)
        possible_schedules_2 = find_schedules(all_possible_schedules[1], final_comb.comb_2.schedule)
        possible_schedules = [possible_schedules_1, possible_schedules_2]
        # print("possible schedules based on chosen day:")
        # print(f"client{final_comb.comb_1.client}, day{final_comb.comb_1.day}-{final_comb.comb_1.schedule}, schedules-->{possible_schedules_1}")
        # print(f"client{final_comb.comb_2.client}, day{final_comb.comb_2.day}, schedules-->{possible_schedules_2}")

        if not possible_schedules_1 or not possible_schedules_2:
            possible_schedules = 0
            return(possible_schedules, False)

    return (possible_schedules, True)


def def_poss_combinations(neigh_order, neighbour, n_days, n_vehicles, final_comb, possible_schedules):

    #    ''' MOVE '''
    if (neigh_order[neighbour] == "k_move_t" or 
        neigh_order[neighbour] == "move_kt"):

        possible_combinations = find_poss_combinations(n_days, n_vehicles, final_comb.day, possible_schedules)

        if not possible_combinations:
            return(possible_combinations, False)

    #    ''' SWAP 1x1 '''
    elif (neigh_order[neighbour] == "k_swap_t" or 
          neigh_order[neighbour] == "f_swap_kt" or 
          neigh_order[neighbour] == "swap_kt" ):

        possible_combinations_1 = find_poss_combinations(n_days, n_vehicles, final_comb.comb_1.day, possible_schedules[0])
        possible_combinations_2 = find_poss_combinations(n_days, n_vehicles, final_comb.comb_2.day, possible_schedules[1])

        possible_combinations = [possible_combinations_1, possible_combinations_2]

        if not possible_combinations_1 or not possible_combinations_2:
            possible_combinations = 0
            return(possible_combinations, False)

    return (possible_combinations, True)


def check_capacity_comb(neigh_order, neighbour, data, vehicle_capacity, all_poss_combinations, new_solution, final_comb):

    #    ''' MOVE '''
    if (neigh_order[neighbour] == "k_move_t" or 
        neigh_order[neighbour] == "move_kt"):

        possible_combinations = find_capacity_comb(data, vehicle_capacity, new_solution, all_poss_combinations, final_comb.client)

        if not possible_combinations:
            possible_combinations = 0
            return(possible_combinations, False)
        
    #    ''' SWAP 1x1 '''
    elif (neigh_order[neighbour] == "k_swap_t" or 
          neigh_order[neighbour] == "f_swap_kt" or 
          neigh_order[neighbour] == "swap_kt" ):

        possible_combinations_1 = find_capacity_comb(data, vehicle_capacity, new_solution, all_poss_combinations[0], final_comb.comb_1.client)
        possible_combinations_2 = find_capacity_comb(data, vehicle_capacity, new_solution, all_poss_combinations[1], final_comb.comb_2.client)

        possible_combinations = [possible_combinations_1, possible_combinations_2]

        if not possible_combinations_1 or not possible_combinations_2:
            possible_combinations = 0
            return(possible_combinations, False)

    return (possible_combinations, True)


def def_valid_schedules(neigh_order, neighbour, n_days, possible_combinations, possible_schedules):

    #    ''' MOVE '''
    if (neigh_order[neighbour] == "k_move_t" or 
        neigh_order[neighbour] == "move_kt"):

        valid_schedules = find_valid_sched(n_days, possible_combinations, possible_schedules)

        if not valid_schedules:
            possible_schedules = 0
            return(valid_schedules, False)

    #    ''' SWAP 1x1 '''
    elif (neigh_order[neighbour] == "k_swap_t" or 
          neigh_order[neighbour] == "f_swap_kt" or 
          neigh_order[neighbour] == "swap_kt" ):

        valid_schedules_1 = find_valid_sched(n_days, possible_combinations[0], possible_schedules[0])
        valid_schedules_2 = find_valid_sched(n_days, possible_combinations[1], possible_schedules[1])

        valid_schedules = [valid_schedules_1, valid_schedules_2]

        if not valid_schedules_1 or not valid_schedules_2:
            possible_schedules = 0
            return(possible_schedules, False)


    return (valid_schedules, True)


def def_selected_schedule(neigh_order, neighbour, valid_schedules):

    #    ''' MOVE '''
    if (neigh_order[neighbour] == "k_move_t" or 
        neigh_order[neighbour] == "move_kt"):

        selected_schedule = random.choice(valid_schedules)

    #    ''' SWAP 1x1 '''
    elif (neigh_order[neighbour] == "k_swap_t" or 
          neigh_order[neighbour] == "f_swap_kt" or 
          neigh_order[neighbour] == "swap_kt" ):

        selected_schedule_1 = random.choice(valid_schedules[0])
        selected_schedule_2 = random.choice(valid_schedules[1])

        selected_schedule = [selected_schedule_1, selected_schedule_2]

    return selected_schedule


def def_selected_combinations(neigh_order, neighbour, n_days, selected_schedule, possible_combinations, final_comb):

    #    ''' MOVE '''
    if (neigh_order[neighbour] == "k_move_t" or 
        neigh_order[neighbour] == "move_kt"):

        selected_combinations = find_choose_linked_comb(n_days, selected_schedule, possible_combinations, final_comb)

    #    ''' SWAP 1x1 '''
    elif (neigh_order[neighbour] == "k_swap_t" or 
          neigh_order[neighbour] == "f_swap_kt" or 
          neigh_order[neighbour] == "swap_kt" ):

        selected_combinations_1 = find_choose_linked_comb(n_days, selected_schedule[0], possible_combinations[0], final_comb.comb_1)
        selected_combinations_2 = find_choose_linked_comb(n_days, selected_schedule[1], possible_combinations[1], final_comb.comb_2)

        selected_combinations = [selected_combinations_1, selected_combinations_2]

    return selected_combinations


def complete_new_solution(neigh_order, neighbour, data, n_vehicles, n_days, distance_matrix, closeness_matrix, new_solution, selected_combinations, linked_combinations, initial_comb):

    new_assigned_ordered_matrix = new_solution.assigned_ordered_matrix
    new_transp_demand_matrix = new_solution.transp_demand_matrix

    #    ''' MOVE '''
    if (neigh_order[neighbour] == "k_move_t" or 
        neigh_order[neighbour] == "move_kt"):

        for comb_vehicle, comb_day in selected_combinations:
            (new_assigned_ordered_matrix, new_transp_demand_matrix) = add_client_NEW(data, new_assigned_ordered_matrix, new_transp_demand_matrix, comb_day, comb_vehicle, initial_comb.client)

    #    ''' SWAP 1x1 '''
    elif (neigh_order[neighbour] == "k_swap_t" or 
          neigh_order[neighbour] == "f_swap_kt" or 
          neigh_order[neighbour] == "swap_kt" ):

        # print(f"selected combos, cl_1:", selected_combinations[0])
        for comb_vehicle, comb_day in selected_combinations[0]:
            (new_assigned_ordered_matrix, new_transp_demand_matrix) = add_client_NEW(data, new_assigned_ordered_matrix, new_transp_demand_matrix, comb_day, comb_vehicle, initial_comb.comb_1.client)

        for comb_vehicle, comb_day in selected_combinations[1]:
            (new_assigned_ordered_matrix, new_transp_demand_matrix) = add_client_NEW(data, new_assigned_ordered_matrix, new_transp_demand_matrix, comb_day, comb_vehicle, initial_comb.comb_2.client)

    new_solution.assigned_ordered_matrix = new_assigned_ordered_matrix
    new_solution.transp_demand_matrix = new_transp_demand_matrix

    # optimize routes:
    #    ''' MOVE '''
    if (neigh_order[neighbour] == "k_move_t" or 
        neigh_order[neighbour] == "move_kt"):
        for comb_vehicle, comb_day in selected_combinations:
            (new_solution.route_dist_matrix, new_solution.assigned_ordered_matrix) = optimize_single_route(n_vehicles, n_days, distance_matrix, closeness_matrix, new_solution.route_dist_matrix, new_solution.assigned_ordered_matrix, comb_vehicle, comb_day)
        for comb_vehicle, comb_day in linked_combinations:
            (new_solution.route_dist_matrix, new_solution.assigned_ordered_matrix) = optimize_single_route(n_vehicles, n_days, distance_matrix, closeness_matrix, new_solution.route_dist_matrix, new_solution.assigned_ordered_matrix, comb_vehicle, comb_day)

    #    ''' SWAP 1x1 '''
    elif (neigh_order[neighbour] == "k_swap_t" or 
          neigh_order[neighbour] == "f_swap_kt" or
          neigh_order[neighbour] == "swap_kt" ):
        for comb_vehicle, comb_day in selected_combinations[0]:
            (new_solution.route_dist_matrix, new_solution.assigned_ordered_matrix) = optimize_single_route(n_vehicles, n_days, distance_matrix, closeness_matrix, new_solution.route_dist_matrix, new_solution.assigned_ordered_matrix, comb_vehicle, comb_day)
        for comb_vehicle, comb_day in selected_combinations[1]:
            (new_solution.route_dist_matrix, new_solution.assigned_ordered_matrix) = optimize_single_route(n_vehicles, n_days, distance_matrix, closeness_matrix, new_solution.route_dist_matrix, new_solution.assigned_ordered_matrix, comb_vehicle, comb_day)
        for comb_vehicle, comb_day in linked_combinations[0]:
            (new_solution.route_dist_matrix, new_solution.assigned_ordered_matrix) = optimize_single_route(n_vehicles, n_days, distance_matrix, closeness_matrix, new_solution.route_dist_matrix, new_solution.assigned_ordered_matrix, comb_vehicle, comb_day)
        for comb_vehicle, comb_day in linked_combinations[1]:
            (new_solution.route_dist_matrix, new_solution.assigned_ordered_matrix) = optimize_single_route(n_vehicles, n_days, distance_matrix, closeness_matrix, new_solution.route_dist_matrix, new_solution.assigned_ordered_matrix, comb_vehicle, comb_day)

    # calculate new OBJ:
    new_solution.OBJ_tot_dist = algorithms.assign_route.calculate_tot_dist (n_vehicles, n_days, new_solution.route_dist_matrix, new_solution.OBJ_tot_dist)

    return new_solution



# SECONDARY FUNCTIONS 

def find_client_combos(neigh_order, neighbour, n_days, n_vehicles, data, current_solution, initial_comb):

    #    ''' MOVE '''
    if (neigh_order[neighbour] == "k_move_t" or 
        neigh_order[neighbour] == "move_kt"):
        clients = [initial_comb.client]
    
    #    ''' SWAP 1x1 '''
    elif (neigh_order[neighbour] == "k_swap_t" or 
          neigh_order[neighbour] == "f_swap_kt" or
          neigh_order[neighbour] == "swap_kt" ):
        clients = [initial_comb.comb_1.client, initial_comb.comb_2.client]
    

    for client in clients: 
        client_combos = []
        for vehicle in range(n_vehicles):
            for day in range(n_days):
                client_list = current_solution.assigned_ordered_matrix[vehicle, day]

                if not np.isin(client, client_list):
                    continue

                client_combos.append((vehicle, day))

        # print(f"client{client}, f{data[client, conf.FREQ_VISIT_INDEX]} --> combos: {client_combos}")

    return client_combos

#-------------------------------------------------

def pick_client(current_solution, vehicle_i, day_i, clients_filtred, avoid_client):

    client_list = copy.copy(current_solution.assigned_ordered_matrix[vehicle_i, day_i])

    # avoid client:
    if avoid_client != 0:
        where = np.where(client_list == avoid_client)[0]
        client_list[where] = 0

    # remove zeros:
    client_list = client_list[client_list != 0]

    # intersects with clients_filtred (i.e. no max freq):
    if np.all(clients_filtred) != 0:
        client_list = np.intersect1d(client_list, clients_filtred)

    # choose a random client:
    if np.size(client_list) == 0:
        real_client_index = 0
        return (real_client_index, False)
    
    real_client_index = random.choice(client_list)
    
    return (real_client_index, True)


def pick_set_clients(n_days, data, current_solution, vehicle_i, day_i, clients_filtred, number_clients):

    client_list = copy.copy(current_solution.assigned_ordered_matrix[vehicle_i, day_i])
    # remove zeros:
    client_list = client_list[client_list != 0]
    # if empty list
    if np.size(client_list) == 0:
        real_client_index = 0
        return (real_client_index, 0, False)
    
    # pick random client #1:
    real_client_index_1 = random.choice(client_list)

    # pick random client #2:
    if number_clients == 0:
        mask = client_list != real_client_index_1
        client_list_no_cl1 = client_list[mask]
        real_client_index_2 = random.choice(client_list_no_cl1)
    else:
        where_cl1 = (np.where(client_list == real_client_index_1)[0][0])
        possible_range = [int(where_cl1-number_clients), int(where_cl1-number_clients+1), int(where_cl1+number_clients-1), int(where_cl1+number_clients+1)]

        if possible_range[0] < 0:
            possible_range[0] = 0
            possible_range[1] = 1
        if possible_range[3] > len(client_list):
            possible_range[2] = len(client_list) -1
            possible_range[3] = len(client_list) 

        possible_client_list_1 = client_list[possible_range[0] : possible_range[1]]
        possible_client_list_2 = client_list[possible_range[2] : possible_range[3]]

        possible_client_list = [possible_client_list_1, possible_client_list_2]
        possible_client_list = np.concatenate((
            client_list[possible_range[0] : possible_range[1]],
            client_list[possible_range[2] : possible_range[3]]))
        
        mask = possible_client_list != real_client_index_1
        client_list_no_cl1 = np.array(possible_client_list[mask])

        real_client_index_2 = random.choice(client_list_no_cl1)

    # output
    where_cl1 = (np.where(client_list == real_client_index_1)[0])
    where_cl2 = (np.where(client_list == real_client_index_2)[0])
    number_clients = (abs(where_cl1 - where_cl2)+ 1)[0]

    real_client_index = np.zeros(2, dtype=int)
    if where_cl1 < where_cl2:
        real_client_index[0] = real_client_index_1
        real_client_index[1] = real_client_index_2
    else:
        real_client_index[1] = real_client_index_1
        real_client_index[0] = real_client_index_2

    return (real_client_index, number_clients, True)


def filter_clients_same_frequ(data, sorted_data, initial_comb_1):

    freq_required = data[initial_comb_1.client, conf.FREQ_VISIT_INDEX]
    clients_sorted_ndex = [np.where((sorted_data[:, conf.FREQ_VISIT_INDEX] == freq_required) )][0][0]
    clients_same_freq = sorted_data[clients_sorted_ndex, conf.CLIENT_ID_INDEX]
    clients_same_freq = [int(x) for x in clients_same_freq]

    return clients_same_freq


def def_possible_schedules(n_days, data, initial_comb_main):

    n_visit_comb = int(data[initial_comb_main.client][conf.N_VISIT_INDEX])
    possible_schedules = []
    
    for schedule in range(n_visit_comb):
        schedule_val = int(data[initial_comb_main.client][conf.VISIT_START_INDEX + schedule])
        schedule_bin = np.array([int(b) for b in format(schedule_val, f'0{n_days}b')], dtype=int)
        possible_schedules.append(schedule_bin)

    return possible_schedules


def def_new_schedule(n_days, n_vehicles, data, current_solution, initial_comb_main, final_comb_main):

    new_schedule = np.zeros(n_days)
    linked_combinations = []

    # print("\n\ndefine linked_combinations ------------------------------------------")
    # print("cliente:", initial_comb_main.client)
    # print("comb. iniziale:", initial_comb_main.vehicle, initial_comb_main.day)
    
    for vehicle in range(n_vehicles):
        for day in range(n_days):
            client_list = current_solution.assigned_ordered_matrix[vehicle, day]
            
            # print(f" v{vehicle}, d{day} lista: {client_list}")

            if not np.isin(initial_comb_main.client, client_list):
                continue
            if vehicle == initial_comb_main.vehicle and day == initial_comb_main.day:   # prima c'era initial_comb, perché??
                continue

            linked_combinations.append((vehicle, day))
            new_schedule[day] = 1
            # print(f"il cliente {initial_comb_main.client} è nella combinazione v{vehicle}, d{day}")
            # print("linked_combinations:", linked_combinations)
            # print("new_schedule:", new_schedule)


            # if (np.isin(initial_comb_main.client, client_list) and 
            #     (vehicle != initial_comb_main.vehicle or 
            #     day != initial_comb_main.day)):
            #     print(f"il cliente {initial_comb_main.client} è nella combinazione v{vehicle}, d{day}")
            #     linked_combinations.append((vehicle, day))
            #     print("linked_combinations:", linked_combinations)
            #     new_schedule[day] = 1
            #     print("new_schedule:", new_schedule)
    new_schedule[initial_comb_main.day] = 0
    new_schedule[final_comb_main.day] = 1

    # print("\nnew_schedule:", new_schedule)

    # # update linked combinations:
    # initial_comb_main.linked_comb = linked_combinations

    return (new_schedule, linked_combinations)


def move_operation(n_vehicles, n_days, data, distance_matrix, closeness_matrix, current_solution, initial_comb, final_comb):

    # creation of new_solution class attributes 
    (new_assigned_ordered_matrix, new_not_assigned_list, new_transp_demand_matrix, new_route_dist_matrix, new_OBJ_tot_dist) = \
        crete_new_sol_attributes(current_solution)

    # Remove and add client to the Assigned customer matrix and the Transported demand matrix
    (new_assigned_ordered_matrix, new_transp_demand_matrix) = \
        remove_client_NEW(data, 
                          new_assigned_ordered_matrix, new_transp_demand_matrix, 
                          initial_comb.day, initial_comb.vehicle, initial_comb.client)
    (new_assigned_ordered_matrix, new_transp_demand_matrix) = \
        add_client_NEW(data, 
                       new_assigned_ordered_matrix, new_transp_demand_matrix, 
                       final_comb.day, final_comb.vehicle, final_comb.client)

    # Reorganize the clients (best route) and update the Route distances matrix
    # (new_route_dist_matrix, new_assigned_ordered_matrix) = find_best_route(n_vehicles, n_days, distance_matrix, closeness_matrix, initial_comb, final_comb, new_route_dist_matrix, new_assigned_ordered_matrix)
    # Optimize routes (both initial and final combinations):
    (new_route_dist_matrix, new_assigned_ordered_matrix) = \
        optimize_single_route(
            n_vehicles, n_days, distance_matrix, closeness_matrix, 
            new_route_dist_matrix, new_assigned_ordered_matrix, 
            initial_comb.vehicle, initial_comb.day)
    (new_route_dist_matrix, new_assigned_ordered_matrix) = \
        optimize_single_route(
            n_vehicles, n_days, distance_matrix, closeness_matrix, 
            new_route_dist_matrix, new_assigned_ordered_matrix, 
            final_comb.vehicle, final_comb.day)
    
    # Calculate the OBJECTIVE value
    new_OBJ_tot_dist = algorithms.assign_route.calculate_tot_dist (n_vehicles, n_days, new_route_dist_matrix, new_OBJ_tot_dist)

    # Save new solution:
    new_solution = classes.Solution(new_OBJ_tot_dist, new_assigned_ordered_matrix, new_not_assigned_list, new_transp_demand_matrix, new_route_dist_matrix)


    return new_solution


def swap_operation(n_vehicles, n_days, data, distance_matrix, closeness_matrix, current_solution, initial_comb, final_comb):

    # creation of new_Solution class attributes
    (new_assigned_ordered_matrix, new_not_assigned_list, new_transp_demand_matrix, new_route_dist_matrix, new_OBJ_tot_dist) = crete_new_sol_attributes(current_solution)

    # Remove and add client to the Assigned customer matrix and the Transported demand matrix
    # for day in range(n_days):
    #     (new_assigned_ordered_matrix, new_transp_demand_matrix) = remove_client(n_days, data, initial_comb.comb_1, final_comb.comb_1, new_assigned_ordered_matrix, new_transp_demand_matrix, day)            
    #     (new_assigned_ordered_matrix, new_transp_demand_matrix) = add_client(n_days, data, initial_comb.comb_1, final_comb.comb_1, new_assigned_ordered_matrix, new_transp_demand_matrix, day)  
    # for day in range(n_days):
    #     (new_assigned_ordered_matrix, new_transp_demand_matrix) = remove_client(n_days, data, initial_comb.comb_2, final_comb.comb_2, new_assigned_ordered_matrix, new_transp_demand_matrix, day)            
    #     (new_assigned_ordered_matrix, new_transp_demand_matrix) = add_client(n_days, data, initial_comb.comb_2, final_comb.comb_2, new_assigned_ordered_matrix, new_transp_demand_matrix, day)  

    (new_assigned_ordered_matrix, new_transp_demand_matrix) = remove_client_NEW(data,new_assigned_ordered_matrix, new_transp_demand_matrix, 
                                                                                initial_comb.comb_1.day, initial_comb.comb_1.vehicle, initial_comb.comb_1.client)
    # print(f"removed c{initial_comb.comb_1.client} --> {new_assigned_ordered_matrix[initial_comb.comb_1.vehicle, initial_comb.comb_1.day]}")
    (new_assigned_ordered_matrix, new_transp_demand_matrix) = add_client_NEW(data, new_assigned_ordered_matrix, new_transp_demand_matrix, 
                                                                             final_comb.comb_1.day, final_comb.comb_1.vehicle, final_comb.comb_1.client)
    # print(f"added c{final_comb.comb_1.client} --> {new_assigned_ordered_matrix[final_comb.comb_1.vehicle, final_comb.comb_1.day]}")

    (new_assigned_ordered_matrix, new_transp_demand_matrix) = remove_client_NEW(data,new_assigned_ordered_matrix, new_transp_demand_matrix, 
                                                                                initial_comb.comb_2.day, initial_comb.comb_2.vehicle, initial_comb.comb_2.client)
    # print(f"removed c{initial_comb.comb_2.client} --> {new_assigned_ordered_matrix[initial_comb.comb_2.vehicle, initial_comb.comb_2.day]}")
    (new_assigned_ordered_matrix, new_transp_demand_matrix) = add_client_NEW(data, new_assigned_ordered_matrix, new_transp_demand_matrix, 
                                                                             final_comb.comb_2.day, final_comb.comb_2.vehicle, final_comb.comb_2.client)
    # print(f"added c{final_comb.comb_2.client} --> {new_assigned_ordered_matrix[final_comb.comb_2.vehicle, final_comb.comb_2.day]}")

    # Reorganize the clients (best route) and update the Route distances matrix
    # (new_route_dist_matrix, new_assigned_ordered_matrix) = find_best_route(n_vehicles, n_days, distance_matrix, closeness_matrix, initial_comb.comb_1, final_comb.comb_1, new_route_dist_matrix, new_assigned_ordered_matrix)
    # (new_route_dist_matrix, new_assigned_ordered_matrix) = find_best_route(n_vehicles, n_days, distance_matrix, closeness_matrix, initial_comb.comb_2, final_comb.comb_2, new_route_dist_matrix, new_assigned_ordered_matrix)
    # (new_route_dist_matrix, new_assigned_ordered_matrix) = find_best_route(n_vehicles, n_days, distance_matrix, closeness_matrix, initial_comb.comb_1, initial_comb.comb_2, new_route_dist_matrix, new_assigned_ordered_matrix)
    # Optimize routes:
    # (n_vehicles, n_days, distance_matrix, closeness_matrix, new_route_dist_matrix, new_assigned_ordered_matrix, vehicle, day)
    # print(f"\nB: must optimize route v{final_comb.comb_1.vehicle}, d{final_comb.comb_1.day} \n--> {new_assigned_ordered_matrix[final_comb.comb_1.vehicle, final_comb.comb_1.day]}") #, )
    (new_route_dist_matrix, new_assigned_ordered_matrix) = optimize_single_route(n_vehicles, n_days, distance_matrix, closeness_matrix, new_route_dist_matrix, new_assigned_ordered_matrix, final_comb.comb_1.vehicle, final_comb.comb_1.day)
    # print(f"A: optimized route v{final_comb.comb_1.vehicle}, d{final_comb.comb_1.day} \n--> {new_assigned_ordered_matrix[final_comb.comb_1.vehicle, final_comb.comb_1.day]}") #, )
    
    # print(f"\nB: must optimize route v{final_comb.comb_2.vehicle}, d{final_comb.comb_2.day} \n--> {new_assigned_ordered_matrix[final_comb.comb_2.vehicle, final_comb.comb_2.day]}") #, )
    (new_route_dist_matrix, new_assigned_ordered_matrix) = optimize_single_route(n_vehicles, n_days, distance_matrix, closeness_matrix, new_route_dist_matrix, new_assigned_ordered_matrix, final_comb.comb_2.vehicle, final_comb.comb_2.day)
    # print(f"optimized route v{final_comb.comb_2.vehicle}, d{final_comb.comb_2.day} \n--> {new_assigned_ordered_matrix[final_comb.comb_2.vehicle, final_comb.comb_2.day]}") #, )


    # Calculate the OBJECTIVE value
    new_OBJ_tot_dist = algorithms.assign_route.calculate_tot_dist (n_vehicles, n_days, new_route_dist_matrix, new_OBJ_tot_dist)

    # Save new solution:
    new_solution = classes.Solution(new_OBJ_tot_dist, new_assigned_ordered_matrix, new_not_assigned_list, new_transp_demand_matrix, new_route_dist_matrix)

    return new_solution


def crete_new_sol_attributes(current_solution):

    new_assigned_ordered_matrix = copy.deepcopy(current_solution.assigned_ordered_matrix)  
    new_not_assigned_list = copy.deepcopy(current_solution.not_assigned_list)
    new_transp_demand_matrix = copy.deepcopy(current_solution.transp_demand_matrix)
    new_route_dist_matrix = copy.deepcopy(current_solution.route_dist_matrix)
    new_OBJ_tot_dist = 0

    return (new_assigned_ordered_matrix, new_not_assigned_list, new_transp_demand_matrix, new_route_dist_matrix, new_OBJ_tot_dist)


def remove_client(n_days, data, initial_comb, final_comb, new_assigned_ordered_matrix, new_transp_demand_matrix, day):

    if initial_comb.schedule[day] == 1:
        client_sequence = new_assigned_ordered_matrix[initial_comb.vehicle, day]
        idx = np.where(client_sequence == initial_comb.client)[0][0]    # Trova la posizione in cui compare il cliente da rimuovere
        client_sequence[idx:-1] = client_sequence[idx+1:] # move to left
        client_sequence[-1] = 0  # azzera l'ultimo

        new_transp_demand_matrix[initial_comb.vehicle, day] -= data[initial_comb.client, conf.DEMAND_INDEX]

    return (new_assigned_ordered_matrix, new_transp_demand_matrix)


def remove_client_NEW(data, new_assigned_ordered_matrix, new_transp_demand_matrix, initial_day, initial_vehicle, client):

    client_sequence = new_assigned_ordered_matrix[initial_vehicle, initial_day]
    # print(f"\nclient{client}, v{initial_vehicle} d{initial_day}")
    # print("client_sequence", client_sequence)
    idx = np.where(client_sequence == client)[0][0]    # Trova la posizione in cui compare il cliente da rimuovere
    # print("\nclient_sequence", client_sequence)
    # print(f"v{initial_vehicle}, d{initial_day}, client{client}")
    # print("where", idx)
    client_sequence[idx:-1] = client_sequence[idx+1:] # move to left
    client_sequence[-1] = 0  # azzera l'ultimo

    new_assigned_ordered_matrix[initial_vehicle, initial_day] = client_sequence
    new_transp_demand_matrix[initial_vehicle, initial_day] -= data[client, conf.DEMAND_INDEX]

    return (new_assigned_ordered_matrix, new_transp_demand_matrix)


def add_client(n_days, data, initial_comb, final_comb, new_assigned_ordered_matrix, new_transp_demand_matrix, day):

    if final_comb.schedule[day] == 1:
        client_sequence = new_assigned_ordered_matrix[final_comb.vehicle, day]
        idx = np.where(client_sequence == 0)[0][1]  # Trova la posizione in cui compare il cliente da rimuovere
        client_sequence[idx] = final_comb.client    # inserisce il nuovo cliente

        new_transp_demand_matrix[final_comb.vehicle, day] += data[final_comb.client, conf.DEMAND_INDEX]

    return (new_assigned_ordered_matrix, new_transp_demand_matrix)


def add_client_NEW(data, new_assigned_ordered_matrix, new_transp_demand_matrix, final_day, final_vehicle, client):

    client_sequence = new_assigned_ordered_matrix[final_vehicle, final_day]
    idx = np.where(client_sequence == 0)[0][1]  # Trova la posizione in cui compare il primo posto libero
    client_sequence[idx] = client    # inserisce il nuovo cliente

    new_assigned_ordered_matrix[final_vehicle, final_day] = client_sequence
    new_transp_demand_matrix[final_vehicle, final_day] += data[client, conf.DEMAND_INDEX]

    return (new_assigned_ordered_matrix, new_transp_demand_matrix)


def find_best_route(n_vehicles, n_days, distance_matrix, closeness_matrix, initial_comb, final_comb, new_route_dist_matrix, new_assigned_ordered_matrix):

    assign_matrix = np.zeros((n_vehicles, n_days), dtype=int)
    for day in range(n_days):    
        if initial_comb.schedule[day] == 1:
            assign_matrix[initial_comb.vehicle, day] = 1
            new_route_dist_matrix[initial_comb.vehicle, day] = 0
        if final_comb.schedule[day] == 1:
            assign_matrix[final_comb.vehicle, day] = 1
            new_route_dist_matrix[final_comb.vehicle, day] = 0
    # print("assign_matrix", assign_matrix)

    (distances_matrix, new_assigned_ordered_matrix) = algorithms.assign_route.calculate_distances_CLOSNESS_line_route(n_vehicles, n_days, assign_matrix, new_assigned_ordered_matrix, distance_matrix, closeness_matrix)
    new_route_dist_matrix += distances_matrix

    return (new_route_dist_matrix, new_assigned_ordered_matrix)
# new find_best_route:
def optimize_single_route(n_vehicles, n_days, distance_matrix, closeness_matrix, new_route_dist_matrix, new_assigned_ordered_matrix, vehicle, day):

    # define route (vehicle, day) to optimize
    assign_matrix = np.zeros((n_vehicles, n_days), dtype=int)
    assign_matrix[vehicle, day] = 1
    new_route_dist_matrix[vehicle, day] = 0

    # optimize route --> OLD: algorithms.assign_route.calculate_distances_CLOSNESS_line_route
    (distances_matrix, new_assigned_ordered_matrix) = calculate_distances_CLOSNESS_line_route(n_vehicles, n_days, assign_matrix, new_assigned_ordered_matrix, distance_matrix, closeness_matrix)
    new_route_dist_matrix += distances_matrix

    return (new_route_dist_matrix, new_assigned_ordered_matrix)


def calculate_distances_CLOSNESS_line_route(
    n_vehicles, n_days, S_poss_assign_matrix, S_assigned_cust_matrix, distance_matrix, closeness_matrix
): 
    import numpy as np
    from collections import Counter

    S_distances_matrix = np.zeros((n_vehicles, n_days), dtype=float)

    for vehicle_k in range(n_vehicles):
        for day_t in range(n_days):

            if S_poss_assign_matrix[vehicle_k][day_t] == 0:
                continue  # Nessun cliente da assegnare

            client_list = S_assigned_cust_matrix[vehicle_k][day_t]
            client_list = client_list[client_list != 0].astype(int).tolist()

            if len(client_list) == 0:
                continue

            # 🔧 crea una lista di occorrenze univoche
            client_occurrences = []
            counter = Counter()
            for cid in client_list:
                counter[cid] += 1
                client_occurrences.append((cid, counter[cid]))  # (cliente_id, numero_visita)

            route = []

            # Primo cliente: più vicino al deposito (nodo 0)
            first = next((c for c in closeness_matrix[0] if any(cid == c for cid, _ in client_occurrences)), None)
            if first is None:
                continue

            # rimuove solo la prima occorrenza di quel cliente
            for i, (cid, occ) in enumerate(client_occurrences):
                if cid == first:
                    client_occurrences.pop(i)
                    break
            route.append(first)

            # Inserisci i restanti clienti greedy
            while client_occurrences:
                prev_cl = int(route[-1])
                next_cl = next((c for c in closeness_matrix[prev_cl] if any(cid == c for cid, _ in client_occurrences)), None)
                if next_cl is not None:
                    for i, (cid, occ) in enumerate(client_occurrences):
                        if cid == next_cl:
                            client_occurrences.pop(i)
                            break
                    route.append(next_cl)
                else:
                    # 👇 se restano clienti non raggiungibili (duplicati), li aggiungo in coda
                    route.extend([cid for cid, _ in client_occurrences])
                    client_occurrences.clear()
                    break

            # Chiudi il percorso aggiungendo il deposito all'inizio e alla fine
            route = [0] + route + [0]

            # Calcolo distanza totale del percorso
            try:
                route_distance = sum(distance_matrix[route[i], route[i + 1]] for i in range(len(route) - 1))
            except IndexError as e:
                print(f"❌ Errore nell'accesso alla distance_matrix: {e}")
                route_distance = 999999

            S_distances_matrix[vehicle_k, day_t] = route_distance
            S_assigned_cust_matrix[vehicle_k, day_t, :len(route)] = route

    return S_distances_matrix, S_assigned_cust_matrix


# def calculate_distances_CLOSNESS_line_route(n_vehicles, n_days, S_poss_assign_matrix, S_assigned_cust_matrix, distance_matrix, closeness_matrix):
#     S_distances_matrix = np.zeros((n_vehicles, n_days), dtype=float)

#     for vehicle_k in range(n_vehicles):
#         for day_t in range(n_days):

#             if S_poss_assign_matrix[vehicle_k][day_t] == 0:
#                 continue  # Nessun cliente da assegnare

#             # Estrai i clienti assegnati, rimuovi zeri e converti in lista
#             client_list = S_assigned_cust_matrix[vehicle_k][day_t]
#             client_list = client_list[client_list != 0].astype(int).tolist()

#             if len(client_list) == 0:
#                 continue  # Nessun cliente utile

#             route = [0] * len(client_list)

#             # Primo cliente: più vicino al deposito (nodo 0)
#             first = next((c for c in closeness_matrix[0] if c in client_list), None)
#             if first is None:
#                 continue
#             route[0] = first
#             client_list.remove(first)

#             # Inserisci i restanti clienti greedy
#             idx = 1

#             while client_list:
#                 # Inserimento 
#                 prev_cl = int(route[idx - 1])
#                 next_cl = next((c for c in closeness_matrix[prev_cl] if c in client_list), None)
#                 if next_cl is not None:
#                     route[idx] = next_cl
#                     client_list.remove(next_cl)
#                     idx += 1
#                 else:
#                     break  # Nessun cliente vicino trovato

#             # Chiudi il percorso aggiungendo il deposito all'inizio e alla fine
#             route = [0] + [int(r) for r in route if r != 0] + [0]

#             # Calcolo distanza totale del percorso
#             try:
#                 route_distance = sum(distance_matrix[route[i], route[i + 1]] for i in range(len(route) - 1))
#             except IndexError as e:
#                 print(f"❌ Errore nell'accesso alla distance_matrix: {e}")
#                 route_distance = 999999

#             S_distances_matrix[vehicle_k, day_t] = route_distance

#             # Salva il percorso nel tensor 3D
#             S_assigned_cust_matrix[vehicle_k, day_t, :len(route)] = route

#             # print(f"✔️ Veicolo {vehicle_k}, Giorno {day_t}, Percorso: {route}, Distanza: {route_distance}")

#     return S_distances_matrix, S_assigned_cust_matrix


# def calculate_tot_dist (n_vehicles, n_days, route_dist_matrix, OBJ_tot_dist):

#     for vehicle_k in range(n_vehicles):
#         for day_t in range(n_days):
#             OBJ_tot_dist += route_dist_matrix[vehicle_k][day_t]

#     return(OBJ_tot_dist)


def find_schedules(all_possible_schedules, final_comb_schedule):

    possible_schedules = []
    actual_day = copy.deepcopy(final_comb_schedule)

    for sched in all_possible_schedules:
        verify_sched = np.add(sched, actual_day)

        if np.any(verify_sched[:] == 2):
            possible_schedules.append(sched)

    return possible_schedules


def find_poss_combinations(n_days, n_vehicles, final_comb_day, possible_schedules):

    poss_days = []
    poss_vehicles = []
    poss_combinations = []

    for schedule in possible_schedules:
        for day in range(n_days):
            if schedule[day] ==1 and schedule[day] != final_comb_day:
                poss_days.append(day)
    
    for vehicle in range(n_vehicles):
        poss_vehicles.append(vehicle)

    for day in poss_days:
        for vehicle in poss_vehicles:
            poss_combinations.append((vehicle, day))

    return poss_combinations


def find_capacity_comb(data, vehicle_capacity, new_solution, all_poss_combinations, final_comb_client):

    poss_combinations = []

    capacity_matrix = copy.deepcopy(new_solution.transp_demand_matrix)
    demand_client = data[final_comb_client, conf.DEMAND_INDEX]

    for vehicle, day in all_poss_combinations:
        actual_capacity = capacity_matrix[vehicle, day]
        tot_possible_capacity = actual_capacity + demand_client

        if tot_possible_capacity <= vehicle_capacity:
            poss_combinations.append((vehicle, day))

    return poss_combinations


def find_valid_sched(n_days, possible_combinations, possible_schedules):

    possible_days_list = unique_days = list(set(day for vehicle, day in possible_combinations))
    available_days_sched = np.zeros(n_days)

    for day in possible_days_list:
        available_days_sched[day] = 1
    
    valid_schedules = []
    for sched in possible_schedules:
        # condizione: ogni 1 nello schedule deve corrispondere a un 1 nei giorni disponibili
        if np.all((sched == 0) | (available_days_sched == 1)):
            valid_schedules.append(sched)

    return valid_schedules


def find_choose_linked_comb(n_days, selected_schedule, possible_combinations, final_comb):

    selected_combinations = []

    for day in range(n_days):
        if selected_schedule[day] == 1 and day != final_comb.day:

            # define possible vehivles and pick one
            possible_vehicles = [vehicle for vehicle, day_comb in possible_combinations if day_comb == day]
            selected_vehicle = random.choice(possible_vehicles)

            # save combination
            selected_combinations.append((selected_vehicle, day))

    return selected_combinations

