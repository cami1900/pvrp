import numpy as np
import copy
from scipy.optimize import linear_sum_assignment

from algorithms.similarity_measures import (clean_np_ints, get_max_seq_len)


''' sim 2 '''

def def_sim_2_matrix(n_vehicles, n_days, assigned_clients):

    # assigned_clients = copy.deepcopy(solution.assigned_ordered_matrix)
    sim_2_matrix = np.empty((n_vehicles, n_days), dtype=object)

    for vehicle in range(n_vehicles):
        for day in range(n_days):

            # inside the loops for vehicle/day — replace your current cleaning block with this:
            clients = assigned_clients[vehicle, day]

            # assicurati di avere un numpy array
            clients = np.asarray(clients, dtype=int)

            # estrai solo i clienti non-zero (toglie sia zeri iniziali che finali/padding)
            nonzeros = clients[clients != 0]

            if nonzeros.size == 0:
                # nessun cliente: tieni due zeri (inizio + fine)
                clients_in_vd = np.array([0, 0], dtype=int)
            else:
                # inverti SOLO la sequenza dei clienti reali
                reversed_clients = nonzeros[::-1]

                # rimetti uno zero davanti e uno alla fine
                clients_in_vd = np.concatenate(([0], reversed_clients, [0])).astype(int)

            # print("clients_in_vd", clients_in_vd)


            # clients_in_vd = assigned_clients[vehicle, day]
            # # Remove trailing zeros
            # nonzero_indices = np.nonzero(clients_in_vd)[0]
            # if len(nonzero_indices) > 0:
            #     last_nonzero = nonzero_indices[-1] + 1
            #     clients_in_vd = clients_in_vd[:last_nonzero]
            # else:
            #     clients_in_vd = np.array([], dtype=int)

            # # Append a zero at the end
            # clients_in_vd = np.append(clients_in_vd, 0)
            # print("clients_in_vd", clients_in_vd)


            max_clients_vd = len(clients_in_vd)
            cl_sequences_vd = []

            for n_clients_route in range(2, max_clients_vd + 1): # for each possible route lengths
                n_clients_sequences = []

                for start in range(max_clients_vd + 1 - n_clients_route): # for each possible start node
                    start_sequences = []

                    for idx in range(start, start + n_clients_route): # for each client in the range 
                        start_sequences.append(clients_in_vd[idx])
    
                    n_clients_sequences.append(start_sequences)
                
                cl_sequences_vd.append(n_clients_sequences)
            
            sim_2_matrix[vehicle, day] = cl_sequences_vd

    return sim_2_matrix

