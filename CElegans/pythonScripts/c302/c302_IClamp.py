import c302
import sys
import neuroml.writers as writers
    
def setup(parameter_set, 
          generate=False,
          duration=3000, 
          dt=0.05,
          target_directory='examples',
          data_reader="SpreadsheetDataReader"):

    exec('from parameters_%s import ParameterisedModel'%parameter_set)
    params = ParameterisedModel()
    
    stim_amplitudes = ["1pA","2pA","3pA","4pA","5pA","6pA"]
    duration = (len(stim_amplitudes))*1000
    
    
    my_cells = ["ADAL","PVCL"]
    muscles_to_include = ['MDR01']
    
    cells               = my_cells
    cells_total  = my_cells + muscles_to_include
    
    reference = "c302_%s_IClamp"%parameter_set
    
    
    if generate:
        nml_doc = c302.generate(reference, 
                    params, 
                    cells=cells, 
                    cells_to_stimulate=[], 
                    muscles_to_include = muscles_to_include,
                    duration=duration, 
                    dt=dt, 
                    target_directory=target_directory)
                    
    for i in range(len(stim_amplitudes)):
        start = "%sms"%(i*1000 + 100)
        for c in cells_total:
            c302.add_new_input(nml_doc, c, start, "800ms", stim_amplitudes[i], params)
    
    
    nml_file = target_directory+'/'+reference+'.nml'
    writers.NeuroMLWriter.write(nml_doc, nml_file) # Write over network file written above...
    
    print("(Re)written network file to: "+nml_file)
                    
    return cells, cells_total, params, muscles_to_include
             
if __name__ == '__main__':
    
    parameter_set = sys.argv[1] if len(sys.argv)==2 else 'A'
    
    setup(parameter_set, generate=True)