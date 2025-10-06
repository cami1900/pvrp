import numpy as np
import random

seed = 5
random.seed(seed)
np.random.seed(seed)

client_list = np.array([0, 4, 35, 6, 27, 19, 23, 1, 14, 0, 0, 0])
number_clients = 2

# remove zeros:
client_list = client_list[client_list != 0]
# if empty list
# if np.size(client_list) == 0:
#     # print("\n\n____________________________empty__________________________\n\n")
#     real_client_index = 0
#     return (real_client_index, False)

# pick random client #1:
real_client_index_1 = random.choice(client_list)
print(real_client_index_1)

# pick random client #2:
if number_clients == 0:
    mask = client_list != real_client_index_1
    client_list_no_cl1 = client_list[mask]
    real_client_index_2 = random.choice(client_list_no_cl1)
else:
    # pick the same number of clients with a variance of [-1, +1]
    where_cl1 = (np.where(client_list == real_client_index_1)[0][0])
    print(where_cl1)
    possible_range = [int(where_cl1-number_clients), int(where_cl1+number_clients+1)]
    print(possible_range)
    possible_client_list = client_list[possible_range[0] : possible_range[1]]
    print(possible_client_list)
    mask = possible_client_list != real_client_index_1
    client_list_no_cl1 = possible_client_list[mask]
    real_client_index_2 = random.choice(client_list_no_cl1)


# output
where_cl1 = (np.where(client_list == real_client_index_1)[0])
where_cl2 = (np.where(client_list == real_client_index_2)[0])
number_clients = (abs(where_cl1 - where_cl2)+ 1)[0]

real_client_index = np.zeros(2, dtype=int)
if where_cl1 < where_cl2:
    real_client_index[0] = real_client_index_1
    real_client_index[1] = real_client_index_2
else:
    real_client_index[1] = real_client_index_1
    real_client_index[0] = real_client_index_2


print(real_client_index, where_cl1, where_cl2, number_clients)