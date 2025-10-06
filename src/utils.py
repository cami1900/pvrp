import matplotlib.pyplot as plt
import numpy as np
import itertools 
import random
import conf
import copy
import os
import openpyxl
from openpyxl import Workbook, load_workbook


''' DATA PREPARATION and data display '''


def extract_general_info(lines):
    """
    Extracts general problem information:
    - Number of vehicles
    - Number of days in the planning period
    - Maximum vehicle capacity

    Args:
        lines (list): List of lines read from the input file.

    Returns:
        dict: n_vehicles, n_days and vehicle_capacity.
    """
    
    parts = list(map(int, lines[0].split()))
    n_vehicles = parts[1]
    n_days = parts[3]
    vehicle_capacity = list(map(int, lines[1].split()))[1]
    
    return n_vehicles, n_days, vehicle_capacity



def extract_client_data(lines, n_days):
    first_data_index = int(lines[0].split()[3]) + 1
    # n_col = 6 + n_days
    max_visit_com = 0
    for line in lines:
        element = line.split()
        if len(element) > 6:  # almeno 7 colonne
            if int(element[6]) > max_visit_com:
                max_visit_com = int(element[6])
    n_col = max_visit_com + 6
    
    n_row = len(lines) - first_data_index #- 2

    data = np.zeros([n_row, n_col])

    for i, data_line in enumerate(lines[first_data_index:]):
        values = list(map(float, data_line.split()))   # !!! float - int !!!
        
        if len(values) <= 1: # skip blank lines
            continue
        
        id, x, y, d, q, f, a, *visit_list = values
        data[i, conf.CLIENT_ID_INDEX]   = id
        data[i, conf.X_COORD_INDEX]     = x
        data[i, conf.Y_COORD_INDEX]     = y
        data[i, conf.DEMAND_INDEX]      = q
        data[i, conf.FREQ_VISIT_INDEX]  = f
        data[i, conf.N_VISIT_INDEX]     = a

        # Add visit_list values if available (max 5 values)
        for j in range(min(len(visit_list), max_visit_com)):
            data[i, conf.VISIT_START_INDEX + j] = visit_list[j]

    return data



def sort_data(data):
    """
    Sorts the customers hierarchically first by descending order of frequency, 
    then by descending order of demand.

    Args:
        data (matrix): A matrix of customers' data. 

    Returns:
        None: Sorted customers' data matrix.

    Notes:
        - 
    """
    
    # Keep the first row as it is
    depot_row = data[0]

    # Sort remaining rows by frequency in descending order
    sorted_rows = sorted(
                sorted(data[1:], key = lambda x: -x[conf.DEMAND_INDEX]),
                key = lambda x: -x[conf.FREQ_VISIT_INDEX])

    # Combine the first row with the sorted rows
    sorted_data = np.vstack([depot_row, sorted_rows])
    
    return sorted_data



# def manhattan_distance_calculator(data):
#     """
#     Defines the Distance matrix by calculating the Manhattan distance between all the customers, depot included.

#     Args:
#         data (matrix): A customers' data matrix.

#     Returns:
#         None: Distance matrix.

#     Notes:
#         - 
#     """
    
#     # Create a zero Distance matrix
#     distance_matrix = np.zeros((len(data), len(data)))

#     # Calculate Manhattan distances
#     for i in range(len(data)):
#         for j in range(len(data)):
#             manhattan = (abs(data[i][conf.X_COORD_INDEX] - data[j][conf.X_COORD_INDEX]) +
#                           abs(data[i][conf.Y_COORD_INDEX] - data[j][conf.Y_COORD_INDEX]))
#             distance_matrix[i][j] = manhattan
    
#     return distance_matrix



# def euclidean_distance_calculator(data):
#     """
#     Defines the Distance matrix by calculating the Euclidean distance between all the customers, depot included.

#     Args:
#         data (matrix): A customers' data matrix.

#     Returns:
#         None: Distance matrix.

#     Notes:
#         - 
#     """

#     # Create a zero Distance matrix
#     distance_matrix = np.zeros((len(data), len(data)))

