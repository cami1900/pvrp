import utils


# solution class
# class Solution:
#     def __init__(self, OBJ_tot_dist,
#                     assigned_ordered_matrix, not_assigned_list, transp_demand_matrix, route_dist_matrix):
#         self.OBJ_tot_dist = OBJ_tot_dist
#         self.assigned_ordered_matrix = assigned_ordered_matrix
#         self.not_assigned_list = not_assigned_list
#         self.transp_demand_matrix = transp_demand_matrix  
#         self.route_dist_matrix = route_dist_matrix      

#     def print_solution(self):
#         print("oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo")
#         print(f"\nTotal distance traveled:{self.OBJ_tot_dist}")
#         utils.print_assinged_matrix(self.assigned_ordered_matrix) 
#         print(f"\nNot assigned customers list:\n", self.not_assigned_list)
#         print("\nTransported demand matrix:\n", self.transp_demand_matrix)
#         print("\nRoute distances matrix:\n", self.route_dist_matrix)

#     def set_OBJ(self, OBJ_tot_dist):
#         self.OBJ_tot_dist = OBJ_tot_dist
    
#     def set_assign_clients(self, assigned_ordered_matrix):
#         self.assigned_ordered_matrix = assigned_ordered_matrix

#     def set_not_ass_cl(self, not_assigned_list):
#         self.not_assigned_list = not_assigned_list

#     def set_transp_demand(self, transp_demand_matrix):
#         self.transp_demand_matrix = transp_demand_matrix

#     def set_route_dist(self, route_dist_matrix):
#         self.route_dist_matrix = route_dist_matrix


class Solution:
    def __init__(self, OBJ_tot_dist,
                    assigned_ordered_matrix, not_assigned_list, transp_demand_matrix, route_dist_matrix):
        self.OBJ_tot_dist = OBJ_tot_dist
        self.assigned_ordered_matrix = assigned_ordered_matrix
        self.not_assigned_list = not_assigned_list
        self.transp_demand_matrix = transp_demand_matrix  
        self.route_dist_matrix = route_dist_matrix   

        self.feasibility_vector = self.FeasibilityVector()
        self.verification_vector = self.VerificationVector()
    
    def print(self):
        print("\noooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo")
        print(f"\nTotal distance traveled:{self.OBJ_tot_dist}")
        utils.print_assinged_matrix(self.assigned_ordered_matrix) 
        print(f"\nNot assigned customers list:\n", self.not_assigned_list)
        print("\nTransported demand matrix:\n", self.transp_demand_matrix)
        print("\nRoute distances matrix:\n", self.route_dist_matrix)

    def print_assigned(self):

        print("hej!")
        utils.print_assinged_matrix(self.assigned_ordered_matrix) 


    class FeasibilityVector:
        def __init__(self, c1=1, c2=1, c3=1, c4=1, c5=1, c6=1):
            self.constr_1 = c1
            self.constr_2 = c2
            self.constr_3 = c3
            self.constr_4 = c4
            self.constr_5 = c5
            self.constr_6 = c6

        def print(self):
            print("\n-------------------------------------------------------------------------------------")
            print("\nThe feasibility vector of the solution is:")
            print("Constr_1:", self.constr_1)
            print("Constr_2:", self.constr_2)
            print("Constr_3:", self.constr_3)
            print("Constr_4:", self.constr_4)
            print("Constr_5:", self.constr_5)
            print("Constr_6:", self.constr_6)

        def verify(self):
            if self.constr_1 == 1 and self.constr_2 == 1 and self.constr_3 == 1 and self.constr_4 == 1 and self.constr_5 == 1 and self.constr_6 == 1:
                return True 
            else:
                return False
            
    

    
    class VerificationVector:
        def __init__(self, dist=1, load=1):
            self.verif_dist = dist
            self.verif_load = load

        def print(self):
            print("\n-------------------------------------------------------------------------------------")
            print("\nThe verification vector of the solution is:")
            print("verif_dist:", self.verif_dist)
            print("verif_load:", self.verif_load)

        def verify(self):
            if self.verif_dist == 1 and self.verif_load == 1:
                return True 
            else:
                return False




class Solution_multiOBJ:
    def __init__(self, 
                 OBJ_value : float, 
                 tot_dist : float,
                 sim_value : float,
                 assigned_ordered_matrix, 
                 not_assigned_list, 
                 transp_demand_matrix,
                 route_dist_matrix, 
                 sim_matrix):
        self.OBJ_value = OBJ_value
        self.tot_dist = tot_dist
        self.sim_value = sim_value
        self.assigned_ordered_matrix = assigned_ordered_matrix
        self.not_assigned_list = not_assigned_list
        self.transp_demand_matrix = transp_demand_matrix  
        self.route_dist_matrix = route_dist_matrix   
        self.sim_matrix = sim_matrix

        self.feasibility_vector = self.FeasibilityVector()
        self.verification_vector = self.VerificationVector()
    
    def print(self):
        print("\n******************************** SOLUTION ***************************************")
        print(f"\nMulti-objective value:{self.OBJ_value}, [dist={self.dist_value}, diss={self.dissim_value}]")
        utils.print_assinged_matrix(self.assigned_ordered_matrix) 
        print(f"\nNot assigned customers list:\n", self.not_assigned_list)
        print("\nTransported demand matrix:\n", self.transp_demand_matrix)
        print("\nRoute distances matrix:\n", self.route_dist_matrix)
        print("\nSimilarity matrix:\n", self.sim_matrix)

    def print_assigned(self):

        print("hej!")
        utils.print_assinged_matrix(self.assigned_ordered_matrix) 


    class FeasibilityVector:
        def __init__(self, c1=1, c2=1, c3=1, c4=1, c5=1, c6=1):
            self.constr_1 = c1
            self.constr_2 = c2
            self.constr_3 = c3
            self.constr_4 = c4
            self.constr_5 = c5
            self.constr_6 = c6

        def print(self):
            print("\n-------------------------------------------------------------------------------------")
            print("\nThe feasibility vector of the solution is:")
            print("Constr_1:", self.constr_1)
            print("Constr_2:", self.constr_2)
            print("Constr_3:", self.constr_3)
            print("Constr_4:", self.constr_4)
            print("Constr_5:", self.constr_5)
            print("Constr_6:", self.constr_6)

        def verify(self):
            if self.constr_1 == 1 and self.constr_2 == 1 and self.constr_3 == 1 and self.constr_4 == 1 and self.constr_5 == 1 and self.constr_6 == 1:
                return True 
            else:
                return False
            
    

    
    class VerificationVector:
        def __init__(self, dist=1, load=1):
            self.verif_dist = dist
            self.verif_load = load

        def print(self):
            print("\n-------------------------------------------------------------------------------------")
            print("\nThe verification vector of the solution is:")
            print("verif_dist:", self.verif_dist)
            print("verif_load:", self.verif_load)
        
        def verify(self):
            if self.verif_dist == 1 and self.verif_load == 1:
                return True 
            else:
                return False




class Move_combination:
    def __init__(self, status, vehicle_k, day_t, schedule_s, real_client_index):
        self.status = status
        self.vehicle = vehicle_k
        self.day = day_t
        self.schedule = schedule_s
        self.client = real_client_index
        # self.linked_comb = linked_combinations

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





