from c302 import generate

import parameters_A as params

if __name__ == '__main__':
    
    pharyngeal_cells = ["M1","M2L","M2R","M3L","M3R","M4","M5","I1L","I1R","I2L","I2R","I3","I4","I5","I6","MI","NSML","NSMR","MCL","MCR"]
    cells_to_stimulate = ["M1","M3R","M4","M5","I1L","I4","I5","I6","MCL","MCR"]
    
    generate("c302_A_Pharyngeal", params, cells=pharyngeal_cells, cells_to_stimulate=cells_to_stimulate, duration=500, dt=0.025, vmin=-72, vmax=-48)