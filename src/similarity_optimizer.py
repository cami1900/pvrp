import itertools
import math
import random
import random2
import copy
import os
import pandas as pd
import numpy as np
import algorithms
import utils
from new_route_optimizer import solve_vrp_day
from algorithms.similarity_measures import (def_sim_1_matrix, measure_sim_1, measure_sim_int, get_sim_functions)
import algorithms.similarity_measures as sim_calc
from test_similarity import (measure_sim_2, measure_sim_3)
from algorithms.VND_multiOBJ import (crete_new_sol_attributes, optimize_single_route, calculate_tot_dist)
from classes import Solution_multiOBJ


def generate_combinations(n_days, n_vehicles):
    """
    Genera tutte le possibili combinazioni uniche di assegnazioni
    (senza contare le permutazioni delle assegnazioni come distinte).
    Restituisce:
        - una lista di configurazioni (ognuna è una lista di permutazioni giornaliere)
        - il numero totale di configurazioni
    """
    # Tutte le permutazioni possibili di veicoli
    perms = list(itertools.permutations(range(n_vehicles)))

    # Fissiamo il primo giorno come [0,1,2,...] per evitare duplicati
    first_day = tuple(range(n_vehicles))

    # Le restanti giornate possono essere qualsiasi permutazione
    other_days_choices = itertools.product(perms, repeat=n_days - 1)

    all_combinations = []
    for days in other_days_choices:
        combo = (first_day,) + days  # aggiungo il primo giorno fisso
        all_combinations.append(combo)

    total = len(all_combinations)
    return all_combinations, total

def measure_sim_int_1(n_vehicles, sim_int_1_matrix):

    sim_int_1_measures = np.zeros(n_vehicles, dtype= int)

    for vehicle in range(n_vehicles):
        sim_int_1_measures[vehicle] = len(sim_int_1_matrix[vehicle])

    return sim_int_1_measures

''' t_swap_r_k versions '''

def t_swap_r_k_worse(n_days, n_vehicles, max_iterations, best_solution):

    iteration = 0
    while iteration < max_iterations:

        ''' initial combo'''
        day_i = random.randint(0, n_days-1)
        vehicle_i = random.randint(0, n_vehicles-1)

        ''' final combo '''
        vehicle_f = random.choice([t for t in range(0, n_vehicles) if t != vehicle_i])

        ''' swap '''
        assigned_clients = copy.deepcopy(best_solution.assigned_ordered_matrix)
        set_clients_per_veichle_base_sol = def_sim_1_matrix(n_vehicles, n_days, assigned_clients)
        
        assigned_clients[vehicle_i, day_i] = copy.deepcopy(best_solution.assigned_ordered_matrix[vehicle_f, day_i])
        assigned_clients[vehicle_f, day_i] = copy.deepcopy(best_solution.assigned_ordered_matrix[vehicle_i, day_i])
        set_clients_per_veichle_new_sol = def_sim_1_matrix(n_vehicles, n_days, assigned_clients)

        # min(max) --> try to minimize the vehicle with higher number of clients

        # set the values to 0:
        worse_sim_int_sol = 0
        worse_sim_int_new_sol = 0

        # search the higher value of clients assigned to a client
        for vehicle in range(n_vehicles):

            n_clients_v_base = len(set_clients_per_veichle_base_sol[vehicle])
            n_clients_v_new = len(set_clients_per_veichle_new_sol[vehicle])

            if n_clients_v_base > worse_sim_int_sol: # if the number of clients is bigger than the actual value
                worse_sim_int_sol = n_clients_v_base

            if n_clients_v_new > worse_sim_int_new_sol: # if the number of clients is bigger than the actual value
                worse_sim_int_new_sol = n_clients_v_new
        
        # if the new_sol's max number of clients is lower than base_sol's max number of clients: accept swap operation
        if worse_sim_int_new_sol < worse_sim_int_sol:
            # print(f"improved internal similarity \nswap: d{day_i}, v{vehicle_i}-v{vehicle_f}")
            best_solution.assigned_ordered_matrix = assigned_clients
            demand_i_i = best_solution.transp_demand_matrix[vehicle_i, day_i]
            best_solution.transp_demand_matrix[vehicle_i, day_i] = best_solution.transp_demand_matrix[vehicle_f, day_i]
            best_solution.transp_demand_matrix[vehicle_f, day_i] = demand_i_i
            distance_i_i = best_solution.route_dist_matrix[vehicle_i, day_i]
            best_solution.route_dist_matrix[vehicle_i, day_i] = best_solution.route_dist_matrix[vehicle_f, day_i]
            best_solution.route_dist_matrix[vehicle_f, day_i] = distance_i_i
            # update parameters
            iteration = 0
        else:
            iteration += 1

    return best_solution

