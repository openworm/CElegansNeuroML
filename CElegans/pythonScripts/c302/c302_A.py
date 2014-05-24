from c302 import generate

import parameters_A as params

if __name__ == '__main__':
    
    # Some random set of neurons
    cells_to_stimulate = ["ADAL", "ADAR", "M1","M2L","M3L","M3R","M4","I1R","I2L","I5","I6","MI","NSMR","MCL","ASEL", "AVEL", "AWAR", "DB1", "DVC", "RIAR", "RMDDL"]
    
    # Plot some directly stimulated & some not stimulated
    cells_to_plot      = ["ADAL", "ADAR", "PVDR", "BDUR","I1R","I2L"]
    
    generate("c302_A", params, cells_to_plot=cells_to_plot, cells_to_stimulate=cells_to_stimulate, duration=500, dt=0.1, vmin=-72, vmax=-48)
