import c302
import sys

import neuroml.writers as writers


def setup(parameter_set,
          generate=False,
          duration=400,
          dt=0.05,
          target_directory='examples',
          data_reader="UpdatedSpreadsheetDataReader"):
    
    exec ('from parameters_%s import ParameterisedModel' % parameter_set)
    params = ParameterisedModel()

    #params.set_bioparameter("unphysiological_offset_current", "0pA", "Testing TapWithdrawal", "0")
    params.set_bioparameter("unphysiological_offset_current_del", "0 ms", "Testing TapWithdrawal", "0")
    params.set_bioparameter("unphysiological_offset_current_dur", "2000 ms", "Testing TapWithdrawal", "0")

    cells = ['VB1', 'VB2', 'VB3', 'DB1', 'DB2', 'DB3', 'DD1', 'DD2', 'DD3', 'VD1', 'VD2', 'VD3', 'VA2', 'VA3', 'DA2', 'DA3']
    #cells += ['AVAL']
    #cells += ['DB6']

    muscles_to_include = ['MVL11', 'MVR11', 'MDL11', 'MDR11']

  
    cells_to_stimulate = ['VB2']

    cells_to_plot = cells
    reference = "c302_%s_VB_DB_DD_VD_ToMuscleTest" % parameter_set

    conns_to_include = [
        #'VA1-MVL07'
    ]

    conn_polarity_override = {
      
    }

    conn_number_override = {
        #'VA1-MVL07':1
    }

    
    

    if generate:
        nml_doc = c302.generate(reference,
                                params,
                                cells=cells,
                                cells_to_plot=cells_to_plot,
                                cells_to_stimulate=cells_to_stimulate,
                                conns_to_include=conns_to_include,
                                conn_polarity_override=conn_polarity_override,
                                conn_number_override=conn_number_override,
                                muscles_to_include=muscles_to_include,
                                duration=duration,
                                dt=dt,
                                target_directory=target_directory,
                                data_reader=data_reader)


    return cells, cells_to_stimulate, params, muscles_to_include


if __name__ == '__main__':
    parameter_set = sys.argv[1] if len(sys.argv) == 2 else 'C2'

    setup(parameter_set, generate=True, data_reader="UpdatedSpreadsheetDataReader")