#     # Calculate Euclidean distances
#     for i in range(len(data)):
#         for j in range(len(data)):
#             dx = data[i][conf.X_COORD_INDEX] - data[j][conf.X_COORD_INDEX]
#             dy = data[i][conf.Y_COORD_INDEX] - data[j][conf.Y_COORD_INDEX]
#             euclidean = np.sqrt(dx**2 + dy**2)
#             distance_matrix[i][j] = euclidean

#     return distance_matrix



# def closeness_matrix_calculator(data, distance_matrix):
#     """
#     Defines a matrix where for each client i all the other clients (!=i) are ordered from closest to farthest, depot included.

#     Args:
#         data (matrix): A customers' data matrix.

#     Returns:
#         None: Distance matrix.

#     Notes:
#         - 
#     """

#     n_clients = distance_matrix.shape[0]
#     closeness_matrix = np.zeros((n_clients, n_clients - 1), dtype=int)

    

#     for client_i in range(n_clients):
#         dist_pointer = 0.0
#         insertion_index = 0
#         all_clients = np.zeros(n_clients, dtype=int)

#         while insertion_index < (n_clients - 1):
#             # Filtra distanze maggiori del dist_pointer, escludendo self-loop
#             filtered_dist = [dist_j for idx, dist_j in enumerate(distance_matrix[client_i, :]) if dist_j >= dist_pointer and idx != client_i and all_clients[idx] == 0]
#             # filtered_dist = [dist_j for idx, dist_j in enumerate(distance_matrix[client_i, :]) if dist_j > dist_pointer and idx != client_i]


#             if not filtered_dist:
#                 break  # nessuna distanza nuova da considerare

#             min_dist = min(filtered_dist)
#             dist_pointer = min_dist

#             # Trova tutti i clienti (nodi) alla distanza minima
#             columns = np.where(distance_matrix[client_i, :] == min_dist)[0]

#             for col in columns:
#                 if col != client_i and insertion_index < n_clients - 1:
#                     closeness_matrix[client_i, insertion_index] = col
#                     insertion_index += 1
#                     all_clients[col] = 1

#     return closeness_matrix



def data_preparation(file_path, distance_type):

    # load file
    with open(file_path, "r") as file:
        lines = file.read().splitlines()

    # general problem data
    n_vehicles, n_days, vehicle_capacity = extract_general_info(lines)
    # print(f"\n\nNumber of vehicles: {n_vehicles} \nNumber of days:{n_days} \nVehicle capacity: {vehicle_capacity}")

    # customer data
    data = extract_client_data(lines, n_days)
    sorted_data = sort_data(data)
    log_matrix(sorted_data, file_path="out\sorted_data.txt")
    n_clients = len(data)
    max_clients_kd = calculate_kd_clients(data, vehicle_capacity)
    # print(f"Number of clients: {n_clients-1} \nMaximum number of clients in one route:{max_clients_kd}")

    # distance matrix
    if distance_type == 1:
        distance_matrix = euclidean_distance_calculator(data)
        log_matrix(distance_matrix, file_path="out\euclidean_distance_matrix.txt")
    if distance_type == 2:
        distance_matrix = manhattan_distance_calculator(data) 
        log_matrix(distance_matrix, file_path="out\manhattan_distance_matrix.txt")
    distance_matrix_adjusted = distance_matrix_adjuste_calculator(distance_matrix)

    # closeness matrix
    closeness_matrix = closeness_matrix_calculator(data, distance_matrix)
    log_matrix(closeness_matrix, file_path="out\closeness_matrix.txt")


    return (n_vehicles, n_days, vehicle_capacity, data, sorted_data, n_clients, max_clients_kd, distance_matrix, distance_matrix_adjusted, closeness_matrix)



def log_matrix(matrix, file_path):

    # Find the max width of integer and decimal parts
    int_width = 0
    dec_width = 0
    for row in matrix:
        for num in row:
            s = f"{num:.10f}".rstrip('0').rstrip('.')  # remove trailing zeroes
            if '.' in s:
                int_part, dec_part = s.split('.')
            else:
                int_part, dec_part = s, ''
            int_width = max(int_width, len(int_part))
            dec_width = max(dec_width, len(dec_part))

    # Format string to align by decimal
    fmt = f"{{:>{int_width}}}.{{:<{dec_width}}}"

    with open(file_path, 'w') as f:
        for row in matrix:
            formatted_row = []
            for num in row:
                s = f"{num:.10f}".rstrip('0').rstrip('.')
                if '.' in s:
                    int_part, dec_part = s.split('.')
                else:
                    int_part, dec_part = s, ''
                formatted_row.append(fmt.format(int_part, dec_part))
            print('  '.join(formatted_row), file=f)




