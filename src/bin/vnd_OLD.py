import matplotlib.pyplot as plt
import numpy as np
import itertools 
import random
import copy
import conf
import classes

def k_move_t_old(n_vehicles, n_days, data, current_solution, neighbour):

    # Inintial combination:
    vehicle_k = random.randint(0, n_vehicles-1)
    day_t1 = random.randint(0, n_days-1)
    client_list = current_solution.assigned_ordered_matrix[vehicle_k, day_t1]
    client_list = client_list[client_list != 0]
    bin_day_t1 = np.zeros(n_days)
    bin_day_t1[day_t1] = 1
    real_client_index = random.choice(client_list)

    initial_comb = classes.Move_combination('initial', vehicle_k, day_t1, bin_day_t1, real_client_index)

    # initial_comb = def_initial_comb(neighbour, n_vehicles, n_days, data, current_solution)

    # Final combination: select new day excluding day 1
    day_t2 = random.choice([t for t in range(0, n_days) if t != day_t1])
    bin_day_t2 = np.zeros(n_days)
    bin_day_t2[day_t2] = 1

    final_comb = classes.Move_combination('final', vehicle_k, day_t2, bin_day_t2, real_client_index)

    
    # in frequency is differnt from 1:
    if data[real_client_index][conf.FREQ_VISIT_INDEX] != 1:
        n_visit_comb_i = int(data[real_client_index][conf.N_VISIT_INDEX])
        possible_schedules_i = np.zeros(n_visit_comb_i, dtype=int)
        schedule_s1 = np.zeros(n_days)
        days_s1 = np.where(current_solution.assigned_ordered_matrix[vehicle_k] == real_client_index)[0]
        for day in days_s1:
            schedule_s1[day] = 1

        for schedule in range(n_visit_comb_i):
            # schedule_s = format(int(data[real_client_index][conf.VISIT_START_INDEX + schedule]), '05b')
            # schedule_s = np.array([int(b) for b in format(int(data[real_client_index][conf.VISIT_START_INDEX + schedule]), '05b')], dtype=int)
            schedule_val = int(data[real_client_index][conf.VISIT_START_INDEX + schedule])
            schedule_s = np.array(
                [int(b) for b in format(schedule_val, f'0{n_days}b')],
                dtype=int
                )
            # if (schedule_s - schedule_s1) != 0: # Check that the schedule is not the current one
            if np.all((np.subtract(schedule_s, schedule_s1)) != 0): # Check that the schedule is not the current one
                # check_day_t2 = schedule_s + bin_day_t2
                check_day_t2 = np.add(schedule_s, bin_day_t2)
                # binary_list = [int(bit) for bit in find_day_t2]
                if np.any(check_day_t2[:] == 2): # Check day_t2 is in the schedule
                    possible_schedules_i[schedule] = schedule_s
        possible_schedules_i[possible_schedules_i!=0]
        schedule_s2 = random.choice(possible_schedules_i)
    initial_comb.change_schedule(schedule_s1)
    final_comb.change_schedule(schedule_s2)

    return(initial_comb, final_comb)


def def_final_comb_old(neighbour, n_vehicles, n_days, data, current_solution, initial_comb):

    day_t2 = random.choice([t for t in range(0, n_days) if t != initial_comb.day])
    bin_day_t2 = np.zeros(n_days)
    bin_day_t2[day_t2] = 1

    final_comb = classes.Move_combination('final', initial_comb.vehicle, day_t2, bin_day_t2, initial_comb.client)

    if data[initial_comb.client][conf.FREQ_VISIT_INDEX] != 1:
        n_visit_comb_i = int(data[initial_comb.client][conf.N_VISIT_INDEX])
        possible_schedules_i = np.zeros(n_visit_comb_i, dtype=int)
        
        for schedule in range(n_visit_comb_i):
            schedule_val = int(data[initial_comb.client][conf.VISIT_START_INDEX + schedule])
            schedule_s = np.array(
                [int(b) for b in format(schedule_val, f'0{n_days}b')],
                dtype=int
                )
            if np.all((np.subtract(schedule_s, initial_comb.schedule)) != 0): # Check that the schedule is not the current one
                check_day_t2 = np.add(schedule_s, bin_day_t2)
                if np.any(check_day_t2[:] == 2): # Check day_t2 is in the schedule
                    possible_schedules_i[schedule] = schedule_s
        possible_schedules_i = possible_schedules_i[possible_schedules_i!=0]
        if np.any(possible_schedules_i != 0 ):
            schedule_s2 = random.choice(possible_schedules_i)
            final_comb.change_schedule(schedule_s2)
        else:
            schedule_s2 = 0
            final_comb.change_schedule(schedule_s2)

    return final_comb


