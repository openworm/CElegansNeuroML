import sys
sys.path.append('../../../')

import c302

import neuroml.writers as writers

range_incl = lambda start, end:range(start, end + 1)

def setup(parameter_set,
          generate=False,
          duration=2000,
          dt=0.05,
          target_directory='../../../examples',
          data_reader="SpreadsheetDataReader",
          param_overrides={},
          verbose=True,
          config_param_overrides={}):
    
    exec ('from parameters_%s import ParameterisedModel' % parameter_set)
    params = ParameterisedModel()

    params.set_bioparameter("unphysiological_offset_current", "0pA", "Testing TapWithdrawal", "0")
    params.set_bioparameter("unphysiological_offset_current_del", "0 ms", "Testing TapWithdrawal", "0")
    params.set_bioparameter("unphysiological_offset_current_dur", "2000 ms", "Testing TapWithdrawal", "0")

    VA_motors = ["VA%s" % c for c in range_incl(1, 12)]
    VB_motors = ["VB%s" % c for c in range_incl(1, 11)]
    DA_motors = ["DA%s" % c for c in range_incl(1, 9)]
    DB_motors = ["DB%s" % c for c in range_incl(1, 7)]
    DD_motors = ["DD%s" % c for c in range_incl(1, 6)]
    VD_motors = ["VD%s" % c for c in range_incl(1, 13)]
    AS_motors = ["AS%s" % c for c in range_incl(1, 11)]

    cells = list(['AVAL', 'AVAR'] + VA_motors + DA_motors + VD_motors + DD_motors)

    muscles_to_include = True

    cells_to_stimulate = []

    cells_to_plot = list(cells)
    reference = "c302_%s_AVA_VA_DA_VD_DD" % parameter_set

    conns_to_include = [
    ]

    conn_polarity_override = {}
    if config_param_overrides.has_key('conn_polarity_override'):
        conn_polarity_override.update(config_param_overrides['conn_polarity_override'])

    conn_number_override = {}
    if config_param_overrides.has_key('conn_number_override'):
        conn_number_override.update(config_param_overrides['conn_number_override'])
    

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

        end = int(duration) - 500
        
        #for vb in VB_motors:
        #    c302.add_new_sinusoidal_input(nml_doc, cell=vb, delay="0ms", duration="1000ms", amplitude="3pA",
        #                                  period="700ms", params=params)

        #for db in DB_motors:
        #    c302.add_new_sinusoidal_input(nml_doc, cell=db, delay="0ms", duration="1000ms", amplitude="3pA",
        #                                  period="700ms", params=params)


        c302.add_new_input(nml_doc, "AVAL", "50ms", "%sms"%end, "15pA", params)
        c302.add_new_input(nml_doc, "AVAR", "50ms", "%sms"%end, "15pA", params)

        nml_file = target_directory + '/' + reference + '.nml'
        writers.NeuroMLWriter.write(nml_doc, nml_file)  # Write over network file written above...

        print("(Re)written network file to: " + nml_file)


    return cells, cells_to_stimulate, params, muscles_to_include


if __name__ == '__main__':
    parameter_set = sys.argv[1] if len(sys.argv) == 2 else 'C2'
    data_reader = sys.argv[2] if len(sys.argv) == 3 else 'UpdatedSpreadsheetDataReader'

    setup(parameter_set, generate=True, data_reader=data_reader)
