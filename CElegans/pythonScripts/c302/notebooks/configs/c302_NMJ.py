import sys
sys.path.append('../../../')

from CElegans.pythonScripts.c302 import c302
import neuroml.writers as writers
    
def setup(parameter_set, 
          generate=False,
          duration=3000, 
          dt=0.05,
          target_directory='examples',
          data_reader="SpreadsheetDataReader",
          param_overrides={},
          verbose=True):

    exec('from parameters_%s import ParameterisedModel'%parameter_set)
    params = ParameterisedModel()
    
    stim_amplitudes = ["1pA","2pA","3pA","4pA","10pA","15pA"]
    duration = (len(stim_amplitudes))*1000
    
    
    cells = ['VB1']
    muscles_to_include = ['MVL07']
    
    cells_total = list(cells + muscles_to_include)
    
    
    reference = "c302_%s_NMJ"%parameter_set
    
    
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
        for c in cells:
            c302.add_new_input(nml_doc, c, start, "800ms", stim_amplitudes[i], params)
    
    
    nml_file = target_directory+'/'+reference+'.nml'
    writers.NeuroMLWriter.write(nml_doc, nml_file) # Write over network file written above...
    
    print("(Re)written network file to: "+nml_file)
                    
    return cells, cells_total, params, muscles_to_include
             
if __name__ == '__main__':
    
    parameter_set = sys.argv[1] if len(sys.argv)>=2 else 'C0'
    data_reader = sys.argv[2] if len(sys.argv) >= 3 else 'SpreadsheetDataReader'
    
    setup(parameter_set, generate=True, data_reader=data_reader)