def t_swap_r_k_tot(n_days, n_vehicles, max_iterations, best_solution):

    iteration = 0
    while iteration < max_iterations:

        ''' initial combo'''
        day_i = random.randint(0, n_days-1)
        vehicle_i = random.randint(0, n_vehicles-1)

        ''' final combo '''
        vehicle_f = random.choice([t for t in range(0, n_vehicles) if t != vehicle_i])

        ''' swap '''
        assigned_clients = copy.deepcopy(best_solution.assigned_ordered_matrix)
        sim_int_1_matrix_sol = def_sim_1_matrix(n_vehicles, n_days, assigned_clients)
        
        assigned_clients[vehicle_i, day_i] = best_solution.assigned_ordered_matrix[vehicle_f, day_i]
        assigned_clients[vehicle_f, day_i] = best_solution.assigned_ordered_matrix[vehicle_i, day_i]
        sim_int_1_matrix_new_sol = def_sim_1_matrix(n_vehicles, n_days, assigned_clients)

        # valuto il costo totale
        sim_int_sol = 0
        sim_int_new_sol = 0
        for vehicle in range(n_vehicles):
            sim_int_sol += len(sim_int_1_matrix_sol[vehicle])
            sim_int_new_sol += len(sim_int_1_matrix_new_sol[vehicle])

                
        if sim_int_new_sol < sim_int_sol:
            # print(f"improved internal similarity \nswap: d{day_i}, v{vehicle_i}-v{vehicle_f}")
            best_solution.assigned_ordered_matrix = assigned_clients
            demand_i_i = best_solution.transp_demand_matrix[vehicle_i, day_i]
            best_solution.transp_demand_matrix[vehicle_i, day_i] = best_solution.transp_demand_matrix[vehicle_f, day_i]
            best_solution.transp_demand_matrix[vehicle_f, day_i] = demand_i_i
            distance_i_i = best_solution.route_dist_matrix[vehicle_i, day_i]
            best_solution.route_dist_matrix[vehicle_i, day_i] = best_solution.route_dist_matrix[vehicle_f, day_i]
            best_solution.route_dist_matrix[vehicle_f, day_i] = distance_i_i
            # update parameters
            iteration = 0
        else:
            iteration += 1

    return best_solution

