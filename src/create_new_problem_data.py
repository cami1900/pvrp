import random

def main():
    # Esempio di utilizzo
    modify_demand("data_new/p02.txt", "data_new/p02_new.txt")


def modifica_domanda(file_input, file_output, percentuale=0.3):
    with open(file_input, 'r') as f:
        lines = f.readlines()

    # Prima riga con type, m, n, t
    header = lines[0].strip()
    type_, m, n, t = map(int, header.split())

    # t righe successive con D Q
    t_lines = lines[1:1+t]

    # Resto dei clienti
    clienti_lines = lines[1+t:]
    
    # Estraggo le informazioni dei clienti
    clienti = []
    for line in clienti_lines:
        parts = line.strip().split()
        i = int(parts[0])
        x, y, d, q = map(float, parts[1:5])
        # Salvo anche il resto dei campi
        resto = parts[5:]
        clienti.append([i, x, y, d, q, resto])

    # Numero di clienti da modificare (almeno 30%)
    num_modifica = max(int(len(clienti) * percentuale), 1)

    # Seleziono clienti casualmente
    clienti_da_modificare = random.sample(clienti, num_modifica)

    # Calcolo la somma totale delle domande
    somma_totale = sum(c[4] for c in clienti)

    # Modifico le domande in modo casuale mantenendo la somma
    delta_totale = 0
    for c in clienti_da_modificare:
        vecchio_q = c[4]
        # Modifica casuale +/-10% (esempio)
        nuovo_q = vecchio_q * random.uniform(0.9, 1.1)
        c[4] = nuovo_q
        delta_totale += vecchio_q - nuovo_q

    # Ridistribuisco la differenza tra tutti i clienti per mantenere la somma invariata
    delta_per_cliente = delta_totale / len(clienti)
    for c in clienti:
        c[4] += delta_per_cliente

    # Scrivo su nuovo file
    with open(file_output, 'w') as f:
        f.write(header + '\n')
        f.writelines(t_lines)
        for c in clienti:
            # Ricostruisco la linea originale
            line = f"{int(c[0])} {c[1]} {c[2]} {c[3]} {c[4]} " + " ".join(map(str, c[5])) + "\n"
            f.write(line)

def modify_demand(file_input, file_output, percentuale=0.3):
    with open(file_input, 'r') as f:
        lines = f.readlines()

    # Prima riga con type, m, n, t
    header = lines[0].strip()
    type_, m, n, t = map(int, header.split())

    # t righe successive con D Q
    t_lines = lines[1:1+t]

    # Resto dei clienti
    clienti_lines = lines[1+t:]
    
    clienti = []
    for line in clienti_lines:
        parts = line.strip().split()
        i = int(parts[0])
        x = float(parts[1])
        y = float(parts[2])
        d = int(parts[3])
        q = int(parts[4])   # domanda come intero
        resto = parts[5:]
        clienti.append([i, x, y, d, q, resto])

    # Numero di clienti da modificare (almeno 30%)
    num_modifica = max(int(len(clienti) * percentuale), 1)
    clienti_da_modificare = random.sample(clienti, num_modifica)

    # Somma originale
    somma_totale = sum(c[4] for c in clienti)

    # Modifico le domande in ±20% (almeno 1 unità di differenza se possibile)
    for c in clienti_da_modificare:
        vecchio_q = c[4]
        if vecchio_q > 0:
            variazione = random.randint(-max(1, vecchio_q // 5), max(1, vecchio_q // 5))
            c[4] = max(0, vecchio_q + variazione)  # mai negativo

    # Somma dopo modifica
    nuova_somma = sum(c[4] for c in clienti)
    delta = somma_totale - nuova_somma

    # Bilancio la differenza distribuendola ai clienti
    idx = 0
    while delta != 0:
        if delta > 0:
            clienti[idx % len(clienti)][4] += 1
            delta -= 1
        elif delta < 0 and clienti[idx % len(clienti)][4] > 0:
            clienti[idx % len(clienti)][4] -= 1
            delta += 1
        idx += 1

    # Scrivo il nuovo file
    with open(file_output, 'w') as f:
        f.write(header + '\n')
        f.writelines(t_lines)
        for c in clienti:
            line = f"{c[0]} {c[1]:.0f} {c[2]:.0f} {c[3]} {c[4]} " + " ".join(map(str, c[5])) + "\n"
            f.write(line)


if __name__ == "__main__":
    main()
