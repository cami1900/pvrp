import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import itertools 
import random
import conf
import utils
import copy
import os
import openpyxl
from openpyxl import Workbook, load_workbook



def create_new_dataset_OLD(
    input_file,
    output_file,
    first_data_index,
    total_mode,       # 0 = totale costante, 1 = può variare entro capacità
    fluct_mode,  # "compensated", "mixed", "uniform"
    affected_pct,        # % di clienti influenzati (0-1)
    variance_pct,        # ampiezza fluttuazione (% rispetto alla domanda)
    distr_type,         # "gamma" o "poisson"
    margin_pct,         # % di margine 
    vehicle_capacity,
    n_vehicles,
    n_days,
    seed
):
    """
    Vary customer demand based on the specified parameters.

    Main parameters:
    - total_mode: 0 = constant sum, 1 = can vary within total capacity
    - fluct_mode: fluctuation type ("compensated", "mixed", "uniform")
    - affected_pct: percentage of affected customers
    - variance_pct: level of variance of the variations (%)
    - dist_type: distribution used ("gamma" or "poisson")

    Input parameters:
    input_file: str,
    output_file: str,
    start_row: int = 0,
    total_mode: int = 0,       # 0 = totale costante, 1 = può variare entro capacità
    fluct_mode: str = "compensated",  # "compensated", "mixed", "uniform"
    affected_pct: float = 1.0,        # % di clienti influenzati (0-1)
    variance_pct: float = 0.1,        # ampiezza fluttuazione (% rispetto alla domanda)
    dist_type: str = "gamma",         # "gamma" o "poisson"
    vehicle_capacity: int = 100,
    num_vehicles: int = 5,
    num_days: int = 5,
    margin: int = 0,
    seed: int = None
    """

    if seed is not None:
        np.random.seed(seed)

    # ---- 1️⃣ Lettura file -------------------------------------------------
    # Il file è separato da spazi variabili → delim_whitespace=True
    df = pd.read_csv(input_file, delim_whitespace=True, header=None)

    # ---- 2️⃣ Identifica colonna domanda -----------------------------------
    demand_col = 4
    start_row = first_data_index +1  # skip depot 
    original_demands = df.iloc[start_row:, demand_col].astype(int).values
    n_clients = len(original_demands)

    # ---- 3️⃣ Selezione clienti influenzati -------------------------------
    n_affected = max(1, int(n_clients * affected_pct))
    affected_idx = np.random.choice(np.arange(n_clients), n_affected, replace=False)

    # ---- 4️⃣ Calcolo capacità totale -------------------------------------
    cap_tot = (vehicle_capacity * n_vehicles * n_days) * (1 - margin_pct)

    # ---- 5️⃣ Generazione variazioni --------------------------------------
    new_demands = original_demands.copy().astype(float)

    for i in affected_idx:
        base = original_demands[i]
        mean = base
        std = base * variance_pct

        if distr_type == "gamma":
            # Parametri gamma tali che media=base e varianza=std^2
            beta = (std**2) / mean if mean > 0 else 1
            alpha = mean / beta if beta > 0 else 1
            new_val = np.random.gamma(alpha, beta)
        elif distr_type == "poisson":
            lam = max(0.1, mean)
            new_val = np.random.poisson(lam)
        else:
            raise ValueError("dist_type deve essere 'gamma' o 'poisson'")

        # Compensazione o tipo fluttuazione
        if total_mode == 0:
            # somma costante → applica compensazione tra aumenti e diminuzioni
            delta = new_val - base
            new_val = base + delta
        else:
            if fluct_mode == "compensated":
                # stessa logica, ma dentro total_mode=1
                delta = new_val - base
                new_val = base + delta
            elif fluct_mode == "mixed":
                # variazioni positive o negative
                sign = np.random.choice([-1, 1])
                new_val = base + sign * abs(new_val - base)
            elif fluct_mode == "uniform":
                # tutti nella stessa direzione
                direction = np.random.choice([-1, 1])
                new_val = base + direction * abs(new_val - base)
            else:
                raise ValueError("fluct_mode non valido")

        new_demands[i] = max(0, round(new_val))

    # ---- 6️⃣ Vincolo somma totale ----------------------------------------
    if total_mode == 0:
        # somma costante
        total_original = original_demands.sum()
        total_new = new_demands.sum()
        if total_new != 0:
            scaling = total_original / total_new
            new_demands = np.round(new_demands * scaling)
    else:
        # non deve superare capacità totale
        total_new = new_demands.sum()
        if total_new > cap_tot:
            scaling = cap_tot / total_new
            new_demands = np.round(new_demands * scaling)

    # ---- 7️⃣ Aggiornamento e salvataggio ---------------------------------
    df.iloc[start_row:, demand_col] = new_demands.astype(int)
    df.to_csv(output_file, sep=" ", header=False, index=False)

    # print(f"File salvato come '{output_file}'")
    # print(f"Domanda totale originale: {original_demands.sum():.0f}")
    # print(f"Domanda totale nuova: {new_demands.sum():.0f} (capacità max: {cap_tot})")

    return df



