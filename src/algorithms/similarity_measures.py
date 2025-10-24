import copy
import numpy as np
import scipy
from scipy.optimize import linear_sum_assignment
import json
import classes




''' similarity measures '''

def measure_sim_1(n_vehicles, sim_1_base, sim_1_new):

    # measure similar clients for each combination vehicle_base-vehicle_new:
    sim_1_combinations_matrix = np.zeros((n_vehicles, n_vehicles), dtype=float)
    
    for vehicle_base in range(n_vehicles):
        tot_clients_in_v_base = len(sim_1_base[vehicle_base])

        if tot_clients_in_v_base == 0:
            for vehicle_new in range(n_vehicles):
                sim_1_combinations_matrix[vehicle_base, vehicle_new] = 0

        for vehicle_new in range(n_vehicles):
            # find common_clients for each combination v_base-v_new:
            sim_1_combinations_matrix[vehicle_base, vehicle_new] = len(np.intersect1d(sim_1_base[vehicle_base], sim_1_new[vehicle_new]))
            # calculate sim_1_measure = common_clients / tot_clients_base
            sim_1_combinations_matrix[vehicle_base, vehicle_new] = (sim_1_combinations_matrix[vehicle_base, vehicle_new])/tot_clients_in_v_base
    
    # find best combinations:
    # linear_sum_assignment minimizza di default → usiamo il negativo per massimizzare
    row_ind, col_ind = linear_sum_assignment(-sim_1_combinations_matrix)

    # output data:
    sim_1_measures = sim_1_combinations_matrix[row_ind, col_ind]
    sim_1_value = sim_1_measures.min()
    sim_1_vehicle_pairings = list(zip(row_ind, col_ind))
    sim_1_vehicle_pairings = clean_np_ints_pairings(sim_1_vehicle_pairings)

    return (sim_1_value, sim_1_combinations_matrix, sim_1_vehicle_pairings, sim_1_measures)


def measure_sim_2(n_vehicles, n_days, sim_2_base, sim_2_new):

    # measure similar clients for each combination vehicle_base-vehicle_new:
    sim_2_combinations_matrix = np.zeros((n_vehicles, n_vehicles), dtype=float)
    
    for vehicle_base in range(n_vehicles):
        sim_2_matrix = np.zeros((n_vehicles, n_days), dtype=float)

        for vehicle_new in range(n_vehicles):

            for day in range(n_days):
                cl_sequences_vd_base = sim_2_base[vehicle_base, day]
                cl_sequences_vd_new = sim_2_new[vehicle_new, day]
                print("cl_sequences_vd_base", cl_sequences_vd_base)
                print("cl_sequences_vd_new", cl_sequences_vd_new)
                cl_sequences_vd_base = clean_np_ints(cl_sequences_vd_base)
                cl_sequences_vd_new  = clean_np_ints(cl_sequences_vd_new)
                print("cl_sequences_vd_base", cl_sequences_vd_base)
                print("cl_sequences_vd_new", cl_sequences_vd_new)
                
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


def measure_sim_3(n_vehicles, n_days, sim_3_base, sim_3_new):

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


''' prepare data '''

def def_sim_1_matrix(n_vehicles, n_days, solution):

    assigned_clients = copy.deepcopy(solution.assigned_ordered_matrix)
    sim_1_matrix = np.empty(n_vehicles, dtype=object)
    
    for vehicle in range(n_vehicles):
        clients_in_v = []

        for day in range(n_days):
            clients_in_vd = assigned_clients[vehicle, day]
            clients_in_vd = clients_in_vd[clients_in_vd != 0]

            for client in range(len(clients_in_vd)):
                if client in clients_in_v:
                    continue
                clients_in_v.append(client)

        sim_1_matrix [vehicle] = clients_in_v

    return sim_1_matrix


def def_sim_2_matrix(n_vehicles, n_days, solution):

    assigned_clients = copy.deepcopy(solution.assigned_ordered_matrix)
    sim_2_matrix = np.empty((n_vehicles, n_days), dtype=object)

    for vehicle in range(n_vehicles):
        for day in range(n_days):

            # clean client list:
            # clients_in_vd = assigned_clients[vehicle, day]
            # while clients_in_vd[-1] == 0:
            #     clients_in_vd.pop()
            # clients_in_vd.append(0)

            clients_in_vd = assigned_clients[vehicle, day]
            # Remove trailing zeros
            nonzero_indices = np.nonzero(clients_in_vd)[0]
            if len(nonzero_indices) > 0:
                last_nonzero = nonzero_indices[-1] + 1
                clients_in_vd = clients_in_vd[:last_nonzero]
            else:
                clients_in_vd = np.array([], dtype=int)

            # Append a zero at the end
            clients_in_vd = np.append(clients_in_vd, 0)


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


def def_sim_3_matrix(n_vehicles, n_days, solution):

    assigned_clients = copy.deepcopy(solution.assigned_ordered_matrix)
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


''' other functions '''

def clean_np_ints(obj):
    if isinstance(obj, np.integer):        # converte np.int64 → int
        return int(obj)
    elif isinstance(obj, list):            # esplora liste
        return [clean_np_ints(x) for x in obj]
    else:
        return obj
    
def clean_np_ints_pairings(obj):
    """Converte ricorsivamente np.int64 (e simili) in int Python puri."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, list):
        return [clean_np_ints(x) for x in obj]
    elif isinstance(obj, tuple):
        return tuple(clean_np_ints(x) for x in obj)
    elif isinstance(obj, dict):
        return {clean_np_ints(k): clean_np_ints(v) for k, v in obj.items()}
    else:
        return obj
    
def get_max_seq_len(seq_group):
    if seq_group and seq_group[-1]:
        last_seq = seq_group[-1][0]
        return len(last_seq) if isinstance(last_seq, (list, np.ndarray)) else 0
    return 0


''' test '''

# # load solutions
# def load_solution(path):
#     with open(path, "r") as f:
#         data = json.load(f)

#     # Ricostruisci l’oggetto Solution
#     sol = classes.Solution(
#         OBJ_tot_dist=data["OBJ_tot_dist"],
#         assigned_ordered_matrix=np.array(data["assigned_ordered_matrix"]),
#         not_assigned_list=data["not_assigned_list"],
#         transp_demand_matrix=np.array(data["transp_demand_matrix"]),
#         route_dist_matrix=np.array(data["route_dist_matrix"])
#     )

#     return sol

# def main():
#     base_path = 
#     base_sol = load_solution
    

# if __name__ == "__main__":
#     main()