''' MATRICES '''


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



def distance_matrix_adjuste_calculator(distance_matrix):

    distance_matrix_adjusted = copy.deepcopy(distance_matrix)

    for raw in range(distance_matrix.shape[0]):
        for column in range(distance_matrix.shape[1]):
            if raw != column:
                if distance_matrix[raw, column] == 0:
                    distance_matrix_adjusted[raw, column] = 999

    return distance_matrix_adjusted



''' PLOT - PRINT - STORE '''


def plot_client_position(data):
    """
    Plots client positions on a scatter plot.

    Args:
        data (matrix): A matrix of customers' data, that contains coordinates (x, y)
                                    positioned in conf.X_COORD_INDEX and conf.Y_COORD_INDEX .

    Returns:
        None: Displays a scatter plot of the clients' positions.

    Notes:
        - The points' color depends on frequency of visit requested by the cunstomer.
        - The customer with frequency equal to zero is considered the depot.
        - The plot includes grid lines, axis labels, and a legend for better readability.
    """
    
    
    # plt.figure(figsize=(8, 6))
    # plt.scatter(data[0, conf.X_COORD_INDEX], data[0, conf.Y_COORD_INDEX], color='red', label='Depot')
    # plt.scatter(data[1:, conf.X_COORD_INDEX], data[1:, conf.Y_COORD_INDEX], color='black', label='Clients')
    
    # Plot creation
    plt.figure(figsize=(8, 6))
    sc = plt.scatter(data[:, conf.X_COORD_INDEX], data[:, conf.Y_COORD_INDEX], c=data[:, conf.FREQ_VISIT_INDEX], cmap='turbo')

    # Add colors label
    cbar = plt.colorbar(sc)
    cbar.set_label("Frequency of visits")

    # Add labels
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.title("Map")
    plt.grid(True)

    # plt.xlabel('x [ m ]')
    # plt.ylabel('y [ m ]')
    # plt.title('Map')
    # plt.legend()
    # plt.grid(True)
    # plt.show()
    return



def print_assinged_matrix(assigned_ordered_matrix):

    print("\nAssigned customers matrix:")
    for vehicle_k, vehicle in enumerate(assigned_ordered_matrix):
        print(f"Vehicle {vehicle_k + 1}:")
        for day_t, route in enumerate(vehicle):
            print(f"  Day {day_t + 1}: {route}")
        print()

    return()



def plot_vehicle_routes(n_vehicles, n_days, data, assigned_ordered_matrix):
    """
    Plots routes for each vehicle over multiple days.

    Args:
        data (np.ndarray): Array of customer data with x, y coordinates.
        assigned_customers_matrix (list): Matrix [vehicle][day] with lists of customer IDs.

    Returns:
        None
    """

    colors = plt.cm.get_cmap("tab10", n_days)  # up to 10 colors for days

    for vehicle_k in range(n_vehicles):
        plt.figure(figsize=(8, 6))
        plt.title(f"Routes for Vehicle {vehicle_k+1}")
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.grid(True)

        for day_t in range(n_days):
            route = assigned_ordered_matrix[vehicle_k][day_t]
            if not route:
                continue

            x = [data[real_client_index, conf.X_COORD_INDEX] for real_client_index in route]
            y = [data[real_client_index, conf.Y_COORD_INDEX] for real_client_index in route]

            # Optionally, add depot (assumed at index 0)
            # x = [data[0, conf.X_COORD_INDEX]] + x + [data[0, conf.X_COORD_INDEX]]
            # y = [data[0, conf.Y_COORD_INDEX]] + y + [data[0, conf.Y_COORD_INDEX]]

            plt.plot(x, y, marker='o', label=f"Day {day_t+1}", color=colors(day_t))

        plt.legend()
        plt.show()