def create_new_dataset_CHAT(
        input_file,
        output_file,
        data=0,
        first_data_index=None,
        vehicle_capacity=None,
        n_vehicles=None,
        n_days=None,
        distance_type=None,
        seed=None,
        total_mode=0,       # 0 = totale costante, 1 = può variare entro capacità
        fluct_mode="compensated",  # "compensated", "mixed", "uniform"
        client_affected_pct=100,        # % di clienti influenzati (0-100)
        variance_pct=10,        # ampiezza fluttuazione (% rispetto alla domanda)
        distr_type="gamma",         # "gamma" o "poisson"
        margin_pct=5,         # % di margine  
):
    """
    Crea un nuovo dataset con le domande dei clienti variate.
    """

    # Imposta seme randomico
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)

    # --- 1️⃣ Lettura righe file ---
    with open(input_file, "r") as f:
        lines = f.readlines()

    # --- 2️⃣ Estrai dati se non forniti ---
    if isinstance(data, int) and data == 0:
        n_vehicles, n_days, vehicle_capacity, first_data_index = utils.extract_general_info(lines)
        data = utils.extract_client_data(lines, n_days)
    elif first_data_index is None:
        _, _, _, first_data_index = utils.extract_general_info(lines)

    # --- 3️⃣ Crea una copia profonda dei dati ---
    new_data = copy.deepcopy(data)

    # --- 4️⃣ Parametri base ---
    demands = data[:, conf.DEMAND_INDEX].copy()
    original_total = demands.sum()
    cap_tot = n_vehicles * vehicle_capacity * n_days * (1 - margin_pct / 100)

    n_clients = len(demands)
    n_affected = max(1, int((n_clients - 1) * client_affected_pct / 100))  # escludi depot

    affected_idx = random.sample(range(1, n_clients), n_affected)  # skip depot

    # --- 5️⃣ Applica le fluttuazioni ---
    new_demands = demands.copy()
    for i in affected_idx:
        base = demands[i]
        if base <= 0:
            continue

        if distr_type == "gamma":
            shape = 2.0
            scale = (variance_pct / 100) * base / shape
            variation = np.random.gamma(shape, scale)
        elif distr_type == "poisson":
            lam = (variance_pct / 100) * base
            variation = np.random.poisson(lam)
        else:
            raise ValueError("distr_type deve essere 'gamma' o 'poisson'")

        # Gestione segno secondo fluct_mode
        if fluct_mode == "compensated":
            sign = random.choice([-1, 1])
        elif fluct_mode == "uniform":
            sign = 1
        else:  # mixed
            sign = random.choice([-1, 1])

        new_val = max(0, base + sign * variation)
        new_demands[i] = int(round(new_val))

    # --- 6️⃣ Total mode ---
    if total_mode == 0:  # somma costante
        diff = new_demands.sum() - original_total
        if diff != 0:
            adj_idx = [i for i in range(1, n_clients) if i not in affected_idx]
            if len(adj_idx) == 0:
                adj_idx = [i for i in range(1, n_clients)]
            for _ in range(abs(int(diff))):
                j = random.choice(adj_idx)
                if diff > 0 and new_demands[j] > 0:
                    new_demands[j] -= 1
                elif diff < 0:
                    new_demands[j] += 1
        new_demands[new_demands < 0] = 0

    elif total_mode == 1:  # somma può variare ma non superare capacità
        if new_demands.sum() > cap_tot:
            scale_factor = cap_tot / new_demands.sum()
            new_demands = np.floor(new_demands * scale_factor).astype(int)

    # --- 7️⃣ Sostituisci valori aggiornati nella copia dei dati ---
    new_data[:, conf.DEMAND_INDEX] = new_demands

    # --- 8️⃣ Scrivi il nuovo file completo ---
    with open(output_file, "w") as f:
        # righe iniziali (intestazione)
        for line in lines[:first_data_index]:
            f.write(line)
        # righe clienti (depot incluso)
        for row in new_data:
            row_clean = [str(int(x)) if idx == conf.DEMAND_INDEX else str(x) 
                         for idx, x in enumerate(row) if not np.isnan(x)]
            f.write(" ".join(row_clean) + "\n")

    # --- 9️⃣ Report ---
    # print(f"✅ File salvato: {output_file}")
    # print(f"Domanda totale originale: {original_total}")
    # print(f"Domanda totale nuova: {int(new_demands.sum())} (capacità max: {int(cap_tot)})")

    return new_data



