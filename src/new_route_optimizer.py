from py2opt142.py2opt.routefinder import RouteFinder    # sarebbe da sostituire con la nuova versione (2-3opt)

import algorithms.assign_route
import utils
import algorithms
from algorithms.feasibility_function_POOP import (check_feasibility_1vehicle, check_feasibility_pvrp)
from algorithms.assign_route import calculate_tot_dist 
import conf
import classes
import numpy as np
import pandas as pd
import copy
import matplotlib.pyplot as plt

import logging
import random
import random2

# VRP solver
from tabulate import tabulate
from vrplib import read_solution
import math
import pyvrp
from pyvrp import read, solve
from pyvrp.plotting import (
    plot_coordinates,
    plot_instance,
    plot_result,
    plot_route_schedule,
)
from pyvrp.stop import MaxIterations, MaxRuntime
# from pyvrp._pyvrp import StoppingCriterion

random.seed(42)
random2.seed(42)
np.random.seed(42)

import os
os.environ["OMP_NUM_THREADS"] = "1"



# Inizializza la tabella globale (4 algoritmi x 4 posizioni)
score_table_global = np.zeros((4, 4), dtype=int)
algo_names = ["dist_2opt", "dist_3opt", "dist_2_3opt", "dist_3_2opt"]


''' FUNCTIONS '''

def route_distance(distance_matrix, route):

    distance = sum(distance_matrix[route[i], route[i + 1]] for i in range(len(route) - 1))

    return distance

def route_demand(data, route):

    transported_demand = sum(data[route[i], conf.DEMAND_INDEX] for i in range(len(route)))

    return transported_demand

''' 2-opt '''
def two_opt(original_route, original_distance, distance_matrix):
    """Applica l'algoritmo 2-opt per ottimizzare la route (il deposito resta fisso)."""
    best_route = original_route.copy()
    best_distance = original_distance.copy()
    # improved = True

    # while improved:
    #     improved = False
    for i in range(1, len(original_route) - 2):
        for j in range(i + 1, len(original_route) - 1):
            # Genera una nuova route invertendo il segmento [i:j]
            new_route = original_route.copy()
            new_route[i:j+1] = original_route[j:i-1:-1]
            new_distance = route_distance(distance_matrix, new_route)
            if new_distance < best_distance:
                best_route = new_route
                best_distance = new_distance
                # improved = True

    return best_route, best_distance

''' 3-opt '''
def three_opt(original_route, original_distance, distance_matrix):
    """Applica l'algoritmo 2-opt per ottimizzare la route (il deposito resta fisso)."""
    best_route = original_route.copy()
    best_distance = original_distance.copy()

    seen_routes = {tuple(original_route)}  # la route iniziale
    new_routes = []

    # improved = True

    # while improved:
    #     improved = False
    for i in range(1, len(original_route) - 3):
        for j in range(i + 1, len(original_route) - 2):
            for k in range(j + 1, len(original_route) - 1):
                segments = [
                    original_route[0:i],
                    original_route[i:j],
                    original_route[j:k],
                    original_route[k:]
                ]

                # Tutte le possibili combinazioni (alcune inversioni)    
                options = [
                    np.concatenate([segments[0], segments[1], segments[2], segments[3]]),
                    np.concatenate([segments[0], segments[1][::-1], segments[2], segments[3]]),
                    np.concatenate([segments[0], segments[1], segments[2][::-1], segments[3]]),
                    np.concatenate([segments[0], segments[1][::-1], segments[2][::-1], segments[3]]),
                    np.concatenate([segments[0], segments[2], segments[1], segments[3]]),
                    np.concatenate([segments[0], segments[2], segments[1][::-1], segments[3]]),
                    np.concatenate([segments[0], segments[2][::-1], segments[1], segments[3]]),
                    np.concatenate([segments[0], segments[2][::-1], segments[1][::-1], segments[3]])
                ]

                unique_options = []
                for opt in options:
                    t = tuple(opt)
                    if t not in seen_routes:
                        seen_routes.add(t)
                        unique_options.append(opt)
                        new_routes.append(opt)
                
                for new_route in unique_options:
                        new_distance = route_distance(distance_matrix, new_route)
                        if new_distance < best_distance:
                            best_route = new_route
                            best_distance = new_distance
                            # improved = True

    return best_route, best_distance

