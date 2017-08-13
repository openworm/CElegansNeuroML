import sys
sys.path.append('../../../')

from CElegans.pythonScripts.c302 import c302

import neuroml.writers as writers

range_incl = lambda start, end:range(start, end + 1)

def setup(parameter_set,
          generate=False,
          duration=1000,
          dt=0.05,
          target_directory='examples',
          data_reader="SpreadsheetDataReader",
          param_overrides={},
          verbose=True):
    
    exec ('from parameters_%s import ParameterisedModel' % parameter_set)
    params = ParameterisedModel()

    params.set_bioparameter("unphysiological_offset_current", "0pA", "Testing TapWithdrawal", "0")
    params.set_bioparameter("unphysiological_offset_current_del", "0 ms", "Testing TapWithdrawal", "0")
    params.set_bioparameter("unphysiological_offset_current_dur", "2000 ms", "Testing TapWithdrawal", "0")

    stim_amplitudes = ["1pA", "2pA", "3pA", "4pA", "5pA", "6pA"]
    duration = (len(stim_amplitudes)) * 1000

    VA_motors = ["VA%s" % c for c in range_incl(1, 12)]
    VB_motors = ["VB%s" % c for c in range_incl(1, 11)]
    DA_motors = ["DA%s" % c for c in range_incl(1, 9)]
    DB_motors = ["DB%s" % c for c in range_incl(1, 7)]
    DD_motors = ["DD%s" % c for c in range_incl(1, 6)]
    VD_motors = ["VD%s" % c for c in range_incl(1, 13)]
    AS_motors = ["AS%s" % c for c in range_incl(1, 11)]

    cells = ['AVAL']

    muscles_to_include = ['MVL07', 'MVL08', 'MVL09', 'MVR07', 'MVR08', 'MVR09', 'MDL07', 'MDL08', 'MDL09', 'MDR07', 'MDR08', 'MDR09']

    cells_to_stimulate = []

    cells_to_plot = muscles_to_include
    
    reference = "c302_%s_MuscleSignalPropagation" % parameter_set

    conns_to_include = [
    ]

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
                                     conns_to_include=conns_to_include,
                                     conn_polarity_override=conn_polarity_override,
                                     conn_number_override=conn_number_override,
                                     muscles_to_include=muscles_to_include,
                                     duration=duration,
                                     dt=dt,
                                     target_directory=target_directory,
                                     data_reader=data_reader,
                                     param_overrides=param_overrides,
                                     verbose=verbose)

    for i in range(len(stim_amplitudes)):
        start = "%sms" % (i * 1000 + 100)
        c302.add_new_input(nml_doc, "MVL08", start, "800ms", stim_amplitudes[i], params)

    nml_file = target_directory + '/' + reference + '.nml'
    writers.NeuroMLWriter.write(nml_doc, nml_file)  # Write over network file written above...

    print("(Re)written network file to: " + nml_file)

    return cells, cells_to_stimulate, params, muscles_to_include, nml_doc


if __name__ == '__main__':
    parameter_set = sys.argv[1] if len(sys.argv) >= 2 else 'C2'
    data_reader = sys.argv[2] if len(sys.argv) >= 3 else 'UpdatedSpreadsheetDataReader'

    setup(parameter_set, generate=True, data_reader=data_reader)