def t_swap_r_k(sim_type, weights, n_days, n_vehicles, current_solution):

    ''' initial combo'''
    day_i = random.randint(0, n_days-1)
    vehicle_i = random.randint(0, n_vehicles-1)

    ''' final combo '''
    vehicle_f = random.choice([t for t in range(0, n_vehicles) if t != vehicle_i])

    ''' swap '''
    assigned_clients_new = copy.deepcopy(current_solution.assigned_ordered_matrix)
    
    assigned_clients_new[vehicle_i, day_i] = copy.deepcopy(current_solution.assigned_ordered_matrix[vehicle_f, day_i])
    assigned_clients_new[vehicle_f, day_i] = copy.deepcopy(current_solution.assigned_ordered_matrix[vehicle_i, day_i])

    ''' similarity values '''
    # min(max) --> try to minimize the vehicle with higher number of clients
    sim_int_value_current = measure_sim_int(n_vehicles, n_days, current_solution.assigned_ordered_matrix)
    sim_int_value_new = measure_sim_int(n_vehicles, n_days, assigned_clients_new)

    # if the new_sol's max number of clients is lower than base_sol's max number of clients: accept swap operation
    if sim_int_value_new < sim_int_value_current:

        # creation of new_Solution class attributes: 
        (new_OBJ_value, new_tot_dist, new_sim_value, 
        new_assigned_ordered_matrix, new_not_assigned_list, new_transp_demand_matrix, new_route_dist_matrix, 
        new_sim_matrix) = \
            crete_new_sol_attributes(current_solution)
        
        # update solution:
        new_assigned_ordered_matrix = assigned_clients_new

        new_transp_demand_matrix[vehicle_i, day_i] = current_solution.transp_demand_matrix[vehicle_f, day_i]
        new_transp_demand_matrix[vehicle_f, day_i] = current_solution.transp_demand_matrix[vehicle_i, day_i]

        new_route_dist_matrix[vehicle_i, day_i] = current_solution.route_dist_matrix[vehicle_f, day_i]
        new_route_dist_matrix[vehicle_f, day_i] = current_solution.route_dist_matrix[vehicle_i, day_i]

        new_tot_dist = current_solution.tot_dist

        # ''' Reorganize the clients (best route) and update the Route distances matrix '''
        # (new_route_dist_matrix, new_assigned_ordered_matrix) = \
        #     optimize_single_route(
        #         n_vehicles, n_days, distance_matrix, closeness_matrix, 
        #         new_route_dist_matrix, new_assigned_ordered_matrix, 
        #         vehicle_i, day_i)
        
        # (new_route_dist_matrix, new_assigned_ordered_matrix) = \
        #     optimize_single_route(
        #         n_vehicles, n_days, distance_matrix, closeness_matrix, 
        #         new_route_dist_matrix, new_assigned_ordered_matrix, 
        #         vehicle_f, day_i)

        # new_tot_dist = calculate_tot_dist(n_vehicles, n_days, new_route_dist_matrix)    # dovrebbe essere la stessa!!!

        if sim_type in ["sim_1", "sim_2", "sim_3"]:
            update_func, measure_func = get_sim_functions(sim_type, sim_calc)

            new_sim_matrix = update_func(n_days,
                new_assigned_ordered_matrix, new_sim_matrix, 
                vehicle_i, day_i)
            new_sim_matrix = update_func(n_days,
                new_assigned_ordered_matrix, new_sim_matrix, 
                vehicle_f, day_i)

            new_sim_value, sim_combinations_matrix, sim_vehicle_pairings, sim_measures = \
                measure_func(n_vehicles, n_days, current_solution.sim_matrix, new_sim_matrix)
    
    ''' Calculate OBJ value '''
    new_dist_value = new_tot_dist/current_solution.dist_value
    new_dissim_value  = 1-new_sim_value
    new_OBJ_value = ((weights[0] * new_dist_value) + (weights[1] * new_dissim_value))

    # Save new solution:
    new_solution = Solution_multiOBJ(
        new_OBJ_value, new_tot_dist, new_sim_value, 
        new_assigned_ordered_matrix, new_not_assigned_list, new_transp_demand_matrix, new_route_dist_matrix, 
        new_sim_matrix)

    return new_solution




def sim_matrix_clean(sim_matrix_sol):

    sim_matrix_sol_clean = [
        sorted(int(c) for c in vehicle_clients)
        for vehicle_clients in sim_matrix_sol
    ]

    return sim_matrix_sol_clean

def calc_internal_sim(n_vehicles, sim_matrix_sol):

    int_sim_sol = []
    for vehicle in range(n_vehicles):
        int_sim_v_value = len(sim_matrix_sol[vehicle])
        int_sim_sol.append(int_sim_v_value)

    return int_sim_sol

''' test t_swap_r_k (2 versions) '''

