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

    params.set_bioparameter("unphysiological_offset_current", "0pA", "Testing TapWithdrawal", "0")
    params.set_bioparameter("unphysiological_offset_current_del", "0 ms", "Testing TapWithdrawal", "0")
    params.set_bioparameter("unphysiological_offset_current_dur", "20000 ms", "Testing TapWithdrawal", "0")

    cells = ['AVM']
    #cells += ['AVDL']
    #cells += ['AVDR']
    #cells += ['AVAL']
    #cells += ['AVAR']
    #cells += ['VA1']
    #muscles_to_include = ['MVR07']
    muscles_to_include = False

    #cells = ['AVAL', 'AVAR', 'AVDL', 'AVDR', 'AVM', 'ALML', 'ALMR']
    
  
    cells_to_stimulate = []

    cells_to_plot = cells
    reference = "c302_%s_SynTest" % parameter_set

    conns_to_include = [
        'AVM-AVDR',# exc num:1
        #AVAR-AVDR exc num:6
        'AVDR-AVAR',# exc num:52
        #AVAR-AVDR_GJ num:15
        'AVAR-VA1_GJ',# num:7
        #AVDR-AVAR_GJ num:15
        #VA1-AVAR_GJ num:7
        'VA1-MVR07',# exc num:2
    ]

    conn_polarity_override = {
    }

    conn_number_override = {
        'AVM-AVDR':1,# exc num:1
      	'AVDR-AVAR':1,# exc num:52
        'AVAR-VA1_GJ':1,# num:7
        'VA1-MVR07':4,# exc num:2
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

        """c302.add_new_input(nml_doc, "AVM", "100ms", "50ms", "0.1pA", params)
        c302.add_new_input(nml_doc, "AVM", "400ms", "50ms", "0.2pA", params)
        c302.add_new_input(nml_doc, "AVM", "700ms", "50ms", "0.5pA", params)
        c302.add_new_input(nml_doc, "AVM", "1000ms", "50ms", "1pA", params)
        c302.add_new_input(nml_doc, "AVM", "1400ms", "50ms", "1.5pA", params)
        c302.add_new_input(nml_doc, "AVM", "1600ms", "50ms", "2pA", params)
        c302.add_new_input(nml_doc, "AVM", "1900ms", "50ms", "5pA", params)
        c302.add_new_input(nml_doc, "AVM", "2100ms", "50ms", "10pA", params)
        
        c302.add_new_input(nml_doc, "AVM", "2400ms", "400ms", "20pA", params)"""

        """c302.add_new_input(nml_doc, "ASHL", "100ms", "50ms", "0.1pA", params)
        c302.add_new_input(nml_doc, "ASHL", "400ms", "50ms", "0.2pA", params)
        c302.add_new_input(nml_doc, "ASHL", "700ms", "50ms", "0.5pA", params)
        c302.add_new_input(nml_doc, "ASHL", "1000ms", "50ms", "1pA", params)
        c302.add_new_input(nml_doc, "ASHL", "1300ms", "50ms", "1.5pA", params)
        c302.add_new_input(nml_doc, "ASHL", "1600ms", "50ms", "2pA", params)
        c302.add_new_input(nml_doc, "ASHL", "1900ms", "50ms", "5pA", params)
        c302.add_new_input(nml_doc, "ASHL", "2100ms", "50ms", "10pA", params)
        c302.add_new_input(nml_doc, "ASHL", "2400ms", "50ms", "15pA", params)

        c302.add_new_input(nml_doc, "ASHL", "2500ms", "400ms", "10.5pA", params)"""

        """c302.add_new_input(nml_doc, "AVM", "100ms", "50ms", "0pA", params)
        c302.add_new_input(nml_doc, "AVM", "400ms", "50ms", "0.1pA", params)
        c302.add_new_input(nml_doc, "AVM", "700ms", "50ms", "0.5pA", params)
        c302.add_new_input(nml_doc, "AVM", "1000ms", "50ms", "1pA", params)
        c302.add_new_input(nml_doc, "AVM", "1300ms", "50ms", "1.5pA", params)
        c302.add_new_input(nml_doc, "AVM", "1600ms", "50ms", "2pA", params)
        c302.add_new_input(nml_doc, "AVM", "1900ms", "50ms", "5pA", params)
        c302.add_new_input(nml_doc, "AVM", "2100ms", "50ms", "10pA", params)
        c302.add_new_input(nml_doc, "AVM", "2400ms", "50ms", "15pA", params)

        c302.add_new_input(nml_doc, "AVM", "2500ms", "400ms", "10.5pA", params)

        c302.add_new_input(nml_doc, "ALML", "100ms", "50ms", "0pA", params)
        c302.add_new_input(nml_doc, "ALML", "400ms", "50ms", "0.1pA", params)
        c302.add_new_input(nml_doc, "ALML", "700ms", "50ms", "0.5pA", params)
        c302.add_new_input(nml_doc, "ALML", "1000ms", "50ms", "1pA", params)
        c302.add_new_input(nml_doc, "ALML", "1300ms", "50ms", "1.5pA", params)
        c302.add_new_input(nml_doc, "ALML", "1600ms", "50ms", "2pA", params)
        c302.add_new_input(nml_doc, "ALML", "1900ms", "50ms", "5pA", params)
        c302.add_new_input(nml_doc, "ALML", "2100ms", "50ms", "10pA", params)
        c302.add_new_input(nml_doc, "ALML", "2400ms", "50ms", "15pA", params)

        c302.add_new_input(nml_doc, "ALML", "2500ms", "400ms", "10.5pA", params)

        c302.add_new_input(nml_doc, "ALMR", "100ms", "50ms", "0pA", params)
        c302.add_new_input(nml_doc, "ALMR", "400ms", "50ms", "0.1pA", params)
        c302.add_new_input(nml_doc, "ALMR", "700ms", "50ms", "0.5pA", params)
        c302.add_new_input(nml_doc, "ALMR", "1000ms", "50ms", "1pA", params)
        c302.add_new_input(nml_doc, "ALMR", "1300ms", "50ms", "1.5pA", params)
        c302.add_new_input(nml_doc, "ALMR", "1600ms", "50ms", "2pA", params)
        c302.add_new_input(nml_doc, "ALMR", "1900ms", "50ms", "5pA", params)
        c302.add_new_input(nml_doc, "ALMR", "2100ms", "50ms", "10pA", params)
        c302.add_new_input(nml_doc, "ALMR", "2400ms", "50ms", "15pA", params)

        c302.add_new_input(nml_doc, "ALMR", "2500ms", "400ms", "10.5pA", params)"""

        nml_file = target_directory + '/' + reference + '.nml'
        writers.NeuroMLWriter.write(nml_doc, nml_file)  # Write over network file written above...

        print("(Re)written network file to: " + nml_file)

    return cells, cells_to_stimulate, params, muscles_to_include


if __name__ == '__main__':
    parameter_set = sys.argv[1] if len(sys.argv) == 2 else 'C2'

    setup(parameter_set, generate=True, data_reader="UpdatedSpreadsheetDataReader")