''' optimize routes '''
def optimize_route(n_vehicles, n_days, distance_matrix, solution):

    new_solution = copy.deepcopy(solution)
    for vehicle in range(n_vehicles):
        for day in range(n_days):
            # print(f"\nv{vehicle}, d{day}")
            route = copy.deepcopy(new_solution.assigned_ordered_matrix[vehicle][day])
            idx = np.where(route == 0)[0][2]    # remove final zeros
            original_route = route[:idx]
            original_distance = route_distance(distance_matrix, original_route)
            # print("original distance:", original_distance)
            # optmize
            best_2opt, dist_2opt = two_opt(original_route, original_distance, distance_matrix)
            best_3opt, dist_3opt = three_opt(original_route, original_distance, distance_matrix)
            # 2-opt + 3-opt
            best_2_3opt, dist_2_3opt = three_opt(best_2opt, dist_2opt, distance_matrix)
            best_3_2opt, dist_3_2opt = three_opt(best_3opt, dist_3opt, distance_matrix)
            # print("dist_2opt", dist_2opt)
            # print("dist_3opt", dist_3opt)
            # print("dist_2_3opt", dist_2_3opt)
            # print("dist_3_2opt", dist_3_2opt)
            update_score_table(original_distance, dist_2opt, dist_3opt, dist_2_3opt, dist_3_2opt)

            if dist_2_3opt < original_distance or dist_3_2opt < original_distance:
                if dist_2_3opt < dist_3_2opt:   # dist_2_3opt better
                    # print("dist_2_3opt")
                    # print(f"original: {original_route}, \noptimized: {best_2_3opt}")
                    # print(f"original: {original_distance}, optimized: {dist_2_3opt}")
                    for client in range(len(best_2_3opt)):
                        new_solution.assigned_ordered_matrix[vehicle][day][client] = best_2_3opt[client]
                    new_solution.route_dist_matrix[vehicle][day] = dist_2_3opt
                    # print(new_solution.route_dist_matrix[vehicle][day])
                else:                           # dist_3_2opt better
                    # print("dist_3_2opt")
                    for client in range(len(best_3_2opt)):
                        new_solution.assigned_ordered_matrix[vehicle][day][client] = best_3_2opt[client]
                    new_solution.route_dist_matrix[vehicle][day] = dist_3_2opt

    return new_solution

def update_score_table_OLD(original_distance, d2, d3, d23, d32):
    """
    Aggiorna la tabella punteggi globale in base alle distanze fornite.
    Assegna +1 in base alla posizione relativa (la più piccola = migliore).
    """
    global score_table_global

    distances = np.array([d2, d3, d23, d32])
    tol = 1e-6

    # Se nessuno migliora, non aggiornare
    improved = distances < original_distance - tol
    if not np.any(improved):
        return

    # Ordina le distanze in modo crescente
    sorted_vals = np.sort(distances)
    ranks = np.argsort(distances)

    # Calcola la "posizione" per ogni algoritmo
    current_rank = 0
    for pos in range(len(distances)):
        if pos == 0 or abs(sorted_vals[pos] - sorted_vals[pos - 1]) > tol:
            current_rank += 1

        # assegna +1 agli algoritmi con questa distanza (entro tolleranza)
        idx_same = np.where(abs(distances - sorted_vals[pos]) <= tol)[0]
        for idx in idx_same:
            score_table_global[idx, current_rank - 1] += 1

def update_score_table(original_distance, d2, d3, d23, d32):
    global score_table_global

    distances = np.array([d2, d3, d23, d32])
    tol = 1e-6

    # Se nessuno migliora l'originale → non aggiornare
    if np.all(distances >= original_distance - tol):
        return

    # Ordina le distanze (crescente)
    sorted_unique_vals = np.unique(np.round(distances, 6))
    current_rank = 0

    for val in sorted_unique_vals:
        # assegna rank solo se migliore dell'originale
        if val < original_distance - tol:
            current_rank += 1
            idx_same = np.where(abs(distances - val) <= tol)[0]
            for idx in idx_same:
                score_table_global[idx, current_rank - 1] += 1


