import c302
import sys

def setup(parameter_set, 
          generate=False,
          duration=1000, 
          dt=0.1,
          target_directory='examples'):
    
    exec('from parameters_%s import ParameterisedModel'%parameter_set)
    params = ParameterisedModel()
    
    #params.set_bioparameter("unphysiological_offset_current", "5pA", "Testing IClamp", "0")
    params.set_bioparameter("unphysiological_offset_current_del", "5 ms", "Testing IClamp", "0")
    params.set_bioparameter("unphysiological_offset_current_dur", "1000 ms", "Testing IClamp", "0")
    
    #params.add_bioparameter("chem_exc_syn_gbase", ".02 nS", "BlindGuess", "0.1")
    params.add_bioparameter("chem_exc_syn_decay", "5 ms", "BlindGuess", "0.1")
    
    #params.add_bioparameter("chem_inh_syn_gbase", ".02 nS", "BlindGuess", "0.1")
    params.add_bioparameter("chem_inh_syn_decay", "30 ms", "BlindGuess", "0.1")
    params.add_bioparameter("inh_syn_erev", "-90 mV", "BlindGuess", "0.1")
    
    #params.add_bioparameter("elec_syn_gbase", "0.001 nS", "BlindGuess", "0.1")
    
    # Any neurons connected to muscles
    
    cells = ['DB1', 'DB2', 'DB3', 'DB4', 'DB5', 'DB6', 'DB7', 
             'DD1', 'DD2', 'DD3', 'DD4', 'DD5', 'DD6',
             'VB1', 'VB10', 'VB11', 'VB2', 'VB3', 'VB4', 'VB5', 'VB6', 'VB7', 'VB8', 'VB9',
             'VD1', 'VD10', 'VD11', 'VD2', 'VD3', 'VD4', 'VD5', 'VD6', 'VD7', 'VD8', 'VD9']
    
    cells = ['DB3', 'VB3', 'DD3', 'VD3', 'DB4', 'VB4', 'DD4', 'VD4']
             
    #cells+=['AVBL','PVCL','AVBR','PVCR']
    #cells+=['AVBL']
    cells+=['PVCL']
    #cells=None  # implies all cells...     
    
    
    cells_to_stimulate = ['PVCL', 'AVBL','AVBR','PVCR']
    #cells_to_stimulate = ['AVBL']
    
    # Plot some directly stimulated & some not stimulated
    cells_to_plot      = ['AVBL','PVCL', 'PVCR', 'DB1','DB2','DB3', 'DB4','DD1','DD2','DD3', 'DD4','DB4','VB1','VB2', 'VB3', 'VB4','VD1','VD2', 'VD3', 'VD4']
    cells_to_plot      = cells
    
    reference = "c302_%s_Oscillator"%parameter_set
    
    include_muscles = True
    include_muscles = False
    
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
