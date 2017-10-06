from c302.c302 import generate

import parameters_A as params

if __name__ == '__main__':
    
    # Chosen as there is 1 synapse between each pair
    cells = ["ADAL", "AIBL", "I1L", "I3", "DB5", "PVCR"]
    cells_to_stimulate      = ["ADAL", "I1L", "PVCR"]
    
    new_conn_numbers = {"I1L-I3":2.5}
    scaled_conn_numbers = {"PVCR-DB5":5}
    
    generate("c302_A_Weights", params, cells=cells, cells_to_stimulate=cells_to_stimulate, \
             conn_number_override=new_conn_numbers, conn_number_scaling=scaled_conn_numbers, \
             duration=500, dt=0.1, vmin=-72, vmax=-48)