def measure_sim_2_onedir(n_vehicles, n_days, sim_2_base, sim_2_new):

    # measure similar clients for each combination vehicle_base-vehicle_new:
    sim_2_combinations_matrix = np.zeros((n_vehicles, n_vehicles), dtype=float)
    
    for vehicle_base in range(n_vehicles):
        sim_2_matrix = np.zeros((n_vehicles, n_days), dtype=float)

        for vehicle_new in range(n_vehicles):

            for day in range(n_days):
                cl_sequences_vd_base = sim_2_base[vehicle_base, day]
                cl_sequences_vd_new = sim_2_new[vehicle_new, day]
                # print("cl_sequences_vd_base", cl_sequences_vd_base)
                # print("cl_sequences_vd_new", cl_sequences_vd_new)
                cl_sequences_vd_base = clean_np_ints(cl_sequences_vd_base)
                cl_sequences_vd_new  = clean_np_ints(cl_sequences_vd_new)
                # print("cl_sequences_vd_base", cl_sequences_vd_base)
                # print("cl_sequences_vd_new", cl_sequences_vd_new)
                
                # max_len_in_vd_base = len(cl_sequences_vd_base[-1][0]) # last cl_sequest == longest 
                # max_len_in_vd_new = len(cl_sequences_vd_new[-1][0]) # last cl_sequest == longest 
                max_len_in_vd_base = get_max_seq_len(cl_sequences_vd_base)
                max_len_in_vd_new  = get_max_seq_len(cl_sequences_vd_new)

                max_len_in_vd = min(max_len_in_vd_base, max_len_in_vd_new)
                max_common_sequence = 0 # [0, 0] length max_sequence, n_times 
                # n_lengths_base = len(cl_sequences_vd_base)
                # n_lengths_new = len(cl_sequences_vd_new)

                if max_len_in_vd_base == 0:
                    for n_clients_route in range(max_len_in_vd-1):
                        sim_2_matrix[vehicle_new, day] = 0

                for n_clients_route in range(max_len_in_vd-1):

                    base_sequences = [tuple(seq) for seq in cl_sequences_vd_base[n_clients_route]]
                    new_sequences  = [tuple(seq) for seq in cl_sequences_vd_new[n_clients_route]]


                    n_common_sequences = len(set(base_sequences) & set(new_sequences))

                    # n_common_sequences = len(set(cl_sequences_vd_base[n_clients_route]) & set(cl_sequences_vd_new[n_clients_route]))
                    len_common_sequences = n_clients_route +1 # ????? (prima era +2)

                    if n_common_sequences == 0:
                        continue

                    # # max_common_sequence[0] = len_common_sequences
                    # # max_common_sequence[1] = n_common_sequences 

                    max_common_sequence = len_common_sequences    # ?????
                    sim_2_matrix[vehicle_new, day] = max_common_sequence/max_len_in_vd_base 

            sim_mean_per_vehicle = np.mean(sim_2_matrix, axis=1)
            sim_2_combinations_matrix[vehicle_base, :] = sim_mean_per_vehicle

    # find best combinations:
    # linear_sum_assignment minimizza di default → usiamo il negativo per massimizzare
    row_ind, col_ind = linear_sum_assignment(-sim_2_combinations_matrix)

    # output data:
    sim_2_measures = sim_2_combinations_matrix[row_ind, col_ind]
    sim_2_value = sim_2_measures.min()
    sim_2_vehicle_pairings = list(zip(row_ind, col_ind))
    
    return (sim_2_value, sim_2_combinations_matrix, sim_2_vehicle_pairings, sim_2_measures)

def measure_sim_2(n_vehicles, n_days, base_ass_matrix, new_ass_matrix):
    
    new_ass_matrix_rev = np.flip(new_ass_matrix, axis=2)

    sim_2_base = def_sim_2_matrix(n_vehicles, n_days, base_ass_matrix)
    sim_2_new = def_sim_2_matrix(n_vehicles, n_days, new_ass_matrix)
    sim_2_new_rev = def_sim_2_matrix(n_vehicles, n_days, new_ass_matrix_rev)    

    (sim_2_value, sim_2_combinations_matrix, sim_2_vehicle_pairings, sim_2_measures) = \
         measure_sim_2_onedir(n_vehicles, n_days, sim_2_base, sim_2_new)
    (sim_2_value_rev, sim_2_combinations_matrix_rev, sim_2_vehicle_pairings_rev, sim_2_measures_rev) = \
         measure_sim_2_onedir(n_vehicles, n_days, sim_2_base, sim_2_new_rev)

    # print("\nsim_2_value", sim_2_value)
    # print("sim_2_combinations_matrix\n", sim_2_combinations_matrix)
    # print("sim_2_vehicle_pairings", sim_2_vehicle_pairings)
    # print("sim_2_measures", sim_2_measures)

    # print("\nsim_2_value", sim_2_value_rev)
    # print("sim_2_combinations_matrix\n", sim_2_combinations_matrix_rev)
    # print("sim_2_vehicle_pairings", sim_2_vehicle_pairings_rev)
    # print("sim_2_measures", sim_2_measures_rev)

    if sim_2_value > sim_2_value_rev:
        dir_type = "same"
        return (dir_type, sim_2_value, sim_2_combinations_matrix, sim_2_vehicle_pairings, sim_2_measures)
    else: 
        dir_type = "rev"
        return (dir_type, sim_2_value_rev, sim_2_combinations_matrix_rev, sim_2_vehicle_pairings_rev, sim_2_measures_rev)


