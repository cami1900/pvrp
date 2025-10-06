import utils

class Move_combination:
    def __init__(self, status, vehicle_k, day_t, schedule_s, real_client_index):
        self.status = status
        self.vehicle = vehicle_k
        self.day = day_t
        self.schedule = schedule_s
        self.client = real_client_index

    def print(self):
        print(f"\nThe {self.status} combination:\n vehicle = {self.vehicle}\n day = {self.day}\n schedule = {self.schedule}\n client index = {self.client}")

    def change_schedule(self, schedule_s):
        self.schedule = schedule_s

class SwapCombination:
    def __init__(self, status, comb_1, comb_2):
        self.status = status
        self.comb_1 = comb_1
        self.comb_2 = comb_2
    
    def print(self):
        print(f"\n\nThe {self.status} combinations are:\n\n" \
              f"{self.comb_1.status}:\n vehicle = {self.comb_1.vehicle}\n day = {self.comb_1.day}\n schedule = {self.comb_1.schedule}\n client index = {self.comb_1.client}\n\n" \
                f"{self.comb_2.status}:\n vehicle = {self.comb_2.vehicle}\n day = {self.comb_2.day}\n schedule = {self.comb_2.schedule}\n client index = {self.comb_2.client}")



