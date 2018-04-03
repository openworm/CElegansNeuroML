import sys
from importlib import import_module

from c302 import c302
import neuroml.writers as writers
    
def setup(parameter_set, 
          generate=False,
          duration=3000, 
          dt=0.05,
          target_directory='examples',
          data_reader="SpreadsheetDataReader",
          param_overrides={},
          config_param_overrides={},
          verbose=True):

    parameters = import_module('c302.parameters_%s'%parameter_set)
    params = parameters.ParameterisedModel()
    
    stim_amplitudes = ["0pA"]*1 + ["2pA"]*2 + ["4pA"]*2 + ["2pA"]*2 + ["0pA"]*1
    #,"4pA","5pA","6pA"]["1pA","2pA","3pA","4pA","5pA","6pA"]
    duration = max(duration,(len(stim_amplitudes))*1000)
    
    
    cells = ['AVAL']
    muscles_to_include = ['MDR01']
    
    cells_total = list(cells + muscles_to_include)
    
    
    reference = "c302_%s_IClampBWM"%parameter_set
    
    if generate:
        nml_doc = c302.generate(reference,
                                params,
                                data_reader=data_reader,
                                cells=cells,
                                cells_to_stimulate=[],
                                muscles_to_include = muscles_to_include,
                                duration=duration,
                                dt=dt,
                                target_directory=target_directory,
                                param_overrides=param_overrides,
                                verbose=verbose)
                    
    for i in range(len(stim_amplitudes)):
        start = "%sms"%(i*1000 + 100)
        for c in muscles_to_include:
            c302.add_new_input(nml_doc, c, start, "800ms", stim_amplitudes[i], params)
    
    nml_file = target_directory+'/'+reference+'.nml'
    writers.NeuroMLWriter.write(nml_doc, nml_file) # Write over network file written above...
    
    print(("(Re)written network file to: "+nml_file))
                    
    return cells, cells_total, params, muscles_to_include
             
if __name__ == '__main__':
    
    parameter_set = sys.argv[1] if len(sys.argv)>=2 else 'C0'
    data_reader = sys.argv[2] if len(sys.argv) >= 3 else 'SpreadsheetDataReader'
    
    setup(parameter_set, generate=True, data_reader=data_reader)