def test_t_swap_r_k_versions(n_days, n_vehicles, start_sol_base, start_sol_new, output_dir):
    """
    Esegue test per entrambe le varianti di t_swap_r_k su diversi valori di max_iterations.
    Salva i risultati in due file di testo distinti, nel formato compatto richiesto.
    """

    iteration_values = list(range(100, 5001, 100))

    versions = {
        "t_swap_r_k_worse": t_swap_r_k_worse,
        "t_swap_r_k_tot": t_swap_r_k_tot
    }

    for version_name, t_swap_func in versions.items():

        results_path = os.path.join(output_dir, f"results_{version_name}.txt")

        # with open(results_path, "w") as f:
        #     f.write(f"# Risultati {version_name}\n")
        #     f.write("=" * 40 + "\n\n")

        # inizializza liste per memorizzare i risultati di tutte le iterazioni
        int_sim_opt_values = []
        opt_sim_1_values = []
        opt_sim_2_values = []
        opt_sim_3_values = []

        for max_iterations in iteration_values:

            ''' START '''
            # assignation matrices
            start_base_ass_matrix = start_sol_base.assigned_ordered_matrix
            start_new_ass_matrix = start_sol_new.assigned_ordered_matrix

            # internal similarity
            sim1_start_sol_base = def_sim_1_matrix(n_vehicles, n_days, start_base_ass_matrix)
            sim1_start_sol_new = def_sim_1_matrix(n_vehicles, n_days, start_new_ass_matrix)
            int_sim_start_sol_base = calc_internal_sim(n_vehicles, sim1_start_sol_base)
            int_sim_start_sol_new = calc_internal_sim(n_vehicles, sim1_start_sol_new)
            int_sim_starting_value = np.mean(np.array([ int_sim_start_sol_base, int_sim_start_sol_new ]))

            # similarity 1
            (starting_sim_1_value, _, _, _) = measure_sim_1(
                n_vehicles, n_days, sim1_start_sol_base, sim1_start_sol_new
            )
            # similarity 2
            (_, starting_sim_2_value, _, _, _) = measure_sim_2(
                n_vehicles, n_days, start_base_ass_matrix, start_new_ass_matrix
            )
            # similarity 3
            (_, starting_sim_3_value, _, _, _) = measure_sim_3(
                n_vehicles, n_days, start_base_ass_matrix, start_new_ass_matrix
            )

            ''' OPT '''
            # Creation of optimized solutions
            opt_sol_base = t_swap_func(n_days, n_vehicles, max_iterations, copy.deepcopy(start_sol_base))
            opt_sol_new = t_swap_func(n_days, n_vehicles, max_iterations, copy.deepcopy(start_sol_new))

            # assignation matrices
            opt_base_ass_matrix = opt_sol_base.assigned_ordered_matrix
            opt_new_ass_matrix = opt_sol_new.assigned_ordered_matrix

            # internal similarity
            sim1_opt_sol_base = def_sim_1_matrix(n_vehicles, n_days, opt_base_ass_matrix)
            sim1_opt_sol_new = def_sim_1_matrix(n_vehicles, n_days, opt_new_ass_matrix)
            int_sim_opt_sol_base = calc_internal_sim(n_vehicles, sim1_opt_sol_base)
            int_sim_opt_sol_new = calc_internal_sim(n_vehicles, sim1_opt_sol_new)
            int_sim_opt_value = np.mean(np.array([ int_sim_opt_sol_base, int_sim_opt_sol_new ]))

            # similarity 1
            (opt_sim_1_value, _, _, _) = measure_sim_1(
                n_vehicles, n_days, sim1_opt_sol_base, sim1_opt_sol_new
            )
            # similarity 2
            (_, opt_sim_2_value, _, _, _) = measure_sim_2(
                n_vehicles, n_days, opt_base_ass_matrix, opt_new_ass_matrix
            )
            # similarity 3
            (_, opt_sim_3_value, _, _, _) = measure_sim_3(
                n_vehicles, n_days, opt_base_ass_matrix, opt_new_ass_matrix
            )

            # Scrittura nel formato richiesto
            # f.write(f"{max_iterations}\n")
            # f.write(f"{int_sim_sol_base} {int_sim_sol_new}\n")
            # f.write(f"{starting_sim_1_value} {starting_sim_1_pair_values}\n")
            # f.write(f"{int_sim_opt_sol_base} {int_sim_opt_sol_new}\n")
            # f.write(f"{opt_sim_1_value} {opt_sim_1_pair_values}\n\n")

            int_sim_opt_values.append(int_sim_opt_value)
            opt_sim_1_values.append(opt_sim_1_value)
            opt_sim_2_values.append(opt_sim_2_value)
            opt_sim_3_values.append(opt_sim_3_value)


        # prepara dizionari con i valori iniziali e finali
        starting_values = {
            "int_sim": int_sim_starting_value,
            "sim_1": starting_sim_1_value,
            "sim_2": starting_sim_2_value,
            "sim_3": starting_sim_3_value
        }

        opt_values = {
            "int_sim": int_sim_opt_values,
            "sim_1": opt_sim_1_values,
            "sim_2": opt_sim_2_values,
            "sim_3": opt_sim_3_values
        }

        # salva in Excel
        save_t_swap_r_k_results_excel(
            output_dir=output_dir,
            version_name=version_name,
            iteration_values=iteration_values,
            starting_values=starting_values,
            opt_values=opt_values
        )

    print(f"✅ Risultati salvati in: {results_path}")