''' sim 3 '''

def def_sim_3_matrix(n_vehicles, n_days, assigned_clients):

    # assigned_clients = copy.deepcopy(solution.assigned_ordered_matrix)
    sim_3_matrix = np.empty((n_vehicles, n_days), dtype=object)

    for vehicle in range(n_vehicles):
        for day in range(n_days):
            client_list = assigned_clients[vehicle, day]
            edges = []

            for idx in range(len(client_list) - 1):
                client_i = client_list[idx]
                client_j = client_list[idx+1]
                if (client_i, client_j) != (0, 0):   # Escludi (0,0)
                    edges.append((client_i, client_j))

            sim_3_matrix[vehicle, day] = edges

    return sim_3_matrix

def measure_sim_3_onedir(n_vehicles, n_days, sim_3_base, sim_3_new):

    # measure similar clients for each combination vehicle_base-vehicle_new:
    sim_3_combinations_matrix = np.zeros((n_vehicles, n_vehicles), dtype=float)
    
    for vehicle_base in range(n_vehicles):
        sim_3_matrix = np.zeros((n_vehicles, n_days), dtype=float)

        for vehicle_new in range(n_vehicles):

            for day in range(n_days):
                tot_arcs_in_vd_base = len(sim_3_base[vehicle_base, day])

                if tot_arcs_in_vd_base == 0:
                    sim_3_matrix[vehicle_new, day] = 0
                    continue

                # common_arcs = len(np.intersect1d(sim_3_base[vehicle_base, day],sim_3_new[vehicle_new, day] ))
                base_edges = set(sim_3_base[vehicle_base, day])
                new_edges = set(sim_3_new[vehicle_new, day])
                common_arcs = len(base_edges & new_edges)  # "&" = intersezione
                # print("base_edges\n", base_edges)
                # print("new_edges\n", new_edges)
                # print("common_arcs\n", common_arcs)
                sim_3_matrix[vehicle_new, day] = common_arcs / tot_arcs_in_vd_base

            sim_mean_per_vehicle = np.mean(sim_3_matrix, axis=1)
            sim_3_combinations_matrix[vehicle_base, :] = sim_mean_per_vehicle
                
    # find best combinations:
    # linear_sum_assignment minimizza di default → usiamo il negativo per massimizzare
    row_ind, col_ind = linear_sum_assignment(-sim_3_combinations_matrix)

    # output data:
    sim_3_measures = sim_3_combinations_matrix[row_ind, col_ind]
    sim_3_value = sim_3_measures.min()
    sim_3_vehicle_pairings = list(zip(row_ind, col_ind))

    return (sim_3_value, sim_3_combinations_matrix, sim_3_vehicle_pairings, sim_3_measures)

