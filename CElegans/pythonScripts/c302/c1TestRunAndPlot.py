import sys
import os
from pyneuroml import pynml
import c302_utils
import shutil

from collections import OrderedDict

def print_msg(msg):
    print "testRunAndPlot\t\t>>>\t%s" % msg

def main(name_post="", cells=[], cells_to_stimulate=[], cells_to_plot=[], conn_polarity_override={}, conn_number_override={}, parameter_set="C2", duration=500, dt=0.05, simulator="jNeuroML_NEURON", save=True, show_plot_already=False, data_reader="UpdatedSpreadsheetDataReader"):
    
    #exec('from c302_%s import setup'%config)
    """cells, cells_to_stimulate, params, muscles = setup(parameter_set, 
                                                       data_reader=data_reader,
                                                       generate=True,
                                                       duration = duration, 
                                                       dt = dt,
                                                       target_directory='examples')"""

    parent_dir = "synapses"
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)
        print_msg("Created dir %s" % parent_dir)
    #os.chdir(parent_dir)

    config = "_".join(cells) + "__stim_" + "_".join(cells_to_stimulate)

    save_dir = os.path.join(parent_dir, config+name_post)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print_msg("Created dir %s" % save_dir)

    save_fig_dir = os.path.join(save_dir, "figures")
    if not os.path.exists(save_fig_dir):
        os.makedirs(save_fig_dir)
        print_msg("Created dir %s" % save_fig_dir)
    save_fig_dir = "figures"

    #os.chdir(save_dir)
    
    
    cells_str = "['" + "','".join(cells) + "']"
    cells_to_plot_str = "['" + "','".join(cells_to_plot) + "']"
    
    cells_to_stimulate_str = "[]"
    if cells_to_stimulate:
        cells_to_stimulate_str = "['" + "','".join(cells_to_stimulate) + "']"
    
    i = 1
    conn_polarity_override_str = "{"
    for key, value in conn_polarity_override.iteritems():
        if i < len(conn_polarity_override.keys()):
            comma = ","
        else:
            comma = ""
        conn_polarity_override_str += "'%s':'%s'%s" % (key, value, comma)
        i += 1
    conn_polarity_override_str += "}"
    if conn_polarity_override_str == "{}": conn_polarity_override_str = None

    i = 1
    conn_number_override_str = "{"
    for key, value in conn_number_override.iteritems():
        if i < len(conn_number_override.keys()):
            comma = ","
        else:
            comma = ""
        conn_number_override_str += "'%s':%s%s" % (key, value, comma)
        i += 1
    conn_number_override_str += "}"
    if conn_number_override_str == "{}": conn_number_override_str = None

    filename = "%s_%s%s" % (parameter_set, config, name_post)
    command = 'python c302.py %s parameters_%s -cells %s -cellstoplot %s -cellstostimulate %s -connpolarityoverride %s -connnumberoverride %s -duration %s -datareader %s -dt %s' \
              % (filename, parameter_set, cells_str, cells_to_plot_str, cells_to_stimulate_str, conn_polarity_override_str, conn_number_override_str, duration, data_reader, dt)

    print_msg("Calling command %s" % command)
    from subprocess import call
    call(command, shell=True)


    nml_file = "%s.nml" % filename
    lems_file = 'LEMS_%s.xml' % (filename)
    
    #print_msg("move %s to %s" % (src, dst))
    shutil.move(lems_file, os.path.join(save_dir, lems_file))
    print_msg("Moved %s to %s" % (lems_file, os.path.join(save_dir, lems_file)))
    shutil.move(nml_file, os.path.join(save_dir, nml_file))
    print_msg("Moved %s to %s" % (nml_file, os.path.join(save_dir, nml_file)))
    shutil.copy("cell_C.xml", os.path.join(save_dir, "cell_C.xml"))
    print_msg("Copied %s to %s" % ("cell_C.xml", os.path.join(save_dir, "cell_C.xml")))
    
    os.chdir(save_dir)
    
    if simulator == 'jNeuroML':
        results = pynml.run_lems_with_jneuroml(lems_file, nogui=True, load_saved_data=True, verbose=True)
    elif simulator == 'jNeuroML_NEURON':
        results = pynml.run_lems_with_jneuroml_neuron(lems_file, nogui=True, load_saved_data=True, verbose=True)
        
    c302_utils.plot_c302_results(results, config, parameter_set, directory=save_fig_dir,save=save,show_plot_already=show_plot_already, data_reader=data_reader)
    
    os.chdir('../..')
    
    