def save_t_swap_r_k_results_excel(
    output_dir,
    version_name,
    iteration_values,
    starting_values,
    opt_values
):
    """
    Crea un file Excel con i risultati per una specifica versione di t_swap_r_k.

    Colonne:
    0 - iteration ("start" per la prima riga, poi max_iterations)
    1 - int_sim_value (starting_sim per la prima riga)
    2 - sim_1_value
    3 - sim_2_value
    4 - sim_3_value
    """

    # Creazione dati per Excel
    data = []

    # Riga iniziale ("start")
    data.append({
        "iteration": "start",
        "int_sim_value": starting_values["int_sim"],
        "sim_1_value": starting_values["sim_1"],
        "sim_2_value": starting_values["sim_2"],
        "sim_3_value": starting_values["sim_3"]
    })

    # Righe successive (una per ogni max_iteration)
    for i, max_it in enumerate(iteration_values):
        data.append({
            "iteration": max_it,
            "int_sim_value": opt_values["int_sim"][i],
            "sim_1_value": opt_values["sim_1"][i],
            "sim_2_value": opt_values["sim_2"][i],
            "sim_3_value": opt_values["sim_3"][i]
        })

    # Creazione DataFrame e salvataggio Excel
    df = pd.DataFrame(data)
    output_path = os.path.join(output_dir, f"sim123_{version_name}.xlsx")
    df.to_excel(output_path, index=False)

    print(f"✅ File Excel salvato in: {output_path}")



def count_client_occurrences(n_vehicles, n_days, assigned_ordered_matrix, sim_sol):
    """
    Conta quante volte ciascun cliente (presente in sim_sol) compare
    nella matrice delle assegnazioni (solution.assigned_ordered_matrix).

    Args:
        n_vehicles (int): numero di veicoli
        n_days (int): numero di giorni
        assigned_ordered_matrix (list of lists): matrice [veicolo][giorno] -> lista clienti
        sim_sol (list of lists): lista clienti per ciascun veicolo

    Returns:
        list of dict: per ciascun veicolo, un dizionario {cliente: conteggio}
    """
    occurrences_per_vehicle = []

    for v in range(n_vehicles):
        client_list = sim_sol[v]  # clienti di riferimento del veicolo
        count_dict = {client: 0 for client in client_list}

        for d in range(n_days):
            clients_day = assigned_ordered_matrix[v, d]  # clienti assegnati quel giorno
            for c in clients_day:
                if c in count_dict:
                    count_dict[c] += 1

        occurrences_per_vehicle.append(count_dict)

    return occurrences_per_vehicle

