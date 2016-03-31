import sys
import os
from pyneuroml import pynml
import matplotlib.pyplot as plt
import numpy as np
import c302

def main(config, parameter_set, prefix, duration, dt, simulator):
    
    
    exec('from c302_%s import setup'%config)
    cells, cells_to_stimulate, params, muscles = setup(parameter_set, 
                                                       generate=True,
                                                       duration = duration, 
                                                       dt = dt,
                                                       target_directory='examples')
    
    os.chdir('examples')
    
    lems_file = 'LEMS_c302_%s_%s.xml'%(parameter_set,config)
    
    if simulator == 'jNeuroML':
        results = pynml.run_lems_with_jneuroml(lems_file, nogui=True, load_saved_data=True, verbose=True)
    elif simulator == 'jNeuroML_NEURON':
        results = pynml.run_lems_with_jneuroml_neuron(lems_file, nogui=True, load_saved_data=True, verbose=True)
    
    print("Reloaded data: %s"%results.keys())
    cells.sort()
    cells.reverse()
    
    ################################################
    ## Plot voltages cells
    
    print("Plotting neuron voltages")
    template = '%s/0/GenericCell/v'
    if parameter_set=='A' or parameter_set=='B':
        template = '%s/0/generic_iaf_cell/v'
        
    for cell in cells:
        v = results[template%cell]
        if cell==cells[0]:
            volts_n = np.array([v])
        else:
            volts_n = np.append(volts_n,[v],axis=0)
        
    info = 'Membrane potentials of %i cells'%(len(cells))
    fig, ax = plt.subplots()
    plot0 = ax.pcolor(volts_n)
    ax.set_yticks(np.arange(volts_n.shape[0]) + 0.5, minor=False)
    ax.set_yticklabels(cells)
    
    fig.colorbar(plot0)
    
    fig.canvas.set_window_title(info)
    plt.title(info)
    plt.xlabel('Time (ms)')
 
    fig.canvas.draw()
    labels = [float(item.get_text())*dt for item in ax.get_xticklabels()]

    ax.set_xticklabels(labels)
    
    ################################################
    ## Plot voltages muscles
    mneurons, all_muscles, muscle_conns = c302.get_cell_muscle_names_and_connection(test=True)
    all_muscles.remove('MANAL')
    all_muscles.remove('MVULVA')
    all_muscles.remove('MVR24')

    if muscles:

        print("Plotting muscle voltages")
        for muscle in all_muscles:
            mv = results[template%muscle]
            if muscle==all_muscles[0]:
                mvolts_n = np.array([mv])
            else:
                mvolts_n = np.append(mvolts_n,[mv],axis=0)

        info = 'Membrane potentials of %i muscles'%(len(all_muscles))
        fig, ax = plt.subplots()
        plot0 = ax.pcolor(mvolts_n)
        ax.set_yticks(np.arange(mvolts_n.shape[0]) + 0.5, minor=False)
        ax.set_yticklabels(all_muscles)

        fig.colorbar(plot0)

        fig.canvas.set_window_title(info)
        plt.title(info)
        plt.xlabel('Time (ms)')

        fig.canvas.draw()
        labels = [float(item.get_text())*dt for item in ax.get_xticklabels()]

        ax.set_xticklabels(labels)
    
    ################################################
    ## Plot activity/[Ca2+] in cells
    
    if parameter_set!='A':
        
        print("Plotting neuron activities")
        variable = 'activity'
        description = 'Activity'
        template = '%s/0/GenericCell/%s'
        if parameter_set=='A' or parameter_set=='B':
            template = '%s/0/generic_iaf_cell/%s'
        if parameter_set=='C' or parameter_set=='C1':
            variable = 'caConc'
            description = '[Ca2+]'

        info = '%s of %i cells'%(description, len(cells))
        for cell in cells:
            a = results[template%(cell,variable)]
            if cell==cells[0]:
                activities_n = np.array([a])
            else:
                activities_n = np.append(activities_n,[a],axis=0)

        fig, ax = plt.subplots()
        plot0 = ax.pcolor(activities_n)
        ax.set_yticks(np.arange(activities_n.shape[0]) + 0.5, minor=False)
        ax.set_yticklabels(cells)

        fig.colorbar(plot0)
        fig.canvas.set_window_title(info)
        plt.title(info)
        plt.xlabel('Time (ms)')

        fig.canvas.draw()
        labels = [float(item.get_text())*dt for item in ax.get_xticklabels()]

        ax.set_xticklabels(labels)
    
    ################################################
    ## Plot activity/[Ca2+] in muscles
    
    if parameter_set!='A' and muscles:
        
        print("Plotting muscle activities")
        variable = 'activity'
        description = 'Activity'
        template = '%s/0/GenericCell/%s'
        if parameter_set=='A' or parameter_set=='B':
            template = '%s/0/generic_iaf_cell/%s'
        if parameter_set=='C' or parameter_set=='C1':
            variable = 'caConc'
            description = '[Ca2+]'

        info = '%s of %i muscles'%(description, len(all_muscles))
        for m in all_muscles:
            a = results[template%(m,variable)]
            if m==all_muscles[0]:
                activities_n = np.array([a])
            else:
                activities_n = np.append(activities_n,[a],axis=0)

        fig, ax = plt.subplots()
        plot0 = ax.pcolor(activities_n)
        ax.set_yticks(np.arange(activities_n.shape[0]) + 0.5, minor=False)
        ax.set_yticklabels(all_muscles)

        fig.colorbar(plot0)
        fig.canvas.set_window_title(info)
        plt.title(info)
        plt.xlabel('Time (ms)')

        fig.canvas.draw()
        labels = [float(item.get_text())*dt for item in ax.get_xticklabels()]

        ax.set_xticklabels(labels)
    
    

    plt.show()
    
if __name__ == '__main__':


    if '-full' in sys.argv or '-muscles' in sys.argv:
        main('Full','C','',300,0.05,'jNeuroML_NEURON')
        
    if '-fullC1' in sys.argv or '-muscles' in sys.argv:
        main('Full','C1','',1000,0.05,'jNeuroML_NEURON')
        
    elif '-muscle' in sys.argv or '-muscles' in sys.argv:
        main('Muscles','C','',500,0.05,'jNeuroML_NEURON')
        
    elif '-pharA' in sys.argv or '-pharyngealA' in sys.argv:
        main('Pharyngeal','A','',500,0.05,'jNeuroML_NEURON')
        
    elif '-pharB' in sys.argv or '-pharyngealB' in sys.argv:
        main('Pharyngeal','B','',500,0.05,'jNeuroML_NEURON')
        
    elif '-pharC1' in sys.argv or '-pharyngealC1' in sys.argv:
        main('Pharyngeal','C1','',500,0.05,'jNeuroML_NEURON')
        
    elif '-phar' in sys.argv or '-pharyngeal' in sys.argv:
        main('Pharyngeal','C','',500,0.05,'jNeuroML_NEURON')
        
    elif '-socialB' in sys.argv:
        main('Social','B','',2500,0.05,'jNeuroML_NEURON')
        
    elif '-social' in sys.argv:
        main('Social','C','',2500,0.05,'jNeuroML_NEURON')
        
    elif '-oscA' in sys.argv:
        main('Oscillator','A','',600,0.05,'jNeuroML_NEURON')
        
    elif '-oscB' in sys.argv:
        main('Oscillator','B','',600,0.05,'jNeuroML_NEURON')
        
    elif '-oscC' in sys.argv:
        main('Oscillator','C','',600,0.05,'jNeuroML_NEURON')
        
        
    else:
        main('Syns','C','',500,0.05,'jNeuroML')
        