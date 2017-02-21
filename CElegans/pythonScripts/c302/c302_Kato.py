import c302
import sys

def setup(parameter_set,
          generate=False,
          duration=1080, #Match time run in Figure 1C of Kato et. al, Cell 2015 http://dx.doi.org/10.1016/j.cell.2015.09.034
          dt=0.1,
          target_directory='examples',
          muscles_to_include = None,
          data_reader="SpreadsheetDataReader",
          param_overrides={},
          verbose=True):

    exec('from parameters_%s import ParameterisedModel'%parameter_set)
    params = ParameterisedModel()

    # Match the labelled cells in Figure 1C of Kato et. al, Cell 2015 http://dx.doi.org/10.1016/j.cell.2015.09.034
    cells_to_stimulate = ["AVAR", "AVAL", "RIMR", "RIML", "AVER", "VA01", "SABVL", "OLQVL", "DB01", "VB01", "DB02", "RMER", "RMEL", "RID", "AVBR", "RIBL", "VB02", "RMED", "RMEV", "AVBL", "SMDVL", "SMDVR", "RIVL", "RIVR", "OLQVR", "OLQDL", "AIBL", "AIBR", "OLQDR", "RIFR", "SMBDR"]


    # Plot some directly stimulated & some not stimulated
    cells_to_plot = ["AVAR", "AVAL", "RIMR", "RIML", "AVER", "VA01", "SABVL", "OLQVL", "DB01", "VB01", "DB02", "RMER", "RMEL", "RID", "AVBR", "RIBL", "VB02", "RMED", "RMEV", "AVBL", "SMDVL", "SMDVR", "RIVL", "RIVR", "OLQVR", "OLQDL", "AIBL", "AIBR", "OLQDR", "RIFR", "SMBDR"]

    reference = "c302_%s_Kato"%parameter_set

    cell_names, conns = c302.get_cell_names_and_connection()

    if generate:
        c302.generate(reference,
             params,
             cells_to_plot=cells_to_plot,
             cells_to_stimulate=cells_to_stimulate,
             muscles_to_include = muscles_to_include,
             duration=duration,
             dt=dt,
             vmin=-72 if parameter_set=='A' else -52,
             vmax=-48 if parameter_set=='A' else -28,
             target_directory=target_directory,
             param_overrides=param_overrides,
             verbose=verbose)

    return cell_names, cells_to_stimulate, params, muscles_to_include


if __name__ == '__main__':

    parameter_set = sys.argv[1] if len(sys.argv)==2 else 'A'

    setup(parameter_set, generate=True)