def export_client_occurrences_to_excel(n_vehicles, n_days, assigned_ordered_matrix, sim_sol, output_path):
    """
    Conta le occorrenze dei clienti per ciascun veicolo e salva i risultati in un file Excel.
    
    Args:
        n_vehicles (int): numero di veicoli
        n_days (int): numero di giorni
        assigned_ordered_matrix (numpy.ndarray): matrice [veicolo][giorno] -> lista clienti
        sim_sol (list of lists): lista clienti per ciascun veicolo
        output_path (str): percorso completo del file Excel da creare
    """
    # Crea cartella se non esiste
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Usa ExcelWriter per scrivere più fogli
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for v in range(n_vehicles):
            client_list = sim_sol[v]
            count_dict = {client: 0 for client in client_list}

            # Conta le occorrenze del cliente nei vari giorni
            for d in range(n_days):
                clients_day = assigned_ordered_matrix[v, d]
                for c in clients_day:
                    if c in count_dict:
                        count_dict[c] += 1

            # Converte in DataFrame
            df = pd.DataFrame({
                "ID Cliente": list(count_dict.keys()),
                "Ripetizioni": list(count_dict.values())
            })

            # Scrive nel foglio corrispondente al veicolo
            sheet_name = f"Veicolo_{v+1}"
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"✅ File Excel creato in: {output_path}")