''' optimize day (VRP) '''
class MaxIters:
    def __init__(self, max_iters):
        self.max_iters = max_iters
        self.counter = 0

    def __call__(self, best_cost):
        self.counter += 1
        return self.counter >= self.max_iters

def crete_new_sol_empty(n_vehicles, n_days, n_clients, max_clients_kd):

    assigned_ordered_matrix = np.zeros((n_vehicles, n_days, max_clients_kd), dtype=int)
    not_assigned_list = np.zeros((n_clients), dtype=int)
    transp_demand_matrix = np.zeros((n_vehicles, n_days), dtype=int)
    route_dist_matrix = np.zeros((n_vehicles, n_days), dtype=float)
    OBJ_tot_dist = 0

    new_solution = classes.Solution(OBJ_tot_dist, assigned_ordered_matrix, not_assigned_list, transp_demand_matrix, route_dist_matrix)

    return new_solution

def solve_vrp_day(n_vehicles, n_days, n_clients, vehicle_capacity, max_clients_kd, data, distance_matrix, solution):

    # new_solution = copy.deepcopy(solution)
    new_solution = crete_new_sol_empty(n_vehicles, n_days, n_clients, max_clients_kd)

    ''' create the model '''    # prepare needed data and add them to the model
    depot = (data[0, conf.X_COORD_INDEX], data[0, conf.Y_COORD_INDEX])  # coordinate del deposito

    for day in range(n_days):
        clients = []
        for vehicle in range(n_vehicles):
            clients_vd = solution.assigned_ordered_matrix[vehicle][day]
            for cl_idx in clients_vd:
                if cl_idx != 0: # ignora il depot
                    x = data[cl_idx, conf.X_COORD_INDEX]
                    y = data[cl_idx, conf.Y_COORD_INDEX]
                    demand = data[cl_idx, conf.DEMAND_INDEX]
                    clients.append({
                        "id": int(cl_idx),
                        "x": float(x),
                        "y": float(y),
                        "demand": float(demand)
                    })

        model = pyvrp.Model()
        # aggiungi deposito
        depot_loc = model.add_depot(*depot, name="Depot")
        # aggiungi clienti
        client_map = {}  # chiave: indice interno PyVRP, valore: indice originale in `data`
        for i, c in enumerate(clients):
            client_obj = model.add_client(
                c["x"],
                c["y"],
                delivery=[int(c["demand"])],
                pickup=[],
                service_duration=0,
                name=f"C{c['id']}"
            )
            client_map[i+1] = c["id"]  # +1 perché PyVRP usa 0 come deposito
        # crea matrice distanze -->     potresti già avere la funzione che estrae la matrice distanze di clienti selezionati!!!!!
        locations = model.locations
        for i in locations:
            for j in locations:
                if i != j:
                    dist = math.hypot(i.x - j.x, i.y - j.y)
                    model.add_edge(i, j, distance=dist, duration=dist)
        #definisci veicoli
        model.add_vehicle_type(
            num_available=n_vehicles,
            capacity=[vehicle_capacity],
            fixed_cost=0,
            unit_distance_cost=1,
            name="Truck"
        )

        ''' solve VRP '''
        stop_criterion = MaxIters(500)
        result = model.solve(stop=stop_criterion, seed=0, collect_stats=False, display=False)

        # print 
        new_routes = []
        for route in result.best.routes():
            mapped_route = []
            for c in route:
                if isinstance(c, int):
                    if c == 0:
                        mapped_route.append(0)  # depot
                    else:
                        mapped_route.append(client_map[c])
                else:
                    mapped_route.append(client_map[c.index])
            new_routes.append(mapped_route)

        ''' update solution '''
        
        # save data
        original_distance = 0
        for vehicle in range(len(new_routes)):
            selected_route = new_routes[vehicle]    # puoi scegliere in base alla similarità!!!!!!
            new_solution.assigned_ordered_matrix[vehicle][day][1:len(selected_route)+1] = selected_route
            selected_route_distance = route_distance(distance_matrix, selected_route)
            new_solution.route_dist_matrix[vehicle][day] = selected_route_distance
            selected_route_demand = route_demand(data, selected_route)
            new_solution.transp_demand_matrix[vehicle][day] = selected_route_demand
            original_distance += solution.route_dist_matrix[vehicle][day]
            # print(f"\n\nv{vehicle}, d{day}")
            # print(f"nold route: {solution.assigned_ordered_matrix[vehicle][day]} \nnew route: {new_solution.assigned_ordered_matrix[vehicle][0]}")
            # print(f"old length: {solution.route_dist_matrix[vehicle][day]}, new length: {new_solution.route_dist_matrix[vehicle][0]}")
    
    new_solution.OBJ_tot_dist = calculate_tot_dist(n_vehicles, n_days, new_solution.route_dist_matrix, new_solution.OBJ_tot_dist)
    # print(f"\nold distance: {solution.OBJ_tot_dist}, new distance: {new_solution.OBJ_tot_dist}")

    return new_solution

