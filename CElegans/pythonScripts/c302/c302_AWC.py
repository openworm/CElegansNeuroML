import c302
import sys

import neuroml.writers as writers

    
def setup(parameter_set, 
          generate=False,
          target_directory='examples',
          data_reader="SpreadsheetDataReader"):
    
    exec('from parameters_%s import ParameterisedModel'%parameter_set)
    params = ParameterisedModel()
    
    
    cells = ['RIAL', 'RIAR', 'SMDVL', 'SMDVR', 'SMDDL', 'SMDDR', 'AIYL', 'AIYR', 'AWCL', 'AWCR']
    #cells = None
    cells_to_stimulate = []
    
    reference = "c302_%s_AWC"%parameter_set
    
    nml_doc = None
    
    if generate:
        nml_doc = c302.generate(reference, 
                 params, 
                 cells=cells, 
                 cells_to_stimulate=cells_to_stimulate, 
                 duration=800, 
                 dt=0.1, 
                 target_directory = target_directory)
                 
        stim_amplitude = "0.6nA"

        c302.add_new_input(nml_doc, "AWCL", "100ms", "100ms", stim_amplitude, params)
        c302.add_new_input(nml_doc, "AWCR", "500ms", "100ms", stim_amplitude, params)
        
        nml_file = target_directory+'/'+reference+'.nml'
        writers.NeuroMLWriter.write(nml_doc, nml_file) # Write over network file written above...

        print("(Re)written network file to: "+nml_file)
             
    return cells, cells_to_stimulate, params, [], nml_doc
             
if __name__ == '__main__':
    
    parameter_set = sys.argv[1] if len(sys.argv)==2 else 'A'
    
    setup(parameter_set, generate=True)