def old_main(n_vehicles, n_days, n_clients, vehicle_capacity, max_clients_kd, data, distance_matrix, solution_base, solution_new, 
             out_base_occur, out_new_occur, out_opt_base_occur, out_opt_new_occur):

    ''' see how many combos '''
    combos, total = generate_combinations(n_days, n_vehicles)
    # print(f"Totale combinazioni uniche: {total}")  # 1296
    # for idx, combo in enumerate(combos):
    #     print(f"\ncombo {idx}:\n")
    #     for ass in enumerate(combo):
    #         print(ass)

    ''' t_swap_r_k '''

    # test with optimized_VRP solution base
    vrp_sol_base = solve_vrp_day(n_vehicles, n_days, n_clients, vehicle_capacity, max_clients_kd, data, distance_matrix, solution_base)
    sim_vrp_sol_base = def_sim_1_matrix(n_vehicles, n_days, vrp_sol_base.assigned_ordered_matrix)
    sim_vrp_sol_base_clean = sim_matrix_clean(sim_vrp_sol_base)
    # print(f"sol_base sim_1_matrix:\n{sim_vrp_sol_base_clean}")
    int_sim_sol_base = calc_internal_sim(n_vehicles, sim_vrp_sol_base)
    # print("int_sim_1_values sol_base:", int_sim_sol_base)


    opt_vrp_sol_base = t_swap_r_k_worse(n_days, n_vehicles, max_iterations, copy.deepcopy(vrp_sol_base))
    sim_opt_vrp_sol_base = def_sim_1_matrix(n_vehicles, n_days, opt_vrp_sol_base.assigned_ordered_matrix)
    sim_opt_vrp_sol_base_clean = sim_matrix_clean(sim_opt_vrp_sol_base)
    # print(f"opt_sol_base sim_1_matrix:\n{sim_opt_vrp_sol_base_clean}")
    int_sim_opt_sol_base = calc_internal_sim(n_vehicles, sim_opt_vrp_sol_base)
    # print("int_sim_1_values opt_sol_base:", int_sim_opt_sol_base)

    # utils.plot_save_vehi_routes(n_vehicles, n_days, data, vrp_sol_base.assigned_ordered_matrix, path_img_vrp_base)
    # utils.plot_save_vehi_routes(n_vehicles, n_days, data, opt_vrp_sol_base.assigned_ordered_matrix, path_img_opt_vrp_base)


    # test with optimized_VRP solution new
    vrp_sol_new = solve_vrp_day(n_vehicles, n_days, n_clients, vehicle_capacity, max_clients_kd, data, distance_matrix, solution_new)
    sim_vrp_sol_new = def_sim_1_matrix(n_vehicles, n_days, vrp_sol_new.assigned_ordered_matrix)
    sim_vrp_sol_new_clean = sim_matrix_clean(sim_vrp_sol_new)
    # print(f"sol_new sim_1_matrix:\n{sim_vrp_sol_new_clean}")
    int_sim_sol_new = calc_internal_sim(n_vehicles, sim_vrp_sol_new)
    # print("int_sim_1_values sol_new:", int_sim_sol_base)

    opt_vrp_sol_new = t_swap_r_k_worse(n_days, n_vehicles, max_iterations, copy.deepcopy(vrp_sol_new))
    sim_opt_vrp_sol_new = def_sim_1_matrix(n_vehicles, n_days, opt_vrp_sol_new.assigned_ordered_matrix)
    sim_opt_vrp_sol_new_clean = sim_matrix_clean(sim_opt_vrp_sol_new)
    # print(f"opt_sol_new sim_1_matrix:\n{sim_opt_vrp_sol_new_clean}")
    int_sim_opt_sol_new = calc_internal_sim(n_vehicles, sim_opt_vrp_sol_new)
    # print("int_sim_1_values opt_sol_new:", int_sim_opt_sol_new)

    # utils.plot_save_vehi_routes(n_vehicles, n_days, data, vrp_sol_new.assigned_ordered_matrix, path_img_vrp_new)
    # utils.plot_save_vehi_routes(n_vehicles, n_days, data, opt_vrp_sol_new.assigned_ordered_matrix, path_img_opt_vrp_new)

    # measure similarity
    (starting_sim_1_value, starting_sim_1_combos_matrix, starting_sim_1_pairings, starting_sim_1_pair_values) = measure_sim_1(n_vehicles, sim_vrp_sol_base, sim_vrp_sol_new)
    (opt_sim_1_value, opt_sim_1_combos_matrix, opt_sim_1_pairings, opt_sim_1_pair_values) = measure_sim_1(n_vehicles, sim_opt_vrp_sol_base, sim_opt_vrp_sol_new)
    
    print("\n\nint_sim_1_values sol_base:", int_sim_sol_base)
    print("int_sim_1_values sol_new:", int_sim_sol_new)
    print(f"\nsim_1 in starting value: {starting_sim_1_value}\ncombo values: {starting_sim_1_pair_values}")
    print("starting pairings", starting_sim_1_pairings)

    print("\n\nint_sim_1_values opt_sol_base:", int_sim_opt_sol_base)
    print("int_sim_1_values opt_sol_new:", int_sim_opt_sol_new)
    print(f"\nsim_1 in opt value: {opt_sim_1_value}\ncombo values: {opt_sim_1_pair_values}")
    print("opt pairings", opt_sim_1_pairings)
    print("\n\n")

    # print(f"opt_base\n{opt_vrp_sol_base.assigned_ordered_matrix[0]}\n\nopt_new\n{opt_vrp_sol_new.assigned_ordered_matrix[0]}")
    # print(f"INT_SIM\nbase\n{sim_opt_vrp_sol_base_clean} \n\nnew{sim_opt_vrp_sol_new_clean}")
    # occur_vehicle_opt_base = count_client_occurrences(n_vehicles, n_days, opt_vrp_sol_base.assigned_ordered_matrix, sim_opt_vrp_sol_base_clean)
    # occur_vehicle_opt_new = count_client_occurrences(n_vehicles, n_days, opt_vrp_sol_new.assigned_ordered_matrix, sim_opt_vrp_sol_new_clean)
    # print(f"CLIENT OCCURRENCES\n base\n{occur_vehicle_opt_base}\n\nnew\n{occur_vehicle_opt_new}")

    export_client_occurrences_to_excel(n_vehicles, n_days, vrp_sol_base.assigned_ordered_matrix, sim_vrp_sol_base_clean, out_base_occur)
    export_client_occurrences_to_excel(n_vehicles, n_days, vrp_sol_new.assigned_ordered_matrix, sim_vrp_sol_new_clean, out_new_occur)


    export_client_occurrences_to_excel(n_vehicles, n_days, opt_vrp_sol_base.assigned_ordered_matrix, sim_opt_vrp_sol_base_clean, out_opt_base_occur)
    export_client_occurrences_to_excel(n_vehicles, n_days, opt_vrp_sol_new.assigned_ordered_matrix, sim_opt_vrp_sol_new_clean, out_opt_new_occur)


    return