def plot_manhattan_vehicles_routes(n_vehicles, n_days, data, assigned_ordered_matrix):
    """
    Plots all vehicle routes side-by-side (one subplot per vehicle), with depot highlighted.

    Args:
        data (np.ndarray): Array with client data (includes X and Y coordinates).
        assigned_customers_matrix (list): [vehicle][day] -> list of client IDs.

    Returns:
        None
    """

    colors = plt.cm.get_cmap("tab10", n_days)  # Up to 10 colors for days

    fig, axes = plt.subplots(1, n_vehicles, figsize=(5 * n_vehicles, 6), sharex=True, sharey=True)

    # Se è 1 veicolo, axes non è una lista: forziamo la lista
    if n_vehicles == 1:
        axes = [axes]

    for v in range(n_vehicles):
        ax = axes[v]
        ax.set_title(f"Vehicle {v + 1}")
        ax.set_xlabel("X Coordinate")
        ax.set_ylabel("Y Coordinate")
        ax.grid(True)

        # Plot each day's route
        for d in range(n_days):
            route = assigned_ordered_matrix[v][d]
            if not route:
                continue

            x = [data[c, conf.X_COORD_INDEX] for c in route]
            y = [data[c, conf.Y_COORD_INDEX] for c in route]

            # Include depot (assumed index 0)
            # depot_x = data[0, conf.X_COORD_INDEX]
            # depot_y = data[0, conf.Y_COORD_INDEX]
            # x = [depot_x] + x + [depot_x]
            # y = [depot_y] + y + [depot_y]

            for i in range(len(route) - 1):
                x1, y1 = data[route[i], conf.X_COORD_INDEX], data[route[i], conf.Y_COORD_INDEX]
                x2, y2 = data[route[i + 1], conf.X_COORD_INDEX], data[route[i + 1], conf.Y_COORD_INDEX]
                
                # Primo tratto orizzontale, poi verticale
                ax.plot([x1, x2], [y1, y1], color=colors(d))  # orizzontale
                ax.plot([x2, x2], [y1, y2], color=colors(d))  # verticale

            # Plot clients' dots
            ax.scatter(x, y, marker='o', color=colors(d), label=f"Day {d + 1}")


        # Highlight the depot once per subplot
        ax.scatter(data[0, conf.X_COORD_INDEX], data[0, conf.Y_COORD_INDEX],
                   c='black', marker='s', s=100, label='Depot')

        ax.legend()

    plt.tight_layout()
    plt.show()



def plot_euclidean_vehicles_routes(n_vehicles, n_days, data, assigned_ordered_matrix):
    """
    Plots all vehicle routes side-by-side (one subplot per vehicle), with depot highlighted.

    Args:
        data (np.ndarray): Array with client data (includes X and Y coordinates).
        assigned_customers_matrix (list): [vehicle][day] -> list of client IDs.

    Returns:
        None
    """

    colors = plt.cm.get_cmap("tab10", n_days)  # Up to 10 colors for days

    fig, axes = plt.subplots(1, n_vehicles, figsize=(5 * n_vehicles, 6), sharex=True, sharey=True)

    # Se è 1 veicolo, axes non è una lista: forziamo la lista
    if n_vehicles == 1:
        axes = [axes]

    for v in range(n_vehicles):
        ax = axes[v]
        ax.set_title(f"Vehicle {v + 1}")
        ax.set_xlabel("X Coordinate")
        ax.set_ylabel("Y Coordinate")
        ax.grid(True)

        # Plot each day's route
        for d in range(n_days):
            route = assigned_ordered_matrix[v][d]
            # if not route:
            #     continue
            if np.all(route == 0):
                continue

            x = [data[c, conf.X_COORD_INDEX] for c in route]
            y = [data[c, conf.Y_COORD_INDEX] for c in route]

            # Include depot (assumed index 0)
            # depot_x = data[0, conf.X_COORD_INDEX]
            # depot_y = data[0, conf.Y_COORD_INDEX]
            # x = [depot_x] + x + [depot_x]
            # y = [depot_y] + y + [depot_y]

            ax.plot(x, y, marker='o', label=f"Day {d + 1}", color=colors(d))

        # Highlight the depot once per subplot
        ax.scatter(data[0, conf.X_COORD_INDEX], data[0, conf.Y_COORD_INDEX],
                   c='black', marker='s', s=100, label='Depot')

        ax.legend()

    plt.tight_layout()
    plt.show()



