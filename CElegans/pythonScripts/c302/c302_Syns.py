import c302
import sys

    
def setup(parameter_set, 
          generate=False,
          duration=500, 
          dt=0.05,
          target_directory='examples'):
    
    exec('from parameters_%s import ParameterisedModel'%parameter_set)
    params = ParameterisedModel()
    
    params.set_bioparameter("unphysiological_offset_current_del", "50 ms", "Testing IClamp", "0")
    
    exc_pre = "URYDL"
    exc_post = "SMDDR"
    inh_pre = "VD12" 
    inh_post = "VB11"
    gap_1 = "AIZL"
    gap_2 = "ASHL"
    
    cells = [exc_pre, exc_post, inh_pre, inh_post]
    cells_to_stimulate      = [exc_pre, inh_pre]
    
    if parameter_set!='A':
        cells.append(gap_1)
        cells.append(gap_2)
        cells_to_stimulate.append(gap_1)
    
    reference = "c302_%s_Syns"%parameter_set
    
    if generate:
        c302.generate(reference, 
                 params, 
                 cells=cells, 
                 cells_to_stimulate=cells_to_stimulate, 
                 duration=duration, 
                 dt=dt, 
                 validate=(parameter_set!='B'),
                 target_directory=target_directory)
             
    return cells, cells_to_stimulate, params, False
             
if __name__ == '__main__':
    
    parameter_set = sys.argv[1] if len(sys.argv)==2 else 'A'
    
    setup(parameter_set, generate=True)