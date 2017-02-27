import c302
import sys

import neuroml.writers as writers


def setup(parameter_set,
          generate=False,
          duration=400,
          dt=0.005,
          target_directory='examples',
          data_reader="UpdatedSpreadsheetDataReader"):
    
    exec ('from parameters_%s import ParameterisedModel' % parameter_set)
    params = ParameterisedModel()

    params.set_bioparameter("unphysiological_offset_current", "0pA", "Testing TapWithdrawal", "0")
    params.set_bioparameter("unphysiological_offset_current_del", "0 ms", "Testing TapWithdrawal", "0")
    params.set_bioparameter("unphysiological_offset_current_dur", "20000 ms", "Testing TapWithdrawal", "0")

    cells = ['AVAL', 'AVAR']
    #muscles_to_include = ['MVR07']
    muscles_to_include = False
    
  
    cells_to_stimulate = []

    cells_to_plot = cells
    reference = "c302_%s_TestTest" % parameter_set

    conns_to_include = [
        'AVAL-AVAR',
        'AVAR-AVAL'
    ]

    conn_polarity_override = {
        'AVAL-AVAR':'inh',
        'AVAR-AVAL':'inh'
    }

    conn_number_override = {
        'AVAL-AVAR':10,
        'AVAR-AVAL':10
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
                                validate=(parameter_set != 'B'),
                                target_directory=target_directory,
                                data_reader=data_reader)

      
        c302.add_new_input(nml_doc, "AVAL", "10ms", "200ms", "5.5pA", params)
        c302.add_new_input(nml_doc, "AVAR", "10ms", "200ms", "5.5pA", params)

        nml_file = target_directory + '/' + reference + '.nml'
        writers.NeuroMLWriter.write(nml_doc, nml_file)  # Write over network file written above...

        print("(Re)written network file to: " + nml_file)

    return cells, cells_to_stimulate, params, muscles_to_include


if __name__ == '__main__':
    parameter_set = sys.argv[1] if len(sys.argv) == 2 else 'C2'

    setup(parameter_set, generate=True, data_reader="UpdatedSpreadsheetDataReader")
