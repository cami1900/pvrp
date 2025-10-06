

import os
import pandas as pd

def parse_result_file(filepath):
    with open(filepath, 'r') as f:
        lines = [line.strip() for line in f if line.strip() != '']

    return {
        'instance': lines[0],
        'vehicles': int(lines[1].split()[0]),
        'clients': int(lines[1].split()[1]),
        'days': int(lines[1].split()[2]),
        'capacity': int(lines[1].split()[3]),
        'initial_sol_val': float(lines[2].replace(',', '.')),
        'VND_sol_val': float(lines[3].replace(',', '.')),
        'time': float(lines[4].replace(',', '.')),
        'max_neigh': int(lines[5].split()[0]),
        'max_iter': int(lines[5].split()[1]),
        'VND_time_limit': int(lines[5].split()[2]),
        'neigh_time_limit': int(lines[5].split()[3]),
        'new_solutions_per_neigh': [int(x) for x in lines[6].split()]
    }

def merge_all_results(folder_path, output_excel_path):
    rows = []
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            filepath = os.path.join(folder_path, filename)
            try:
                result = parse_result_file(filepath)
                rows.append(result)
            except Exception as e:
                print(f"Errore nel file {filename}: {e}")

    # Espandi la colonna dei nuovi valori per ogni neighbourhood in più colonne (facoltativo)
    max_len = max(len(r['new_solutions_per_neigh']) for r in rows)
    for r in rows:
        for i in range(max_len):
            r[f'neigh_{i}'] = r['new_solutions_per_neigh'][i] if i < len(r['new_solutions_per_neigh']) else 0
        del r['new_solutions_per_neigh']  # rimuovi lista originale

    df = pd.DataFrame(rows)
    df.to_excel(output_excel_path, index=False)
    print(f"Salvato in {output_excel_path}")

# Esempio di uso:
if __name__ == "__main__":
    merge_all_results(folder_path='out/results/WorseSol_n3_500', output_excel_path='out/results/WorseSol_n3_500/all_results_WorseSol_n3_500t.xlsx')
