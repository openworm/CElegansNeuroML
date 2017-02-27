import c302
import sys

import neuroml.writers as writers


def setup(parameter_set,
          generate=False,
          duration=3000,
          dt=0.05,
          target_directory='examples',
          data_reader="UpdatedSpreadsheetDataReader"):
    
    exec ('from parameters_%s import ParameterisedModel' % parameter_set)
    params = ParameterisedModel()

    params.set_bioparameter("unphysiological_offset_current", "0pA", "Testing TapWithdrawal", "0")
    params.set_bioparameter("unphysiological_offset_current_del", "0 ms", "Testing TapWithdrawal", "0")
    params.set_bioparameter("unphysiological_offset_current_dur", "2000 ms", "Testing TapWithdrawal", "0")

    cells = ['ASHL']
    #cells += ['AVAL']
    #cells += ['DB6']

    muscles_to_include = False

  
    cells_to_stimulate = []

    cells_to_plot = cells
    reference = "c302_%s_SingleCellTest" % parameter_set

    conn_polarity_override = {
      
    }

    conn_number_override = {
       
    }

    if generate:
        nml_doc = c302.generate(reference,
                                params,
                                cells=cells,
                                cells_to_plot=cells_to_plot,
                                cells_to_stimulate=cells_to_stimulate,
                                conn_polarity_override=conn_polarity_override,
                                conn_number_override=conn_number_override,
                                muscles_to_include=muscles_to_include,
                                duration=duration,
                                dt=dt,
                                validate=(parameter_set != 'B'),
                                target_directory=target_directory,
                                data_reader=data_reader)

        c302.add_new_input(nml_doc, "ASHL", "100ms", "50ms", "0pA", params)
        c302.add_new_input(nml_doc, "ASHL", "400ms", "50ms", "0.1pA", params)
        c302.add_new_input(nml_doc, "ASHL", "700ms", "50ms", "0.5pA", params)
        c302.add_new_input(nml_doc, "ASHL", "1000ms", "50ms", "1pA", params)
        c302.add_new_input(nml_doc, "ASHL", "1300ms", "50ms", "1.5pA", params)
        c302.add_new_input(nml_doc, "ASHL", "1600ms", "50ms", "2pA", params)
        c302.add_new_input(nml_doc, "ASHL", "1900ms", "50ms", "5pA", params)
        c302.add_new_input(nml_doc, "ASHL", "2100ms", "50ms", "10pA", params)
        c302.add_new_input(nml_doc, "ASHL", "2400ms", "50ms", "15pA", params)

	c302.add_new_input(nml_doc, "ASHL", "2500ms", "400ms", "10.5pA", params)

        nml_file = target_directory + '/' + reference + '.nml'
        writers.NeuroMLWriter.write(nml_doc, nml_file)  # Write over network file written above...

        print("(Re)written network file to: " + nml_file)

    return cells, cells_to_stimulate, params, muscles_to_include


if __name__ == '__main__':
    parameter_set = sys.argv[1] if len(sys.argv) == 2 else 'C2'

    setup(parameter_set, generate=True, data_reader="UpdatedSpreadsheetDataReader")