def calculate_grups_data(n_vehicles, n_days, data, assigned_ordered_matrix, radius_mode='mean_dist', fixed_radius=10):
    centroids = []
    radii = []

    for v in range(n_vehicles):
        vehicle_k_customers = []
        for d in range(n_days):
            vehicle_k_customers.extend(assigned_ordered_matrix[v][d])
        
        if not vehicle_k_customers:
            continue
        
        # Count customer occurrences
        unique_customers = list(set(vehicle_k_customers))  # Remove duplicates
        x_coords = [data[c, conf.X_COORD_INDEX] for c in unique_customers]
        y_coords = [data[c, conf.Y_COORD_INDEX] for c in unique_customers]
        
        # Calculate centroid
        centroid_x = np.mean(x_coords)
        centroid_y = np.mean(y_coords)
        
        # Define radius 
        if radius_mode == 'max_dist':
            dists = [abs(x - centroid_x) + abs(y - centroid_y) for x, y in zip(x_coords, y_coords)]
            radius = max(dists)
        elif radius_mode == 'mean_dist':
            dists = [abs(x - centroid_x) + abs(y - centroid_y) for x, y in zip(x_coords, y_coords)]
            radius = np.mean(dists)
        else:
            radius = fixed_radius
        
        centroids.append((float(centroid_x), float(centroid_y)))
        radii.append(float(radius))
    
    return centroids, radii



def plot_group_clients(n_vehicles, n_days, data, assigned_ordered_matrix, centroids, radii):

    # colors = ['blue', 'green', 'orange']
    colors = plt.cm.get_cmap("tab10", n_vehicles)
    vehicle_labels = ['Vehicle 1', 'Vehicle 2', 'Vehicle 3']
    fig, ax = plt.subplots(figsize=(10, 10))

    radius_mode = 'mean_dist'  # 'max_dist', 'mean_dist', or 'fixed'
    fixed_radius = 10       # If using fixed

    for v in range(n_vehicles):
        vehicle_k_customers = []
        for d in range(n_days):
            vehicle_k_customers.extend(assigned_ordered_matrix[v][d])
        
        if not vehicle_k_customers:
            continue
        
        # Count customer occurrences
        unique_customers = list(set(vehicle_k_customers))  # Remove duplicates
        x_coords = [data[c, conf.X_COORD_INDEX] for c in unique_customers]
        y_coords = [data[c, conf.Y_COORD_INDEX] for c in unique_customers]
        sizes = [data[c, conf.FREQ_VISIT_INDEX] * 50 for c in unique_customers] 
        
        # Plot client locations
        ax.scatter(x_coords, y_coords, s=sizes, c=[colors(v)], label=vehicle_labels[v], alpha=0.6)
        # ax.scatter(x_coords, y_coords, s=sizes, c=colors[v], label=vehicle_labels[v], alpha=0.6)

        # Plot centroid
        centroid_x, centroid_y = centroids[v]
        ax.scatter(centroid_x, centroid_y, c=[colors(v)], marker='*', s=300)

        # Plot circle with transparency
        radius = radii[v]
        circle = plt.Circle((centroid_x, centroid_y + v * 2), radius, color=colors(v), fill=True,  alpha=0.1, linestyle='--')
        ax.add_patch(circle)

    # Show depot
    ax.scatter(data[0, conf.X_COORD_INDEX], data[0, conf.Y_COORD_INDEX], c='black', marker='s', s=150, label='Depot')

    ax.set_title("Customers per vehicle with frequency and centroids")
    ax.set_xlabel("X Coordinate")
    ax.set_ylabel("Y Coordinate")
    ax.grid(True)
    ax.legend()
    plt.axis('equal')
    plt.show()



def tot_euclidean_distance(assigned_ordered_matrix, euclidean_distance_matrix):
    total_euclidean_distance = 0

    for vehicle_days in assigned_ordered_matrix:
        for customer_list in vehicle_days:
            if len(customer_list) < 2:
                continue  # Nessun tragitto se c'è solo un cliente o nessuno

            # Calcola la distanza totale tra clienti consecutivi
            for i in range(len(customer_list) - 1):
                c1 = customer_list[i]
                c2 = customer_list[i + 1]
                total_euclidean_distance += euclidean_distance_matrix[c1][c2]

    return total_euclidean_distance



