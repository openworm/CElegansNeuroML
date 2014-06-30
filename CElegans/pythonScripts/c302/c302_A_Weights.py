from c302 import generate

import parameters_A as params

if __name__ == '__main__':
    
    cells = ["ADAL", "AIBL", "I1L", "I1R"]
    cells_to_stimulate      = ["ADAL", "I1L"]
    
    new_weights = {"I1L-I1R":2.5}
    
    generate("c302_A_Weights", params, cells=cells, cells_to_stimulate=cells_to_stimulate, weightoverride=new_weights, duration=500, dt=0.1, vmin=-72, vmax=-48)