import c302
import sys

import neuroml.writers as writers
    
def setup(parameter_set, 
          generate=False,
          duration=1000, 
          dt=0.05,
          target_directory='examples',
          data_reader="SpreadsheetDataReader"):

    exec('from parameters_%s import ParameterisedModel'%parameter_set)
    params = ParameterisedModel()
    
    params.set_bioparameter("unphysiological_offset_current", "0pA", "Testing IClamp", "0")
    params.set_bioparameter("unphysiological_offset_current_del", "100 ms", "Testing IClamp", "0")
    params.set_bioparameter("unphysiological_offset_current_dur", "20000 ms", "Testing IClamp", "0")
    
    
    my_cells = ["ADAL","PVCL","MDR1", "RMDL"]
    my_cells = ["ADAL", "PVCL", "RMDL", "VD13"]
    include_muscles = False
    
    cells               = my_cells
    cells_to_stimulate  = []
    
    reference = "c302_%s_IClamp"%parameter_set
    
    if generate:
        nml_doc = c302.generate(reference, 
                    params, 
                    cells=cells, 
                    cells_to_stimulate=cells_to_stimulate, 
                    include_muscles = include_muscles,
                    duration=duration, 
                    dt=dt, 
                    validate=('B' not in parameter_set),
                    vmin=-65,
                    vmax=100,
                    target_directory=target_directory)

        c302.add_new_input(nml_doc, "PVCL", "50ms", "50ms", "0.5pA", params)
        c302.add_new_input(nml_doc, "PVCL", "200ms", "50ms", "1pA", params)
        c302.add_new_input(nml_doc, "PVCL", "300ms", "50ms", "2pA", params)
        c302.add_new_input(nml_doc, "PVCL", "400ms", "50ms", "5pA", params)
        c302.add_new_input(nml_doc, "PVCL", "500ms", "50ms", "7pA", params)
        c302.add_new_input(nml_doc, "PVCL", "600ms", "50ms", "10pA", params)
        c302.add_new_input(nml_doc, "PVCL", "700ms", "50ms", "14pA", params)
        c302.add_new_input(nml_doc, "PVCL", "1450ms", "50ms", "7pA", params)
        c302.add_new_input(nml_doc, "PVCL", "1800ms", "300ms", "14pA", params)
        c302.add_new_input(nml_doc, "PVCL", "2150ms", "300ms", "30pA", params)

        c302.add_new_input(nml_doc, "RMDL", "300ms", "1500ms", "-4pA", params)
        c302.add_new_input(nml_doc, "ADAL", "500ms", "1500ms", "100pA", params)

        nml_file = target_directory+'/'+reference+'.nml'
        writers.NeuroMLWriter.write(nml_doc, nml_file) # Write over network file written above...
                    
    return cells, cells_to_stimulate, params, include_muscles
             
if __name__ == '__main__':
    
    parameter_set = sys.argv[1] if len(sys.argv)==2 else 'A'
    
    setup(parameter_set, generate=True)
