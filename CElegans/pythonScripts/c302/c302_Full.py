from c302 import generate
import sys

if __name__ == '__main__':
    
    parameter_set = sys.argv[1] if len(sys.argv)==2 else 'A'
    exec('from parameters_%s import ParameterisedModel'%parameter_set)
    params = ParameterisedModel()
    
    # Some random set of neurons
    cells_to_stimulate = ["ADAL", "ADAR", "M1","M2L","M3L","M3R","M4","I1R","I2L","I5","I6","MI","NSMR","MCL","ASEL", "AVEL", "AWAR", "DB1", "DVC", "RIAR", "RMDDL"]
    
    # Plot some directly stimulated & some not stimulated
    cells_to_plot      = ["ADAL", "ADAR", "PVDR", "BDUR","I1R","I2L"]
    
    reference = "c302_%s_Full"%parameter_set
    
    generate(reference, 
             params, 
             cells_to_plot=cells_to_plot, 
             cells_to_stimulate=cells_to_stimulate, 
             duration=500, 
             dt=0.1, 
             vmin=-72 if parameter_set=='A' else -52, 
             vmax=-48 if parameter_set=='A' else -28,
             validate=(parameter_set!='B'),
             target_directory='examples')    