def calculate_kd_clients(data, vehicle_capacity):

    load_sorted_clients = sorted([(float(i), float(l)) for i, l in zip(data[:, conf.CLIENT_ID_INDEX], data[:, conf.DEMAND_INDEX])],
                                 key=lambda x: x[1])
    tot_load = 0
    selected_clients = []
    max_clients_kd = 0

    for idx, load in load_sorted_clients:
        if tot_load + load <= vehicle_capacity:
            selected_clients.append(idx)
            tot_load += load
            max_clients_kd += 1
        else:
            break
    
    max_clients_kd += max_clients_kd

    return max_clients_kd



def format_assigned_matrix(matrix):
    lines = ["Assigned customers matrix:"]
    for vehicle_k, vehicle in enumerate(matrix):
        lines.append(f"Vehicle {vehicle_k}:")
        for day_t, route in enumerate(vehicle):
            lines.append(f"{' '.join(map(str, route))}")
        lines.append("")  # Riga vuota tra veicoli

    return '\n'.join(lines)



def save_results_in_txt(instance_number, n_vehicles, n_clients, n_days, vehicle_capacity, solution_0, new_vnd_best_solution, new_sol_per_neigh, total_time,
                        max_neighbour, max_iteration_neigh, time_limit_VND, time_limit_neigh):

    # Save results in a .txt file
    lines = []
    lines.append(f"{instance_number}")
    lines.append(f"{n_vehicles} {n_clients-1} {n_days} {vehicle_capacity}")
    lines.append("")
    
    lines.append(f"{solution_0.OBJ_tot_dist}")
    lines.append("")

    lines.append(f"{new_vnd_best_solution.OBJ_tot_dist}")
    lines.append(f"{total_time}")
    lines.append(f"{max_neighbour} {max_iteration_neigh} {time_limit_VND} {time_limit_neigh}")
    lines.append(' '.join(map(str, new_sol_per_neigh)))
    lines.append("")

    # lines.append("Assigned ordered matrix of clients:")
    # lines += [' '.join(map(str, row)) for row in new_vnd_best_solution.assigned_ordered_matrix]
    # lines.append((format_assigned_matrix(new_vnd_best_solution.assigned_ordered_matrix)))
    lines.append("Assigned customers matrix:")
    for vehicle_k, vehicle in enumerate(new_vnd_best_solution.assigned_ordered_matrix):
        lines.append(f"Vehicle {vehicle_k}:")
        for day_t, route in enumerate(vehicle):
            lines.append(f"{' '.join(map(str, route))}")
        lines.append("")  # Riga vuota tra veicoli

    lines.append("Transported demand matrix:")
    lines += [' '.join(map(str, row)) for row in new_vnd_best_solution.transp_demand_matrix]
    lines.append("")

    lines.append("Routes distance matrix:")
    lines += [' '.join(map(str, row)) for row in new_vnd_best_solution.route_dist_matrix]

    return '\n'.join(lines)



