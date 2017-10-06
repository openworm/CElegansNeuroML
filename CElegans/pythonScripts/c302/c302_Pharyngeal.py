from c302 import c302
import sys

def setup(parameter_set, 
          generate=False,
          duration=500, 
          dt=0.01,
          target_directory='examples',
          data_reader="SpreadsheetDataReader",
          param_overrides={},
          config_param_overrides={},
          verbose=True):

    exec('from parameters_%s import ParameterisedModel'%parameter_set)
    params = ParameterisedModel()
    
    
    cells = ["M1","M2L","M2R","M3L","M3R","M4","M5","I1L","I1R","I2L","I2R","I3","I4","I5","I6","MI","NSML","NSMR","MCL","MCR"]
    cells_to_stimulate = ["M1","M3R","M4","M5","I1L","I4","I5","I6","MCL","MCR"]
    
    reference = "c302_%s_Pharyngeal"%parameter_set
    
    if generate:
        c302.generate(reference,  
                      params, 
                      cells=cells, 
                      cells_to_stimulate=cells_to_stimulate, 
                      duration=duration, 
                      dt=dt, 
                      target_directory=target_directory,
                      param_overrides=param_overrides,
                      verbose=verbose)
             
    return cells, cells_to_stimulate, params, []
             
if __name__ == '__main__':
    
    parameter_set = sys.argv[1] if len(sys.argv)==2 else 'A'
    
    setup(parameter_set, generate=True)