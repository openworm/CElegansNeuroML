from c302 import generate
import sys

if __name__ == '__main__':
    
    parameter_set = sys.argv[1] if len(sys.argv)==2 else 'A'
    exec('import parameters_%s as params'%parameter_set)
    
    pharyngeal_cells = ["M1","M2L","M2R","M3L","M3R","M4","M5","I1L","I1R","I2L","I2R","I3","I4","I5","I6","MI","NSML","NSMR","MCL","MCR"]
    cells_to_stimulate = ["M1","M3R","M4","M5","I1L","I4","I5","I6","MCL","MCR"]
    
    reference = "c302_%s_Pharyngeal"%parameter_set
    
    generate(reference, 
             params, 
             cells=pharyngeal_cells, 
             cells_to_stimulate=cells_to_stimulate, 
             duration=500, 
             dt=0.025, 
             vmin=-72 if parameter_set=='A' else -52, 
             vmax=-48 if parameter_set=='A' else -28,
             validate=(parameter_set!='B'))