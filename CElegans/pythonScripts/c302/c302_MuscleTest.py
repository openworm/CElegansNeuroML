import sys
import os

sys.path.insert(0, os.path.abspath('.'))

import c302

import neuroml.writers as writers

range_incl = lambda start, end:range(start, end + 1)


def setup(parameter_set,
          generate=False,
          duration=2000,
          dt=0.05,
          target_directory='examples',
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


    cells = []

    muscles_to_include = True

    if config_param_overrides.has_key('muscles_to_include'):
        muscles_to_include = config_param_overrides['muscles_to_include']

    cells_to_stimulate = []

    cells_to_plot = list(cells)
    reference = "c302_%s_MuscleTest" % parameter_set


    conns_to_include = []
    if config_param_overrides.has_key('conns_to_include'):
        conns_to_include = config_param_overrides['conns_to_include']

    conns_to_exclude = ['^.+-.+$']
    if config_param_overrides.has_key('conns_to_exclude'):
        conns_to_exclude = config_param_overrides['conns_to_exclude']

    conn_polarity_override = {}
    if config_param_overrides.has_key('conn_polarity_override'):
        conn_polarity_override.update(config_param_overrides['conn_polarity_override'])

    conn_number_override = {

    }
    if config_param_overrides.has_key('conn_number_override'):
        conn_number_override.update(config_param_overrides['conn_number_override'])

    end = '%sms' % (int(duration) - 100)

    duration = 1000

    input_list = [
        ('MDL01', '100ms', '250ms', '1pA'),
        ('MDL02', '130ms', '250ms', '1pA'),
        ('MDL03', '160ms', '250ms', '1pA'),
        ('MDL04', '190ms', '250ms', '1pA'),
        ('MDL05', '210ms', '250ms', '1pA'),
        ('MDL06', '240ms', '250ms', '1pA'),
        ('MDL07', '270ms', '250ms', '1pA'),
        ('MDL08', '300ms', '250ms', '1pA'),
        ('MDL09', '330ms', '250ms', '1pA'),
        ('MDL10', '360ms', '250ms', '1pA'),

        ('MDR01', '100ms', '250ms', '1pA'),
        ('MDR02', '130ms', '250ms', '1pA'),
        ('MDR03', '160ms', '250ms', '1pA'),
        ('MDR04', '190ms', '250ms', '1pA'),
        ('MDR05', '210ms', '250ms', '1pA'),
        ('MDR06', '240ms', '250ms', '1pA'),
        ('MDR07', '270ms', '250ms', '1pA'),
        ('MDR08', '300ms', '250ms', '1pA'),
        ('MDR09', '330ms', '250ms', '1pA'),
        ('MDR10', '360ms', '250ms', '1pA'),

        ('MDL01', '600ms', '250ms', '1pA'),
        ('MDL02', '630ms', '250ms', '1pA'),
        ('MDL03', '660ms', '250ms', '1pA'),
        ('MDL04', '690ms', '250ms', '1pA'),
        ('MDL05', '710ms', '250ms', '1pA'),
        ('MDL06', '740ms', '250ms', '1pA'),
        ('MDL07', '770ms', '250ms', '1pA'),
        ('MDL08', '800ms', '250ms', '1pA'),
        ('MDL09', '830ms', '250ms', '1pA'),
        ('MDL10', '860ms', '250ms', '1pA'),

        ('MDR01', '600ms', '250ms', '1pA'),
        ('MDR02', '630ms', '250ms', '1pA'),
        ('MDR03', '660ms', '250ms', '1pA'),
        ('MDR04', '690ms', '250ms', '1pA'),
        ('MDR05', '710ms', '250ms', '1pA'),
        ('MDR06', '740ms', '250ms', '1pA'),
        ('MDR07', '770ms', '250ms', '1pA'),
        ('MDR08', '800ms', '250ms', '1pA'),
        ('MDR09', '830ms', '250ms', '1pA'),
        ('MDR10', '860ms', '250ms', '1pA'),
    ]

    nml_doc = None
    if generate:
        nml_doc = c302.generate(reference,
                                params,
                                cells=cells,
                                cells_to_plot=cells_to_plot,
                                cells_to_stimulate=cells_to_stimulate,
                                conns_to_include=conns_to_include,
                                conns_to_exclude=conns_to_exclude,
                                conn_polarity_override=conn_polarity_override,
                                conn_number_override=conn_number_override,
                                muscles_to_include=muscles_to_include,
                                duration=duration,
                                dt=dt,
                                target_directory=target_directory,
                                data_reader=data_reader,
                                param_overrides=param_overrides,
                                verbose=verbose)

        if config_param_overrides.has_key('input'):
            input_list = config_param_overrides['input']

        for stim_input in input_list:
            cell, start, dur, current = stim_input
            c302.add_new_input(nml_doc, cell, start, dur, current, params)

        nml_file = target_directory + '/' + reference + '.nml'
        writers.NeuroMLWriter.write(nml_doc, nml_file)  # Write over network file written above...

        print("(Re)written network file to: " + nml_file)


    return cells, cells_to_stimulate, params, muscles_to_include, nml_doc


if __name__ == '__main__':
    parameter_set = sys.argv[1] if len(sys.argv) == 2 else 'C2'
    data_reader = sys.argv[2] if len(sys.argv) == 3 else 'UpdatedSpreadsheetDataReader'

    setup(parameter_set, generate=True, data_reader=data_reader)
