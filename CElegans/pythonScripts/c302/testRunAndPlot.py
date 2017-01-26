import sys
import os
from pyneuroml import pynml
import c302_utils
import shutil

from collections import OrderedDict

def print_msg(msg):
    print "testRunAndPlot\t\t>>>\t%s" % msg

def main(cells=[], cells_to_stimulate=[], parameter_set="C2", duration=500, dt=0.05, simulator="jNeuroML_NEURON", save=True, show_plot_already=False, data_reader="UpdatedSpreadsheetDataReader"):
    
    #exec('from c302_%s import setup'%config)
    """cells, cells_to_stimulate, params, muscles = setup(parameter_set, 
                                                       data_reader=data_reader,
                                                       generate=True,
                                                       duration = duration, 
                                                       dt = dt,
                                                       target_directory='examples')"""

    parent_dir = "test"
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)
        print_msg("Created dir %s" % parent_dir)
    #os.chdir(parent_dir)

    config = "_".join(cells) + "__stim_" + "_".join(cells_to_stimulate)

    save_dir = os.path.join(parent_dir, config)
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
    cells_to_stimulate_str = "['" + "','".join(cells_to_stimulate) + "']"
    filename = "%s_%s" % (parameter_set, config)
    command = 'python c302.py %s parameters_%s -cells %s -cellstostimulate %s -duration %s -datareader %s -dt %s' \
              % (filename, parameter_set, cells_str, cells_to_stimulate_str, duration, data_reader, dt)

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
    
    #PLM-PVC, stim PLM
    main(cells=["PLML", "PVCL"], cells_to_stimulate=["PLML"])
    main(cells=["PLML", "PVCR"], cells_to_stimulate=["PLML"])
    main(cells=["PLMR", "PVCL"], cells_to_stimulate=["PLMR"])
    main(cells=["PLMR", "PVCR"], cells_to_stimulate=["PLMR"])
    main(cells=["PLML", "PLMR", "PVCL"], cells_to_stimulate=["PLML", "PLMR"])
    main(cells=["PLML", "PLMR", "PVCR"], cells_to_stimulate=["PLML", "PLMR"])
    main(cells=["PLML", "PLMR", "PVCL", "PVCR"], cells_to_stimulate=["PLML"])
    main(cells=["PLML", "PLMR", "PVCL", "PVCR"], cells_to_stimulate=["PLMR"])
    main(cells=["PLML", "PLMR", "PVCL", "PVCR"], cells_to_stimulate=["PLML", "PLMR"])

    # PLM-AVD, stim PLM
    main(cells=["PLML", "AVDL"], cells_to_stimulate=["PLML"])
    main(cells=["PLML", "AVDR"], cells_to_stimulate=["PLML"])
    main(cells=["PLMR", "AVDL"], cells_to_stimulate=["PLMR"])
    main(cells=["PLMR", "AVDR"], cells_to_stimulate=["PLMR"])
    main(cells=["PLML", "PLMR", "AVDL"], cells_to_stimulate=["PLML", "PLMR"])
    main(cells=["PLML", "PLMR", "AVDR"], cells_to_stimulate=["PLML", "PLMR"])
    main(cells=["PLML", "PLMR", "AVDL", "AVDR"], cells_to_stimulate=["PLML"])
    main(cells=["PLML", "PLMR", "AVDL", "AVDR"], cells_to_stimulate=["PLMR"])
    main(cells=["PLML", "PLMR", "AVDL", "AVDR"], cells_to_stimulate=["PLML", "PLMR"])
    

    # PVC-AVA, stim PVC
    main(cells=["PVCL", "AVAL"], cells_to_stimulate=["PVCL"])
    main(cells=["PVCL", "AVAR"], cells_to_stimulate=["PVCL"])
    main(cells=["PVCR", "AVAL"], cells_to_stimulate=["PVCR"])
    main(cells=["PVCR", "AVAR"], cells_to_stimulate=["PVCR"])
    main(cells=["PVCL", "PVCR", "AVAL"], cells_to_stimulate=["PVCL", "PVCR"])
    main(cells=["PVCL", "PVCR", "AVAR"], cells_to_stimulate=["PVCL", "PVCR"])
    main(cells=["PVCL", "PVCR", "AVAL", "AVAR"], cells_to_stimulate=["PVCL"])
    main(cells=["PVCL", "PVCR", "AVAL", "AVAR"], cells_to_stimulate=["PVCR"])
    main(cells=["PVCL", "PVCR", "AVAL", "AVAR"], cells_to_stimulate=["PVCL", "PVCR"])
    
    # PVC-AVB, stim PVC
    main(cells=["PVCL", "AVBL"], cells_to_stimulate=["PVCL"])
    main(cells=["PVCL", "AVBR"], cells_to_stimulate=["PVCL"])
    main(cells=["PVCR", "AVBL"], cells_to_stimulate=["PVCR"])
    main(cells=["PVCR", "AVBR"], cells_to_stimulate=["PVCR"])
    main(cells=["PVCL", "PVCR", "AVBL"], cells_to_stimulate=["PVCL", "PVCR"])
    main(cells=["PVCL", "PVCR", "AVBR"], cells_to_stimulate=["PVCL", "PVCR"])
    main(cells=["PVCL", "PVCR", "AVBL", "AVBR"], cells_to_stimulate=["PVCL"])
    main(cells=["PVCL", "PVCR", "AVBL", "AVBR"], cells_to_stimulate=["PVCR"])
    main(cells=["PVCL", "PVCR", "AVBL", "AVBR"], cells_to_stimulate=["PVCL", "PVCR"])

    # PVC-AVA-AVB, stim PVC
    main(cells=["PVCL", "PVCR", "AVAL", "AVAR", "AVBL", "AVBR"], cells_to_stimulate=["PVCL"])
    main(cells=["PVCL", "PVCR", "AVAL", "AVAR", "AVBL", "AVBR"], cells_to_stimulate=["PVCR"])
    main(cells=["PVCL", "PVCR", "AVAL", "AVAR", "AVBL", "AVBR"], cells_to_stimulate=["PVCL", "PVCR"])

    # AVD-AVA, stim AVD
    main(cells=["AVDL", "AVAL"], cells_to_stimulate=["AVDL"])
    main(cells=["AVDL", "AVAR"], cells_to_stimulate=["AVDL"])
    main(cells=["AVDR", "AVAL"], cells_to_stimulate=["AVDR"])
    main(cells=["AVDR", "AVAR"], cells_to_stimulate=["AVDR"])
    main(cells=["AVDL", "AVDR", "AVAL"], cells_to_stimulate=["AVDL", "AVDR"])
    main(cells=["AVDL", "AVDR", "AVAR"], cells_to_stimulate=["AVDL", "AVDR"])
    main(cells=["AVDL", "AVDR", "AVAL", "AVAR"], cells_to_stimulate=["AVDL", "AVDR"])

    # AVD-AVB, stim AVD
    main(cells=["AVDL", "AVBL"], cells_to_stimulate=["AVDL"])
    main(cells=["AVDL", "AVBR"], cells_to_stimulate=["AVDL"])
    main(cells=["AVDR", "AVBL"], cells_to_stimulate=["AVDR"])
    main(cells=["AVDR", "AVBR"], cells_to_stimulate=["AVDR"])
    main(cells=["AVDL", "AVDR", "AVBL"], cells_to_stimulate=["AVDL", "AVDR"])
    main(cells=["AVDL", "AVDR", "AVBR"], cells_to_stimulate=["AVDL", "AVDR"])
    main(cells=["AVDL", "AVDR", "AVBL", "AVBR"], cells_to_stimulate=["AVDL", "AVDR"])

    # AVD-AVA-AVB, stim AVD
    main(cells=["AVDL", "AVDR", "AVAL", "AVAR", "AVBL", "AVBR"], cells_to_stimulate=["AVDL"])
    main(cells=["AVDL", "AVDR", "AVAL", "AVAR", "AVBL", "AVBR"], cells_to_stimulate=["AVDR"])
    main(cells=["AVDL", "AVDR", "AVAL", "AVAR", "AVBL", "AVBR"], cells_to_stimulate=["AVDL", "AVDR"])
    
    # PVC-AVD-AVA-AVB, stim PVC
    main(cells=["PVCL", "PVCR", "AVDL", "AVDR", "AVAL", "AVAR", "AVBL", "AVBR"], cells_to_stimulate=["PVCL", "PVCR"])
    # PVC-AVD-AVA-AVB, stim AVD
    main(cells=["PVCL", "PVCR", "AVDL", "AVDR", "AVAL", "AVAR", "AVBL", "AVBR"], cells_to_stimulate=["AVDL", "AVDR"])
    # PVC-AVD-AVA-AVB, stim PVC & AVD
    main(cells=["PVCL", "PVCR", "AVDL", "AVDR", "AVAL", "AVAR", "AVBL", "AVBR"], cells_to_stimulate=["PVCL", "PVCR", "AVDL", "AVDR"])    
    
    # AVA(L,R) - VA(1-12)
    for i in range_incl(1, 12):
        main(cells = ["AVAL", "VA%s" % i], cells_to_stimulate = ["AVAL"])
    for i in range_incl(1, 12):
        main(cells = ["AVAR", "VA%s" % i], cells_to_stimulate = ["AVAR"])
        
    # AVA(L,R) - DA(1-9)
    for i in range_incl(1, 9):
        main(cells = ["AVAL","DA%s"%i], cells_to_stimulate = ["AVAL"])
    for i in range_incl(1, 9):
        main(cells = ["AVAR","DA%s"%i], cells_to_stimulate = ["AVAR"])
        
    # AVA(L,R) - VB(1-11)
    for i in range_incl(1, 11):
        main(cells=["AVAL", "VB%s" % i], cells_to_stimulate=["AVAL"])
    for i in range_incl(1, 11):
        main(cells=["AVAR", "VB%s" % i], cells_to_stimulate=["AVAR"])

    # AVA(L,R) - DB(1-7)
    for i in range_incl(1, 7):
        main(cells=["AVAL", "DB%s" % i], cells_to_stimulate=["AVAL"])
    for i in range_incl(1, 7):
        main(cells=["AVAR", "DB%s" % i], cells_to_stimulate=["AVAR"])

    # AVB(L,R) - VA(1-12)
    for i in range_incl(1, 12):
        main(cells=["AVBL", "VA%s" % i], cells_to_stimulate=["AVBL"])
    for i in range_incl(1, 12):
        main(cells=["AVBR", "VA%s" % i], cells_to_stimulate=["AVBR"])

    # AVB(L,R) - DA(1-9)
    for i in range_incl(1, 9):
        main(cells=["AVBL", "DA%s" % i], cells_to_stimulate=["AVBL"])
    for i in range_incl(1, 9):
        main(cells=["AVBR", "DA%s" % i], cells_to_stimulate=["AVBR"])

    # AVB(L,R) - VB(1-11)
    for i in range_incl(1, 11):
        main(cells=["AVBL", "VB%s" % i], cells_to_stimulate=["AVBL"])
    for i in range_incl(1, 11):
        main(cells=["AVBR", "VB%s" % i], cells_to_stimulate=["AVBR"])

    # AVB(L,R) - DB(1-7)
    for i in range_incl(1, 7):
        main(cells=["AVBL", "DB%s" % i], cells_to_stimulate=["AVBL"])
    for i in range_incl(1, 7):
        main(cells=["AVBR", "DB%s" % i], cells_to_stimulate=["AVBR"])

    # AVA - VA(1-12)
    for i in range_incl(1, 12):
        main(cells=["AVAL", "AVAR", "VA%s" % i], cells_to_stimulate=["AVAL", "AVAR"])

    # AVA - DA(1-9)
    for i in range_incl(1, 9):
        main(cells=["AVAL", "AVAR", "DA%s" % i], cells_to_stimulate=["AVAL", "AVAR"])

    # AVA - VB(1-11)
    for i in range_incl(1, 11):
        main(cells=["AVAL", "AVAR", "VB%s" % i], cells_to_stimulate=["AVAL", "AVAR"])

    # AVA - DB(1-7)
    for i in range_incl(1, 7):
        main(cells=["AVAL", "AVAR", "DB%s" % i], cells_to_stimulate=["AVAL", "AVAR"])

    # AVB - VA(1-12)
    for i in range_incl(1, 12):
        main(cells=["AVBL", "AVBR", "VA%s" % i], cells_to_stimulate=["AVBL", "AVBR"])

    # AVB - DA(1-9)
    for i in range_incl(1, 9):
        main(cells=["AVBL", "AVBR", "DA%s" % i], cells_to_stimulate=["AVBL", "AVBR"])

    # AVB - VB(1-11)
    for i in range_incl(1, 11):
        main(cells=["AVBL", "AVBR", "VB%s" % i], cells_to_stimulate=["AVBL", "AVBR"])

    # AVB - DB(1-7)
    for i in range_incl(1, 7):
        main(cells=["AVBL", "AVBR", "DB%s" % i], cells_to_stimulate=["AVBL", "AVBR"])

    # AVA-AVB-VA(1-12), stim AVB
    for i in range_incl(1, 12):
        main(cells=["AVAL", "AVAR", "AVBL", "AVBR", "VA%s" % i], cells_to_stimulate=["AVBL", "AVBR"])

    # AVA-AVB-DA(1-9), stim AVB
    for i in range_incl(1, 9):
        main(cells=["AVAL", "AVAR", "AVBL", "AVBR", "DA%s" % i], cells_to_stimulate=["AVBL", "AVBR"])

    # AVA-AVB-VB(1-11), stim AVB
    for i in range_incl(1, 11):
        main(cells=["AVAL", "AVAR", "AVBL", "AVBR", "VB%s" % i], cells_to_stimulate=["AVBL", "AVBR"])

    # AVA-AVB-DB(1-7), stim AVB
    for i in range_incl(1, 7):
        main(cells=["AVAL", "AVAR", "AVBL", "AVBR", "DB%s" % i], cells_to_stimulate=["AVBL", "AVBR"])

    # AVA-AVB-VA(1-12), stim AVA
    for i in range_incl(1, 12):
        main(cells=["AVAL", "AVAR", "AVBL", "AVBR", "VA%s" % i], cells_to_stimulate=["AVAL", "AVAR"])

    # AVA-AVB-DA(1-9), stim AVA
    for i in range_incl(1, 9):
        main(cells=["AVAL", "AVAR", "AVBL", "AVBR", "DA%s" % i], cells_to_stimulate=["AVAL", "AVAR"])

    # AVA-AVB-VB(1-11), stim AVA
    for i in range_incl(1, 11):
        main(cells=["AVAL", "AVAR", "AVBL", "AVBR", "VB%s" % i], cells_to_stimulate=["AVAL", "AVAR"])

    # AVA-AVB-DB(1-7), stim AVA
    for i in range_incl(1, 7):
        main(cells=["AVAL", "AVAR", "AVBL", "AVBR", "DB%s" % i], cells_to_stimulate=["AVAL", "AVAR"])

    main(cells=["AVAL", "AVAR"]+VA_cells+VB_cells, cells_to_stimulate=["AVAL", "AVAR"])
    main(cells=["AVAL", "AVAR"]+DA_cells+DB_cells, cells_to_stimulate=["AVAL", "AVAR"])
    main(cells=["AVBL", "AVBR"]+VA_cells+VB_cells, cells_to_stimulate=["AVBL", "AVBR"])
    main(cells=["AVBL", "AVBR"]+DA_cells+DB_cells, cells_to_stimulate=["AVBL", "AVBR"])

    main(cells=["AVAL", "AVAR", "AVBL", "AVBR"]+VA_cells+VB_cells, cells_to_stimulate=["AVAL", "AVAR"])
    main(cells=["AVAL", "AVAR", "AVBL", "AVBR"]+DA_cells+DB_cells, cells_to_stimulate=["AVAL", "AVAR"])
    main(cells=["AVAL", "AVAR", "AVBL", "AVBR"]+VA_cells+VB_cells, cells_to_stimulate=["AVBL", "AVBR"])
    main(cells=["AVAL", "AVAR", "AVBL", "AVBR"]+DA_cells+DB_cells, cells_to_stimulate=["AVBL", "AVBR"])

    main(cells=["AVAL", "AVAR", "AVBL", "AVBR"]+DA_cells+DB_cells+DD_cells, cells_to_stimulate=["AVAL", "AVAR"])
    main(cells=["AVAL", "AVAR", "AVBL", "AVBR"]+DA_cells+DB_cells+DD_cells, cells_to_stimulate=["AVBL", "AVBR"])

    # VA(1-12) - VB(1-11) stim VA
    for i in range_incl(1, 12):
        for j in range_incl(1,11):
            main(cells=["VA%s" % i, "VB%s" % j], cells_to_stimulate=["VA%s" % i])

    # VA(1-12) - VB(1-11) stim VB
    for i in range_incl(1, 12):
        for j in range_incl(1, 11):
            main(cells=["VA%s" % i, "VB%s" % j], cells_to_stimulate=["VB%s" % j])

    # VA(1-12) - VB(1-11) stim VA and VB
    for i in range_incl(1, 12):
        for j in range_incl(1, 11):
            main(cells=["VA%s" % i, "VB%s" % j], cells_to_stimulate=["VA%s" % i, "VB%s" % j])

    
    # DD(1-6)-VA(1-12) stim DD
    for i in range_incl(1, 6):
        for j in range_incl(1, 12):
            main(cells=["DD%s" % i, "VA%s" % j], cells_to_stimulate=["DD%s" % i])
    # DD(1-6)-VB(1-11) stim DD
    for i in range_incl(1, 6):
        for j in range_incl(1, 11):
            main(cells=["DD%s" % i, "VA%s" % j], cells_to_stimulate=["DD%s" % i])
    # DD(1-6)-DA(1-9) stim DD
    for i in range_incl(1, 6):
        for j in range_incl(1, 9):
            main(cells=["DD%s" % i, "VA%s" % j], cells_to_stimulate=["DD%s" % i])
    # DD(1-6)-DB(1-12) stim DD
    for i in range_incl(1, 6):
        for j in range_incl(1, 6):
            main(cells=["DD%s" % i, "DB%s" % j], cells_to_stimulate=["DD%s" % i])

    main(cells=DD_cells+VA_cells, cells_to_stimulate=DD_cells)
    main(cells=DD_cells+VB_cells, cells_to_stimulate=DD_cells)
    main(cells=DD_cells+DA_cells, cells_to_stimulate=DD_cells)
    main(cells=DD_cells+DB_cells, cells_to_stimulate=DD_cells)
    

