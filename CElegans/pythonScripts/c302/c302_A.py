from c302 import generate

import parameters_A as params

if __name__ == '__main__':
    
    cells_to_stimulate = ["ADAL", "ADAR"]
    cells_to_plot      = ["ADAL", "ADAR", "PVDR", "BDUR"]
    
    generate("c302_A", params, cells_to_plot=cells_to_plot, cells_to_stimulate=cells_to_stimulate, duration=500, dt=0.1, vmin=-72, vmax=-48)