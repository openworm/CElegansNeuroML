from c302 import generate
import sys

if __name__ == '__main__':
    
    parameter_set = sys.argv[1] if len(sys.argv)==2 else 'A'
    
    exec('from parameters_%s import ParameterisedModel'%parameter_set)
    params = ParameterisedModel()
    
    exc_pre = "URYDL"
    exc_post = "SMDDR"
    inh_pre = "VD12" 
    inh_post = "VB11"
    gap_1 = "AIZL"
    gap_2 = "ASHL"
    
    cells = [exc_pre, exc_post, inh_pre, inh_post]
    cells_to_stimulate      = [exc_pre, inh_pre]
    
    if parameter_set=='B':
        cells.append(gap_1)
        cells.append(gap_2)
        cells_to_stimulate.append(gap_1)
    
    reference = "c302_%s_Syns"%parameter_set
    
    generate(reference, 
             params, 
             cells=cells, 
             cells_to_stimulate=cells_to_stimulate, 
             duration=500, 
             dt=0.1, 
             vmin=-72 if parameter_set=='A' else -52, 
             vmax=-48 if parameter_set=='A' else -28,
             validate=(parameter_set!='B'),
             target_directory='examples')