def manhattan_distance_calculator(data):
    """
    Defines the Distance matrix by calculating the Manhattan distance between all the customers, depot included.

    Args:
        data (matrix): A customers' data matrix.

    Returns:
        None: Distance matrix.

    Notes:
        - 
    """
    
    # Create a zero Distance matrix
    distance_matrix = np.zeros((len(data), len(data)))

    # Calculate Manhattan distances
    for i in range(len(data)):
        for j in range(len(data)):
            manhattan = (abs(data[i][conf.X_COORD_INDEX] - data[j][conf.X_COORD_INDEX]) +
                          abs(data[i][conf.Y_COORD_INDEX] - data[j][conf.Y_COORD_INDEX]))
            distance_matrix[i][j] = manhattan
    
    return distance_matrix



def euclidean_distance_calculator(data):
    """
    Defines the Distance matrix by calculating the Euclidean distance between all the customers, depot included.

    Args:
        data (matrix): A customers' data matrix.

    Returns:
        None: Distance matrix.

    Notes:
        - 
    """

    # Create a zero Distance matrix
    distance_matrix = np.zeros((len(data), len(data)))

    # Calculate Euclidean distances
    for i in range(len(data)):
        for j in range(len(data)):
            dx = data[i][conf.X_COORD_INDEX] - data[j][conf.X_COORD_INDEX]
            dy = data[i][conf.Y_COORD_INDEX] - data[j][conf.Y_COORD_INDEX]
            euclidean = np.sqrt(dx**2 + dy**2)
            distance_matrix[i][j] = euclidean

    return distance_matrix



def closeness_matrix_calculator(data, distance_matrix):
    """
    Defines a matrix where for each client i all the other clients (!=i) are ordered from closest to farthest, depot included.

    Args:
        data (matrix): A customers' data matrix.

    Returns:
        None: Distance matrix.

    Notes:
        - 
    """

    n_clients = distance_matrix.shape[0]
    closeness_matrix = np.zeros((n_clients, n_clients - 1), dtype=int)

    

    for client_i in range(n_clients):
        dist_pointer = 0.0
        insertion_index = 0
        all_clients = np.zeros(n_clients, dtype=int)

        while insertion_index < (n_clients - 1):
            # Filtra distanze maggiori del dist_pointer, escludendo self-loop
            filtered_dist = [dist_j for idx, dist_j in enumerate(distance_matrix[client_i, :]) if dist_j >= dist_pointer and idx != client_i and all_clients[idx] == 0]
            # filtered_dist = [dist_j for idx, dist_j in enumerate(distance_matrix[client_i, :]) if dist_j > dist_pointer and idx != client_i]


            if not filtered_dist:
                break  # nessuna distanza nuova da considerare

            min_dist = min(filtered_dist)
            dist_pointer = min_dist

            # Trova tutti i clienti (nodi) alla distanza minima
            columns = np.where(distance_matrix[client_i, :] == min_dist)[0]

            for col in columns:
                if col != client_i and insertion_index < n_clients - 1:
                    closeness_matrix[client_i, insertion_index] = col
                    insertion_index += 1
                    all_clients[col] = 1

    return closeness_matrix


