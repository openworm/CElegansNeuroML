import c302
import sys


def setup(parameter_set,
          generate=False,
          duration=1000,
          dt=0.05,
          target_directory='examples',
          data_reader="SpreadsheetDataReader"):
    exec ('from parameters_%s import ParameterisedModel' % parameter_set)
    params = ParameterisedModel()

    params.set_bioparameter("unphysiological_offset_current", "5pA", "Testing IClamp", "0")
    params.set_bioparameter("unphysiological_offset_current_del", "100 ms", "Testing IClamp", "0")
    params.set_bioparameter("unphysiological_offset_current_dur", "800 ms", "Testing IClamp", "0")

    my_cells = ["ADAL", "PVCL", "MDR1"]
    my_cells = ["ADAL", "PVCL"]
    muscles_to_include = ['MDR01']

    cells = my_cells
    cells_to_stimulate = my_cells + muscles_to_include

    reference = "c302_%s_IClamp" % parameter_set

    if generate:
        c302.generate(reference,
                      params,
                      cells=cells,
                      cells_to_stimulate=cells_to_stimulate,
                      muscles_to_include=muscles_to_include,
                      duration=duration,
                      dt=dt,
                      validate=('B' not in parameter_set),
                      target_directory=target_directory)

    return cells, cells_to_stimulate, params, muscles_to_include


if __name__ == '__main__':
    parameter_set = sys.argv[1] if len(sys.argv) == 2 else 'A'

    setup(parameter_set, generate=True)