def solve_vrp_day_WRONG(n_vehicles, n_days, n_clients, vehicle_capacity,
                  max_clients_kd, data, distance_matrix, solution):
    new_solution = copy.deepcopy(solution)

    # --- 1️⃣ Coordinate del deposito ---
    depot = (data[0, conf.X_COORD_INDEX], data[0, conf.Y_COORD_INDEX])

    # --- 2️⃣ Costruisci lista clienti ---
    clients = []
    for vehicle in range(n_vehicles):
        clients_vd = new_solution.assigned_ordered_matrix[vehicle][0]
        for cl_idx in clients_vd:
            if cl_idx != 0:  # ignora il deposito
                x = data[cl_idx, conf.X_COORD_INDEX]
                y = data[cl_idx, conf.Y_COORD_INDEX]
                demand = data[cl_idx, conf.DEMAND_INDEX]
                clients.append({
                    "id": int(cl_idx),
                    "x": float(x),
                    "y": float(y),
                    "demand": float(demand),
                })

    # --- 3️⃣ Crea modello ---
    model = pyvrp.Model()
    depot_loc = model.add_depot(*depot, name="Depot")

    for c in clients:
        model.add_client(
            c["x"],
            c["y"],
            delivery=[int(c["demand"])],
            pickup=[],
            service_duration=0,
            required=True,           # 🔥 forzali come obbligatori!
            name=f"C{c['id']}",
    )


    # --- 4️⃣ Crea archi e distanze ---
    locations = model.locations
    for i in range(len(locations)):
        for j in range(len(locations)):
            if i != j:
                dist = math.hypot(locations[i].x - locations[j].x,
                                  locations[i].y - locations[j].y)
                model.add_edge(locations[i], locations[j],
                               distance=dist, duration=dist)

    # --- 5️⃣ Definisci i veicoli ---
    model.add_vehicle_type(
        num_available=n_vehicles,
        capacity=[vehicle_capacity],
        fixed_cost=0,
        unit_distance_cost=1,
        name="Truck",
    )

    # --- 6️⃣ Risolvi ---
    stop_criterion = MaxIters(500)
    result = model.solve(stop=stop_criterion, seed=42,
                         collect_stats=False, display=False)

    # --- 7️⃣ Mappa location index → ID cliente ---
    # (ordine in model.locations: 0 = depot, poi clienti in ordine di aggiunta)
    id_map = {i: 0 for i in range(len(model.locations))}  # inizializza a depot=0
    for i, loc in enumerate(model.locations[1:], start=1):
        if loc.name.startswith("C"):
            try:
                id_map[i] = int(loc.name[1:])  # "C12" → 12
            except ValueError:
                id_map[i] = i

    # --- 8️⃣ Estrai costo e rotte ---
    total_cost = result.cost()
    print(f"Costo totale: {total_cost}")

    new_routes = []
    for r_idx, route in enumerate(result.best.routes()):
        clients_ids = []
        for c in route:
            try:
                # c è un Client/Depot → trova il suo indice in model.locations
                loc_idx = model.locations.index(c)
                clients_ids.append(id_map[loc_idx])
            except ValueError:
                clients_ids.append(0)
        new_routes.append(clients_ids)
        print(f"Route {r_idx + 1}: {clients_ids}")

    # --- 9️⃣ Ricostruisci nuova soluzione ---
    new_solution = crete_new_sol_empty(n_vehicles, n_days,
                                       n_clients, max_clients_kd)
    for vehicle in range(n_vehicles):
        selected_route = new_routes[vehicle]
        new_solution.assigned_ordered_matrix[vehicle][0][1:len(selected_route)+1] = selected_route
        selected_route_distance = route_distance(distance_matrix, selected_route)
        selected_route_demand = route_demand(data, selected_route)
        new_solution.route_dist_matrix[vehicle][0] = selected_route_distance
        new_solution.transp_demand_matrix[vehicle][0] = selected_route_demand

        print(f"\nOld route: {solution.assigned_ordered_matrix[vehicle][0]}")
        print(f"New route: {new_solution.assigned_ordered_matrix[vehicle][0]}")
        print(f"Old length: {solution.route_dist_matrix[vehicle][0]}, "
              f"new length: {new_solution.route_dist_matrix[vehicle][0]}")

    new_solution.OBJ_tot_dist = calculate_tot_dist(
        n_vehicles, n_days, new_solution.route_dist_matrix,
        new_solution.OBJ_tot_dist
    )
    print(f"\nOld total distance: {solution.OBJ_tot_dist}, "
          f"new total distance: {new_solution.OBJ_tot_dist}")

    return new_solution

