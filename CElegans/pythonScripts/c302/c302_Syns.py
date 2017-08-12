import c302
import sys
import neuroml.writers as writers

    
def setup(parameter_set, 
          generate=False,
          duration=500, 
          dt=0.05,
          target_directory='examples',
          data_reader="SpreadsheetDataReader",
          param_overrides={},
          config_param_overrides={},
          verbose=True):
    
    exec('from parameters_%s import ParameterisedModel'%parameter_set)
    params = ParameterisedModel()
    
    stim_amplitudes = ["3pA","5pA"]
    duration = (len(stim_amplitudes))*1000
    
    params.set_bioparameter("unphysiological_offset_current_del", "50 ms", "Testing IClamp", "0")
    
    exc_pre = "URYDL"
    exc_post = "SMDDR"
    inh_pre = "VD12" 
    inh_post = "VB11"
    gap_1 = "AIZL"
    gap_2 = "ASHL"
    
    cells = [exc_pre, exc_post, inh_pre, inh_post]
    cells_to_stimulate_extra      = [exc_pre, inh_pre]
    
    if parameter_set!='A':
        cells.append(gap_1)
        cells.append(gap_2)
        cells_to_stimulate_extra.append(gap_1)
    
    reference = "c302_%s_Syns"%parameter_set
    
    if generate:
        nml_doc = c302.generate(reference, 
                 params, 
                 cells=cells, 
                 cells_to_stimulate=[], 
                 duration=duration, 
                 dt=dt, 
                 target_directory=target_directory,
                 param_overrides=param_overrides,
                 verbose=verbose)
                 
                 
    for i in range(len(stim_amplitudes)):
        start = "%sms"%(i*1000 + 100)
        for c in cells_to_stimulate_extra:
            c302.add_new_input(nml_doc, c, start, "800ms", stim_amplitudes[i], params)
    
    nml_file = target_directory+'/'+reference+'.nml'
    writers.NeuroMLWriter.write(nml_doc, nml_file) # Write over network file written above...
    
    print(("(Re)written network file to: "+nml_file))
    
             
    return cells, cells_to_stimulate_extra, params, []
             
if __name__ == '__main__':
    
    parameter_set = sys.argv[1] if len(sys.argv)==2 else 'A'
    
    setup(parameter_set, generate=True)