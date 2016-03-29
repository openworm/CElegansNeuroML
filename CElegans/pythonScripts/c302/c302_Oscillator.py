import c302
import sys

def setup(parameter_set, 
          generate=False,
          duration=600, 
          dt=0.1,
          target_directory='examples'):
    
    exec('from parameters_%s import ParameterisedModel'%parameter_set)
    params = ParameterisedModel()
    
    params.set_bioparameter("unphysiological_offset_current", "0.35nA", "Testing IClamp", "0")
    params.set_bioparameter("unphysiological_offset_current_del", "5 ms", "Testing IClamp", "0")
    params.set_bioparameter("unphysiological_offset_current_dur", "1000 ms", "Testing IClamp", "0")
    
    params.add_bioparameter("chem_exc_syn_gbase", "5 nS", "BlindGuess", "0.1")
    params.add_bioparameter("chem_exc_syn_decay", "5 ms", "BlindGuess", "0.1")
    params.add_bioparameter("chem_inh_syn_gbase", "5 nS", "BlindGuess", "0.1")
    params.add_bioparameter("chem_inh_syn_decay", "20 ms", "BlindGuess", "0.1")
    params.add_bioparameter("elec_syn_gbase", "0.2 nS", "BlindGuess", "0.1")
    
    # Any neurons connected to muscles
    
    cells = ['DB1', 'DB2', 'DB3', 'DB4', 'DB5', 'DB6', 'DB7', 
             'VB1', 'VB10', 'VB11', 'VB2', 'VB3', 'VB4', 'VB5', 'VB6', 'VB7', 'VB8', 'VB9']
             
    cells+=['AVBL','PVCL']
    #cells=None  # implies all cells...     
    
    
    cells_to_stimulate = ['PVCL', 'AVBL']
    
    # Plot some directly stimulated & some not stimulated
    cells_to_plot      = ['AVBL','PVCL', 'PVCR', 'DB1','DB2', 'DB4','DB4','VB1','VB2', 'VB3', 'VB4']
    
    reference = "c302_%s_Oscillator"%parameter_set
    
    include_muscles = True
    #include_muscles = False
    
    if generate:
        c302.generate(reference, 
                    params, 
                    cells=cells,
                    cells_to_plot=cells_to_plot, 
                    cells_to_stimulate=cells_to_stimulate, 
                    include_muscles = include_muscles,
                    duration=duration, 
                    dt=dt, 
                    validate=(parameter_set!='B'),
                    target_directory=target_directory)  

    return cells, cells_to_stimulate, params, include_muscles
             
if __name__ == '__main__':
    
    parameter_set = sys.argv[1] if len(sys.argv)==2 else 'A'
    
    setup(parameter_set, generate=True)