def measure_sim_3(n_vehicles, n_days, base_ass_matrix, new_ass_matrix):

    new_ass_matrix_rev = np.flip(new_ass_matrix, axis=2)

    sim_3_base = def_sim_3_matrix(n_vehicles, n_days, base_ass_matrix)
    sim_3_new = def_sim_3_matrix(n_vehicles, n_days, new_ass_matrix)
    sim_3_new_rev = def_sim_3_matrix(n_vehicles, n_days, new_ass_matrix_rev)   

    (sim_3_value, sim_3_combinations_matrix, sim_3_vehicle_pairings, sim_3_measures) = \
         measure_sim_3_onedir(n_vehicles, n_days, sim_3_base, sim_3_new)
    (sim_3_value_rev, sim_3_combinations_matrix_rev, sim_3_vehicle_pairings_rev, sim_3_measures_rev) = \
         measure_sim_3_onedir(n_vehicles, n_days, sim_3_base, sim_3_new_rev)

    # print("\nsim_3_value", sim_3_value)
    # print("sim_3_combinations_matrix\n", sim_3_combinations_matrix)
    # print("sim_3_vehicle_pairings", sim_3_vehicle_pairings)
    # print("sim_3_measures", sim_3_measures)

    # print("\nsim_3_value", sim_3_value_rev)
    # print("sim_3_combinations_matrix\n", sim_3_combinations_matrix_rev)
    # print("sim_3_vehicle_pairings", sim_3_vehicle_pairings_rev)
    # print("sim_3_measures", sim_3_measures_rev)

    if sim_3_value > sim_3_value_rev:
        dir_type = "same"
        return (dir_type, sim_3_value, sim_3_combinations_matrix, sim_3_vehicle_pairings, sim_3_measures)
    else: 
        dir_type = "rev"
        return (dir_type, sim_3_value_rev, sim_3_combinations_matrix_rev, sim_3_vehicle_pairings_rev, sim_3_measures_rev)


''' other '''

def clean_int64(obj):
    if isinstance(obj, list):
        return [clean_int64(x) for x in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    else:
        return obj

def sim_2_matrix_clean(sim_matrix_sol, n_days, n_vehicles):
    def clean_element(x):
        if isinstance(x, list):
            return [clean_element(i) for i in x]
        elif isinstance(x, np.integer):
            return int(x)
        else:
            return x

    sim_matrix_sol_clean = [
        [
            clean_element(sim_matrix_sol[vehicle][day])
            for vehicle in range(n_vehicles)
        ]
        for day in range(n_days)
    ]
    return sim_matrix_sol_clean



# Esempio
if __name__ == "__main__":
    print("hello")

    n_vehicles = 2
    n_days = 3

    base_ass_matrix = np.array([[[0, 1, 2, 3, 4, 5, 0, 0, 0, 0], 
                                 [0, 3, 4, 5, 6, 7, 8, 0, 0, 0], 
                                 [0, 1, 2, 7, 8, 9, 10, 11, 0, 0]],
                                [[0, 4, 5, 9, 11, 12, 13, 0, 0, 0], 
                                 [0, 1, 2, 13, 14, 15, 16, 17, 0, 0],
                                 [0, 4, 5, 6, 15, 16, 17, 0, 0, 0]]], 
                                 dtype=int)
    
    new_ass_matrix = np.array([[[0, 5, 4, 3, 2, 1, 0, 0, 0, 0], 
                                [0, 3, 4, 5, 6, 15, 16, 17, 0, 0], 
                                [0, 2, 1, 7, 8, 11, 10, 9, 0, 0]],
                               [[0, 4, 5, 11, 9, 13, 12, 0, 0, 0], 
                                [0, 1, 2, 13, 14, 7, 8, 0, 0, 0],
                                [0, 17, 16, 15, 6, 5, 4, 0, 0, 0]]], 
                                dtype=int)
    new_ass_matrix_rev = np.flip(new_ass_matrix, axis=2)
    # print("reversed_matrix", new_ass_matrix_rev)

    (dir_type, sim_2_value, sim_2_combinations_matrix, sim_2_vehicle_pairings, sim_2_measures) = \
        measure_sim_2(n_vehicles, n_days, base_ass_matrix, new_ass_matrix)
    
    print("\ndir_type", dir_type)
    print("sim_2_value", sim_2_value)

    (dir_type, sim_3_value, sim_3_combinations_matrix, sim_3_vehicle_pairings, sim_3_measures) = \
        measure_sim_3(n_vehicles, n_days, base_ass_matrix, new_ass_matrix)
    
    print("\ndir_type", dir_type)
    print("sim_2_value", sim_3_value)
    print("\n\n")

