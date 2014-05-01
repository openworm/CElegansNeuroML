from c302 import generate

import parameters_A as params

if __name__ == '__main__':
    
    cells = ["ADAL", "AIBL", "RIVR", "RMEV"]
    cells_to_stimulate      = ["ADAL", "RIVR"]
    
    generate("c302_A_Syns", params, cells=cells, cells_to_stimulate=cells_to_stimulate, duration=500, dt=0.1, vmin=-72, vmax=-48)