if __name__ == '__main__':
    range_incl = lambda start, end: range(start, end + 1)
    VA_cells = ["VA%s"%c for c in range_incl(1, 12)]
    VB_cells = ["VB%s"%c for c in range_incl(1, 11)]
    DA_cells = ["DA%s"%c for c in range_incl(1, 9)]
    DB_cells = ["DB%s"%c for c in range_incl(1, 7)]
    DD_cells = ["DD%s"%c for c in range_incl(1, 6)]
    TW_cells = ['AVAL', 'AVAR', 'AVBL', 'AVBR', 'PVCL', 'PVCR', 'AVDL', 'AVDR', 'DVA', 'PVDL', 'PVDR', 'PLML', 'PLMR', 'AVM', 'ALML', 'ALMR']
    TW_sensory = ["PLML", "PLMR", "AVM", "ALML", "ALMR"]
    
    #PLM-PVC, stim PLM
    cells = ["PLML"]
    cells_to_plot = cells
    main(cells=cells, cells_to_stimulate=cells, cells_to_plot=cells_to_plot, parameter_set="C1")
    main(cells=cells, cells_to_stimulate=cells, cells_to_plot=cells_to_plot, parameter_set="C2")

    cells = ["ALML", "PVCL"]
    cells_to_plot = cells
    main(name_post="_exc", cells=cells, cells_to_stimulate=["ALML"], cells_to_plot=cells_to_plot, conn_polarity_override={"ALML-PVCL":"exc"}, conn_number_override={"ALML-PVCL":1}, parameter_set="C1")
    main(name_post="_exc", cells=cells, cells_to_stimulate=["ALML"], cells_to_plot=cells_to_plot, conn_polarity_override={"ALML-PVCL":"exc"}, conn_number_override={"ALML-PVCL":1}, parameter_set="C2")

    main(name_post="_inh", cells=cells, cells_to_stimulate=["ALML"], cells_to_plot=cells_to_plot, conn_polarity_override={"ALML-PVCL":"inh"}, conn_number_override={"ALML-PVCL":1}, parameter_set="C1")
    main(name_post="_inh", cells=cells, cells_to_stimulate=["ALML"], cells_to_plot=cells_to_plot, conn_polarity_override={"ALML-PVCL":"inh"}, conn_number_override={"ALML-PVCL":1}, parameter_set="C2")

    cells = ["PLML", "PVCL"]
    cells_to_plot = cells
    main(cells=cells, cells_to_stimulate=["PLML"], cells_to_plot=cells_to_plot, conn_number_override={"PLML-PVCL_GJ":1}, parameter_set="C1")
    main(cells=cells, cells_to_stimulate=["PLML"], cells_to_plot=cells_to_plot, conn_number_override={"PLML-PVCL_GJ":1}, parameter_set="C2")

    #main(cells=TW_cells, cells_to_stimulate=TW_sensory, parameter_set="C1")
    #main(cells=TW_cells, cells_to_stimulate=TW_sensory, parameter_set="C2")
    
    """cells = ['AVAL', 'AVAR', 'AVBL', 'AVBR', 'PVCL', 'PVCR', 'AVDL', 'AVDR', 'DVA', 'PVDL', 'PVDR', 'PLML', 'PLMR', 'AVM', 'ALML', 'ALMR']
    cells_to_plot = list(cells)
    #cells_to_stimulate = ["PLML", "PLMR"]
    #cells_to_stimulate = ["AVM", "ALML", "ALMR"]
    cells_to_stimulate = ["PLML", "PLMR", "AVM", "ALML", "ALMR"]
    conn_polarity_override = {
        'ALML-ALML':'inh',
        'ALML-PVCL':'inh',
        'ALML-PVCR':'inh',
        'ALML-AVDR':'inh',
        'ALMR-PVCR':'inh',

        'AVM-PVCL':'inh',
        'AVM-PVCR':'inh',
        'AVM-AVBL':'inh',
        'AVM-AVBR':'inh',
        'AVM-AVDL':'inh',
        'AVM-AVDR':'inh',

        'PVDL-PVDR':'inh',
        'PVDL-PVCL':'inh',
        'PVDL-PVCR':'inh',
        'PVDL-AVAL':'inh',
        'PVDL-AVAR':'inh',
        'PVDL-AVDL':'inh',
        'PVDL-AVDR':'inh',
        'PVDR-PVDL':'inh',
        'PVDR-DVA':'inh',
        'PVDR-PVCL':'inh',
        'PVDR-PVCR':'inh',
        'PVDR-AVAL':'inh',
        'PVDR-AVAR':'inh',
        'PVDR-AVDL':'inh',

        'DVA-PVCL':'inh',
        'DVA-PVCR':'inh',
        'DVA-AVAL':'inh',
        'DVA-AVAR':'inh',
        'DVA-AVBL':'inh',
        'DVA-AVBR':'inh',
        'DVA-AVDR':'inh',

        'PVCL-DVA':'exc',
        'PVCL-PVCL':'exc',
        'PVCL-PVCR':'exc',
        'PVCL-AVAL':'inh',
        'PVCL-AVAR':'inh',
        'PVCL-AVBL':'exc',
        'PVCL-AVBR':'exc',
        'PVCL-AVDL':'inh',
        'PVCL-AVDR':'inh',
        'PVCR-PVDL':'exc',
        'PVCR-PVDR':'exc',
        'PVCR-DVA':'exc',
        'PVCR-PVCL':'exc',
        'PVCR-AVAL':'inh',
        'PVCR-AVAR':'inh',
        'PVCR-AVBL':'exc',
        'PVCR-AVBR':'exc',
        'PVCR-AVDL':'inh',
        'PVCR-AVDR':'inh',

        'AVAL-PVCL':'inh',
        'AVAL-PVCR':'inh',
        'AVAL-AVAR':'inh',
        'AVAL-AVBL':'inh',
        'AVAL-AVDL':'inh',
        'AVAL-AVDR':'inh',

        'AVAR-PVCL':'inh',
        'AVAR-PVCR':'inh',
        'AVAR-AVAL':'inh',
        'AVAR-AVBL':'inh',
        'AVAR-AVBR':'inh',
        'AVAR-AVDL':'inh',
        'AVAR-AVDR':'inh',

        'AVBL-DVA':'inh',
        'AVBL-PVCR':'inh',
        'AVBL-AVAL':'inh',
        'AVBL-AVAR':'inh',
        'AVBL-AVBR':'inh',
        'AVBL-AVDR':'inh',
        'AVBR-AVAL':'inh',
        'AVBR-AVAR':'inh',
        'AVBR-AVBL':'inh',
        'AVBR-AVDL':'inh',

        'AVDL-PVCL':'exc',
        'AVDL-AVAL':'exc',
        'AVDL-AVAR':'exc',
        'AVDL-AVDR':'exc',
        'AVDR-PVCR':'exc',
        'AVDR-AVAL':'exc',
        'AVDR-AVAR':'exc',
        'AVDR-AVBL':'exc',
        'AVDR-AVDL':'exc',
    }
    conn_number_override = {
        'PVCR-AVDR_GJ':2 * 0.01,
        'AVDR-PVCR_GJ':2 * 0.01,
        'PVCL-AVAL_GJ':5 * 0.01,
        'AVAL-PVCL_GJ':5 * 0.01,
        'PVCL-AVAR_GJ':10 * 0.01,
        'AVAR-PVCL_GJ':10 * 0.01,
        'PVCR-AVAL_GJ':15 * 0.01,
        'AVAL-PVCR_GJ':15 * 0.01,
        'PVCR-AVAR_GJ':22 * 0.01,
        'AVAR-PVCR_GJ':22 * 0.01,     
        'PVDL-AVAR_GJ':4 * 0.01,
        'AVAR-PVDL_GJ':4 * 0.01,
        'PVDR-AVAL_GJ':6 * 0.01,
        'AVAL-PVDR_GJ':6 * 0.01,
    }
    parameter_set="C2WithoutMotor"
    main(cells=cells, cells_to_plot=cells_to_plot, cells_to_stimulate=cells_to_stimulate, conn_number_override=conn_number_override, conn_polarity_override=conn_polarity_override, parameter_set=parameter_set)
    """