# Esempio
if __name__ == "__main__":

    # seed
    seed = 42 
    random.seed(seed)
    np.random.seed(seed)
    random2.seed(seed)

    # Demand fluctuation parameters
    total_mode = 0                 # 0 = totale costante, 1 = può variare entro capacità
    fluct_mode = "compensated"     # "compensated", "mixed", "uniform"
    client_affected_pct = 1        # % di clienti influenzati (0-1)
    variance_pct = 0.5             # ampiezza fluttuazione (%(0-1) rispetto alla domanda)
    distr_type = "poisson"         # "gamma" o "poisson"
    margin_pct = 0.1               # % di margine (0-1)

    # similarity optimizer parameters:
    max_iterations = 5000

    # save data paths:
    path_data_base = f"data/p02.txt"
    path_data_new = f"src/similarity_optimizer_test/test_p02.txt"
    # percorso assoluto della cartella dove si trova il file corrente
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(BASE_DIR, "similarity_optimizer_test")
    # output_dir = "similarity_optimizer_test"
    # path_img_vrp_base = os.path.join(output_dir, "vrp_sol_base" + ".jpg")
    # path_img_opt_vrp_base = os.path.join(output_dir, "opt_vrp_sol_base" + ".jpg")
    # path_data_new = os.path.join(output_dir, "test_p02" + ".txt")
    # path_img_vrp_new = os.path.join(output_dir, "vrp_sol_new" + ".jpg")
    # path_img_opt_vrp_new = os.path.join(output_dir, "opt_vrp_sol_new" + ".jpg")
    # out_base_occur = os.path.join(output_dir, "sol_base_occur" + ".xlsx")
    # out_new_occur = os.path.join(output_dir, "sol_new_occur" + ".xlsx")
    # out_opt_base_occur = os.path.join(output_dir, "opt_sol_base_occur" + ".xlsx")
    # out_opt_new_occur = os.path.join(output_dir, "opt_sol_new_occur" + ".xlsx")
    

    # Prepare data
    distance_type = 1 
    (n_vehicles, n_days, vehicle_capacity,
      data, sorted_data, n_clients, max_clients_kd, first_data_index,
        distance_matrix, distance_matrix_adjusted, closeness_matrix) = \
        utils.data_preparation(path_data_base, distance_type)

    '''INITIAL SOLUTION'''
    solution_base = algorithms.assign_route.assign_to_1_vehicle_algorithm(
        n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, sorted_data,
          distance_matrix, distance_matrix_adjusted, closeness_matrix)
   
    ''' INSTANCE NEW '''
    # Create new instances (demand fluctuation)
    data_new = utils.create_new_dataset(
        path_data_base, path_data_new,
        data, first_data_index, vehicle_capacity, n_vehicles, n_days,
        distance_type,
        total_mode, fluct_mode, client_affected_pct, variance_pct, distr_type, margin_pct,
        )
    sorted_data_new = utils.sort_data(data_new)

    # Use existing dataset
    # (n_vehicles, n_days, vehicle_capacity,
    #   data_new, sorted_data_new, n_clients, max_clients_kd, first_data_index,
    #     distance_matrix, distance_matrix_adjusted, closeness_matrix) = \
    #     utils.data_preparation(path_data_new, distance_type)
    
    solution_new = algorithms.assign_route.assign_to_1_vehicle_algorithm(
        n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, sorted_data_new,
          distance_matrix, distance_matrix_adjusted, closeness_matrix)
   
    ''' SOLVE VRP '''
    vrp_sol_base = solve_vrp_day(n_vehicles, n_days, n_clients, vehicle_capacity, max_clients_kd, data, distance_matrix, solution_base)
    vrp_sol_new = solve_vrp_day(n_vehicles, n_days, n_clients, vehicle_capacity, max_clients_kd, data, distance_matrix, solution_new)
    # print("\n\nbase")
    # print(vrp_sol_base.assigned_ordered_matrix)
    # print("\n\nnew")
    # print(vrp_sol_new.assigned_ordered_matrix)

    
    test_t_swap_r_k_versions(n_days, n_vehicles, vrp_sol_base, vrp_sol_new, output_dir)

    # old_main(n_vehicles, n_days, n_clients, vehicle_capacity, max_clients_kd, data, distance_matrix, solution_base, solution_new, 
            #  out_base_occur, out_new_occur, out_opt_base_occur, out_opt_new_occur)
