import sys
import os
from pyneuroml import pynml
import matplotlib.pyplot as plt
import numpy as np

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
        
    volts = []
    template = '%s/0/GenericCell/v'
    if parameter_set=='A' or parameter_set=='B':
        template = '%s/0/generic_iaf_cell/v'
        
    cells.sort()
    cells.reverse()
    for cell in cells:
        v = results[template%cell]
        volts.append(v)
        
    volts_n = np.array(volts)

    fig, ax = plt.subplots()
    plot0 = ax.pcolor(volts_n)
    ax.set_yticks(np.arange(volts_n.shape[0]) + 0.5, minor=False)
    ax.set_yticklabels(cells)
    
    fig.colorbar(plot0)
    
    plt.title('Membrane potentials of %i cells'%(len(cells)))
 
    fig.canvas.draw()
    labels = [float(item.get_text())*dt for item in ax.get_xticklabels()]

    ax.set_xticklabels(labels)

    plt.show()
    
if __name__ == '__main__':


    if '-full' in sys.argv or '-muscles' in sys.argv:
        main('Full','C','',300,0.05,'jNeuroML_NEURON')
    elif '-muscle' in sys.argv or '-muscles' in sys.argv:
        main('Muscles','C','',500,0.05,'jNeuroML_NEURON')
    elif '-pharA' in sys.argv or '-pharyngealA' in sys.argv:
        main('Pharyngeal','A','',500,0.05,'jNeuroML_NEURON')
    elif '-pharB' in sys.argv or '-pharyngealB' in sys.argv:
        main('Pharyngeal','B','',500,0.05,'jNeuroML_NEURON')
    elif '-phar' in sys.argv or '-pharyngeal' in sys.argv:
        main('Pharyngeal','C','',500,0.05,'jNeuroML_NEURON')
    elif '-social' in sys.argv:
        main('Social','C','',2500,0.05,'jNeuroML_NEURON')
    else:
        main('Syns','C','',500,0.05,'jNeuroML')
        