def check_solution(data, n_vehicles, n_days, solution):

    total_transported_demand = 0
    total_clients_demand = 0

    n_info = 1+1+n_days+1 # id, freq, schedule (=n_days), schedule in decimal
    client_records = np.zeros((data.shape[0], n_info), dtype=int)

    for vehicle in range(n_vehicles):
        for day in range(n_days):
            total_transported_demand += solution.transp_demand_matrix[vehicle, day]

            clients_vd = copy.deepcopy(solution.assigned_ordered_matrix[vehicle, day])
            idx = np.where(clients_vd == 0)[0][1]    # remove final zeros
            clients_vd = clients_vd[1:idx]

            for c in range(len(clients_vd)):
                client_idx = clients_vd[c]
                client_records[client_idx, 0] = client_idx
                client_records[client_idx, 1] += 1
                client_records[client_idx, 2+day] = vehicle+1
    
    for c in range(client_records.shape[0]):
        total_clients_demand += (data[c, conf.DEMAND_INDEX] * data[c, conf.FREQ_VISIT_INDEX])

        schedule = np.zeros(n_days, dtype=int)
        for day in range(n_days):
            if client_records[c, 2+day] == 0:
                continue
            schedule[day] = 1
        client_records[c, -1] = int(''.join(map(str, schedule)), 2)

    # compare with data:
    error_assignation = True
    for c in range(client_records.shape[0]):
        client_idx = client_records[c, 0]
        # print(client_idx)
        if client_idx != data[c, conf.CLIENT_ID_INDEX]:
            error_assignation = False
            print(f"errore: cliente originale {data[c, conf.CLIENT_ID_INDEX]}, cliente verificato {client_idx}")
        if client_records[c, 1] != data[c, conf.FREQ_VISIT_INDEX]:
            error_assignation = False
            print(f"errore: frequenza sbagliata del cliente {client_idx}, richiesta {data[c, conf.FREQ_VISIT_INDEX]}, attuale {client_records[c, 1]}")
        if client_records[c, -1] not in data[c, conf.VISIT_START_INDEX:]:
            error_assignation = False
            print(f"errore: la schedule non è tra quelle previste del cliente {client_idx} --> {client_records[c, -1]} vs {data[c, conf.VISIT_START_INDEX:]}")
    if error_assignation == True:    
        print("TUTTE LE ASSEGNAZIONI RISULTANO CORRETTE")

    if total_transported_demand != total_clients_demand:
        print(f"errore: la domanda della soluzione ({total_transported_demand}) non corrisponde a quella dei clienti ({total_clients_demand})")
    print("LA DOMANDA TOTALE SEMBRA CORRETTA")
    # print(client_records)
    return 