def save_vnd_results_in_excel(
        filename, 
        repetitions_VND, time_limit_VND, neigh_order, max_iteration_neigh, worse_sol_neigh, worse_sol_percentage,
        total_time, total_iteration, initial_sol, best_sol_OBJ, all_solutions_VND):

    # # Crea nuovo file Excel
    # wb = Workbook()

    # # --- Foglio 1: Parametri e Risultati ---
    # ws1 = wb.active
    # ws1.title = "Run_Info"

    # # Input
    # ws1.append(["INPUT"])
    # ws1.append(["repetitions_VND"] + repetitions_VND)
    # ws1.append(["time_limit_VND", time_limit_VND])
    # ws1.append(["neigh_order"] + neigh_order)
    # ws1.append(["max_iteration_neigh", max_iteration_neigh])
    # ws1.append(["worse_sol_neigh", worse_sol_neigh])
    # ws1.append(["worse_sol_percentage", worse_sol_percentage])

    # # Riga vuota
    # ws1.append([])

    # # Output
    # ws1.append(["OUTPUT"])
    # ws1.append(["total_time", total_time])
    # ws1.append(["total_iteration", total_iteration])
    # ws1.append(["initial_sol", initial_sol])
    # ws1.append(["best_sol_OBJ", best_sol_OBJ])

    # # --- Foglio 2: Tutte le soluzioni ---
    # ws2 = wb.create_sheet(title="All_Solutions")
    # ws2.append(["repetition", "iteration", "solution_OBJ"])

    # ## unpack data
    # initial_sol = all_solutions_VND[0]
    # data = all_solutions_VND[1::]
    # print(data)
    # for rep_list in data:
    #     for rep, it, obj in rep_list:
    #         ws2.append([rep, it, obj])

    # # Salva il file
    # wb.save(filename)
    # print(f"File salvato: {filename}")

    # === Workbook e Foglio 1 ===
    wb = Workbook()
    ws1 = wb.active
    ws1.title = "Run_Info"

    def _write_row(name, value):
        # nome in colonna A; se value è lista/tupla, espandi nelle colonne successive
        if isinstance(value, (list, tuple)):
            ws1.append([name, *value])
        else:
            ws1.append([name, value])

    # INPUT
    ws1.append(["INPUT"])
    _write_row("repetitions_VND", repetitions_VND)
    _write_row("time_limit_VND", time_limit_VND)
    _write_row("neigh_order", neigh_order)
    _write_row("max_iteration_neigh", max_iteration_neigh)
    _write_row("worse_sol_neigh", "random")
    _write_row("worse_sol_percentage", worse_sol_percentage)

    ws1.append([])  # riga vuota

    # OUTPUT
    ws1.append(["OUTPUT"])
    _write_row("total_time", total_time)
    _write_row("total_iteration", total_iteration)
    _write_row("initial_sol", initial_sol)
    _write_row("best_sol_OBJ", best_sol_OBJ)

    # === Foglio 2: All_Solutions ===
    ws2 = wb.create_sheet(title="All_Solutions")
    ws2.append(["repetition", "iteration", "solution_OBJ"])

    ## unpack data
    initial_sol = all_solutions_VND[0]
    data = all_solutions_VND[1::]
    # data = [[(rep,it,obj), ...], [(rep,it,obj), ...], ...]
    for group in data:
        if not isinstance(group, (list, tuple)):
            continue
        for item in group:
            if isinstance(item, (list, tuple)) and len(item) == 3:
                rep, it, obj = item
                # cast per evitare np.int64 / np.float64
                ws2.append([int(rep), int(it), float(obj)])

    # Salva file .xlsx
    wb.save(filename)

    # Verifica che sia un vero Excel ricaricandolo
    _ = load_workbook(filename)  # se non è xlsx valido, qui solleverà errore
    return filename



def plot_VND_graph(all_solutions_VND, imgname):

    """
    Crea un grafico dell'andamento della funzione obiettivo per il VND,
    mostrando sia le iterations per repetition che quelle cumulative.

    Parametri
    ----------
    all_solutions_VND : list of tuple
        [(iter_in_rep, iter_total, obj_value), ...]
    """

    ## unpack data
    initial_sol = all_solutions_VND[0]
    data = all_solutions_VND[1::]

    obj_values = []
    iter_total = []
    repetition_index = []
    iter_index = 0

    obj_values.append(initial_sol)
    iter_total.append(iter_index)

    for repetition in data:
        for sol in repetition:
            ## plot x-axis
            iter_index += sol[1]
            iter_total.append(iter_index)
            
            ## plot y-axis
            obj_values.append(sol[2])
        
        ## plot repetition vertical lines
        repetition_index.append(len(iter_total)-1)        

    ## plot the iter total on the x-axis, the obj_values on the y-axis. plot vertical lines of repetition_index
     # Plot objective values vs total iterations
    plt.figure(figsize=(17, 6))
    plt.plot(iter_total, obj_values, marker='o', label='Objective Value')

    # Add vertical lines to mark the end of each repetition
    for idx in repetition_index:
        plt.axvline(x=iter_total[idx], color='r', linestyle='--', alpha=0.5)

    plt.xlabel('Total Iterations')
    plt.ylabel('Objective Value')
    plt.title('VND Objective Function Progression')
    plt.legend()
    plt.grid(True)

    # Salva automaticamente il grafico
    plt.savefig(imgname, dpi=300, bbox_inches="tight")
    plt.close()  # chiude la figura per evitare conflitti

    return
