import random
import random2
import numpy as np
import os
import sys
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed


import utils



''' SETTINGS -------------------------------------------------------------------------------------------------------'''

MAX_WORKERS = 8     # Maximum number of cores to use (change as desired) --> CLUSTER: max = 4

# Directory
input_dir_base = "data"
input_dir_new  = "data_new"     # To create a new dataset, create a folder and rename path
output_dir = "out/results/AVND_multiobj"       # Create new folder to avoid overwriting results and rename path

distance_type = 1       # select: Euclidean = 1, Manhattan = 2 (NOT use!!)


# Demand fluctuation parameters
total_mode = 0                 # 0 = totale costante, 1 = può variare entro capacità
fluct_mode = "compensated"     # "compensated", "mixed", "uniform"
client_affected_pct = 1        # % di clienti influenzati (0-1)
variance_pct = 0.5             # ampiezza fluttuazione (%(0-1) rispetto alla domanda)
distr_type = "gamma"         # "gamma" o "poisson"
margin_pct = 0.1               # % di margine (0-1)


def instance_dataset_create(filename):

    ''' INSTANCE '''
    instance_number = int(filename[1:])  # 'p01' -> 1

    ''' PATHS '''
    output_dir_instance = os.path.join(output_dir, "filename")
    os.makedirs(output_dir_instance, exist_ok=True)     # Crea automaticamente la directory (e sottocartelle se mancano)

    path_data_base = os.path.join(input_dir_base, filename + ".txt")

    path_data_new  = os.path.join(input_dir_new,  filename + ".txt")

    ''' INSTANCE BASE '''
        # Prepare data
    (n_vehicles, n_days, vehicle_capacity,
      data, sorted_data, 
      n_clients, max_clients_kd, first_data_index,
        distance_matrix, distance_matrix_adjusted, closeness_matrix) = \
        utils.data_preparation(path_data_base, distance_type)
    print(f"{filename}: data prepared")

    ''' INSTANCE NEW '''
    # Create new instances (demand fluctuation)
    data_new = utils.create_new_dataset(
        path_data_base, path_data_new,
        data, first_data_index, vehicle_capacity, n_vehicles, n_days,
        distance_type,
        total_mode, fluct_mode, client_affected_pct, variance_pct, distr_type, margin_pct,
        )

    return filename


def main():

    # seed
    seed = 42 
    random.seed(seed)
    np.random.seed(seed)
    random2.seed(seed)

        # --- User confirmation ---
    proceed = input("⚙️  Do you want to continue with the execution? (yes/no): ").strip().lower()
    if proceed not in ['y', 'yes']:
        print("⛔ Execution aborted by user.")
        sys.exit(0)

    # --- Execution ---
    os.makedirs(output_dir, exist_ok=True)
    instance_files = [f"p{str(i).zfill(2)}" for i in range(1, 32+1)]

    print(f"Avvio elaborazione parallela con {MAX_WORKERS} worker...\n")

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(instance_dataset_create, file): file for file in instance_files}

        for future in as_completed(futures):
            instance = futures[future]
            try:
                future.result()
                print(f"{instance} completata.")
            except Exception as e:
                print(f"Errore in {instance}: {e}")
                traceback.print_exc()

    print("\nElaborazione completata.")

    



    
if __name__ == "__main__":
    main()