def main():

    instance_files = [f"p{str(i).zfill(2)}.txt" for i in range(1, 32+1)]

    for fname in instance_files:
        file_path = os.path.join("data", fname)
        if not os.path.exists(file_path):
            print(f"File non trovato: {file_path} — salto")
            continue

        print(f"\n\n=== Running instance {file_path} ===")
        distance_type = 1
    
        '''DATA PREPARATION'''
        distance_type = 1

        # Prepare data
        (n_vehicles, n_days, vehicle_capacity,
            data, sorted_data, n_clients, max_clients_kd, first_data_index,
            distance_matrix, distance_matrix_adjusted, closeness_matrix) = \
            utils.data_preparation(file_path, distance_type)

        ''' INITIAL SOLUTION '''
        solution_0 = algorithms.assign_route.assign_to_1_vehicle_algorithm(
                n_vehicles, n_days, n_clients, max_clients_kd, vehicle_capacity, sorted_data, distance_matrix, distance_matrix_adjusted, closeness_matrix)

        # check fesibility
        V_distances_matrix, V_loads_matrix, solution_0 = check_feasibility_1vehicle(
            n_vehicles, n_days, n_clients, data, max_clients_kd, vehicle_capacity, distance_matrix, 
            solution_0)    
        if np.any(solution_0.feasibility_vector) != 1 or np.any(solution_0.verification_vector) != 1:
            print("potrebbe esserci un problema")


        ''' OPTMIZED SOLUTION '''

        ''' optimize route '''
        solution_1 = optimize_route(n_vehicles, n_days, distance_matrix, solution_0)

        solution_1.OBJ_tot_dist = 0
        (OBJ_tot_dist_optimized) = calculate_tot_dist(n_vehicles, n_days, solution_1.route_dist_matrix, solution_1.OBJ_tot_dist)
        # print("\noriginal_tot_dist:", solution_0.OBJ_tot_dist)
        # print("optimized_tot_dist:", OBJ_tot_dist_optimized)
        # print("\n\n")

    # crea DataFrame con i risultati cumulativi
    df = pd.DataFrame(
        score_table_global,
        index=algo_names,
        columns=["pos1", "pos2", "pos3", "pos4"]
    )

    # crea la cartella di output se non esiste
    # cartella dello script corrente
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # percorso completo della cartella di output
    output_dir = os.path.join(script_dir, "route_optimizer_test")
    os.makedirs(output_dir, exist_ok=True)

    # file paths
    excel_path = os.path.join(output_dir, "results_summary.xlsx")
    txt_path   = os.path.join(output_dir, "results_summary.txt")

    # stampa su schermo
    print("\n\n===== RISULTATI CUMULATIVI =====")
    print(df)

    # salva su file Excel
    df.to_excel(excel_path, index=True)
    print(f"\nTabella salvata in formato Excel: {excel_path}")

    # salva anche in formato testo (tabella leggibile)
    with open(txt_path, "w") as f:
        f.write("===== RISULTATI CUMULATIVI =====\n")
        f.write(df.to_string())
    print(f"Tabella salvata anche come testo: {txt_path}")

        # for vehicle in range(n_vehicles):
        #     print(f"v{vehicle}, d0: {solution_0.assigned_ordered_matrix[vehicle][0]}")
        # (n_vehicles, n_days, n_clients, vehicle_capacity, max_clients_kd, data, distance_matrix, solution)

        # ''' optimize day '''
        # solution_1 = solve_vrp_day(n_vehicles, n_days, n_clients, vehicle_capacity, max_clients_kd, data, distance_matrix, solution_0)

        # # check fesibility
        # V_distances_matrix, V_loads_matrix, solution_0 = check_feasibility_pvrp(
        #     n_vehicles, n_days, n_clients, data, max_clients_kd, vehicle_capacity, distance_matrix, 
        #     solution_0)    
        # if np.any(solution_0.feasibility_vector) != 1 or np.any(solution_0.verification_vector) != 1:
        #     print("potrebbe esserci un problema")

        # check_solution(data, n_vehicles, n_days, solution_1)


if __name__ == "__main__":
    main()