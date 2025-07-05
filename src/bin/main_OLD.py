


# ## DATA PREPARATION 
    # # load file
    # file_path = "data/p02.txt"
    # with open(file_path, "r") as file:
    #     lines = file.read().splitlines()

    # # general problem data
    # n_vehicles, n_days, vehicle_capacity = utils.extract_general_info(lines)
    # print(f"\n\nNumber of vehicles: {n_vehicles} \nNumber of days:{n_days} \nVehicle capacity: {vehicle_capacity}")

    # # customer data
    # data = utils.extract_client_data(lines, n_days)
    # sorted_data = utils.sort_data(data)
    # utils.log_matrix(sorted_data, file_path="out\sorted_data.txt")
    # n_clients = len(data)
    # max_clients_kd = utils.calculate_kd_clients(data, vehicle_capacity)
    # print(f"Number of clients: {n_clients} \nMaximum number of clients in one route:{max_clients_kd}")

    # # distance matrix
    # # manhattan_distance_matrix = utils.manhattan_distance_calculator(data) 
    # euclidean_distance_matrix = utils.euclidean_distance_calculator(data)
    # utils.log_matrix(euclidean_distance_matrix, file_path="out\euclidean_distance_matrix.txt")

    # # closeness matrix
    # closeness_matrix = utils.closeness_matrix_calculator(data, euclidean_distance_matrix)
    # utils.log_matrix(closeness_matrix, file_path="out\closeness_matrix.txt")