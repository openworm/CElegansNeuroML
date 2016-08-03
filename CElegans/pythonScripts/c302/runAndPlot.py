import sys
import os
from pyneuroml import pynml
import matplotlib.pyplot as plt
import numpy as np
import c302
import c302_utils

save_fig_dir = 'summary/'


def main(config, parameter_set, prefix, duration, dt, simulator, save=False, show_plot_already=True):
    
    
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
        
    c302_utils.plot_c302_results(results, config, parameter_set, directory=save_fig_dir,save=save,show_plot_already=show_plot_already)
    
    
    
if __name__ == '__main__':


    if '-full' in sys.argv or '-muscles' in sys.argv:
        main('Full','C','',300,0.05,'jNeuroML_NEURON')
        
    elif '-fullC1' in sys.argv or '-muscles' in sys.argv:
        main('Full','C1','',1000,0.05,'jNeuroML_NEURON')
        
    elif '-muscle' in sys.argv or '-muscles' in sys.argv:
        main('Muscles','C','',500,0.05,'jNeuroML_NEURON')
        
    elif '-musclesA' in sys.argv:
        main('Muscles','A','',1000,0.05,'jNeuroML_NEURON')
        
    elif '-musclesC1' in sys.argv or  '-muscC1' in sys.argv:
        main('Muscles','C1','',1000,0.05,'jNeuroML_NEURON')
        
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
        
    elif '-socialC' in sys.argv:
        main('Social','C','',2500,0.05,'jNeuroML_NEURON')
        
    elif '-socialC1' in sys.argv:
        main('Social','C1','',2500,0.05,'jNeuroML_NEURON')
        
    elif '-oscA' in sys.argv:
        main('Oscillator','A','',600,0.05,'jNeuroML_NEURON')
        
    elif '-oscB' in sys.argv:
        main('Oscillator','B','',600,0.05,'jNeuroML_NEURON')
        
    elif '-oscC' in sys.argv:
        main('Oscillator','C','',1000,0.05,'jNeuroML_NEURON')
        
    elif '-oscC1' in sys.argv:
        main('Oscillator','C1','',1000,0.05,'jNeuroML_NEURON')
        
    elif '-KatoC1' in sys.argv:
        main('Kato','C1','',1080,0.05,'jNeuroML_NEURON')

    elif '-iA' in sys.argv:
        main('IClamp','A','',1000,0.05,'jNeuroML')
    elif '-iB' in sys.argv:
        main('IClamp','B','',1000,0.05,'jNeuroML')
    elif '-iC' in sys.argv:
        main('IClamp','C','',1000,0.05,'jNeuroML')
    elif '-iC1' in sys.argv:
        main('IClamp','C1','',1000,0.05,'jNeuroML',save=True)
        
    elif '-all' in sys.argv:
        print('Generating all plots')
        html = '<table>\n'
        html2 = '<table>\n'
        
        param_sets = ['IClamp','Syns']
        #param_sets = ['IClamp']
        param_sets = ['IClamp','Syns','Pharyngeal','Social']
        param_sets = ['IClamp','Syns','Pharyngeal','Social','Oscillator','Muscles','Full']
        #param_sets = ['IClamp','Muscles']
        
        durations = {'IClamp':1000,
                     'Syns':500,
                     'Pharyngeal':500,
                     'Social':2500,
                     'Oscillator':1000,
                     'Muscles':1000,
                     'Full':1000}
            
        html+='<tr>'
        html+='<td>&nbsp;</td>'
        for p in param_sets:
            html+='<td align="center"><b><a href="https://github.com/openworm/CElegansNeuroML/blob/master/CElegans/pythonScripts/c302/c302_%s.py">%s</a></b></td>'%(p,p)

        html+='</tr>\n'
        for c in ['A','B','C','C1']:
            print('Generating for: %s'%c)
            html+='<tr>'
            html+='<td><b><a href="https://github.com/openworm/CElegansNeuroML/blob/master/CElegans/pythonScripts/c302/parameters_%s.py">Params %s</a></b></td>'%(c,c)
            for p in param_sets:
                html+='<td>'
                html+='<a href="summary_%s_%s.html"/>'%(c,p)
                html+='<img alt="?" src="neurons_%s_%s.png" height="80"/></a>'%(c,p)
                
                html+='<br/><a href="https://github.com/openworm/CElegansNeuroML/blob/master/CElegans/pythonScripts/c302/examples/c302_%s_%s.nml"/>NML</a>'%(c,p)
                html+='&nbsp;<a href="http://opensourcebrain.org/projects/celegans?explorer=https://raw.githubusercontent.com/openworm/CElegansNeuroML/master/CElegans/pythonScripts/c302/examples/c302_%s_%s.nml"/>OSB</a>'%(c,p)
                
                html2=''
                html2+='<tr><td><img alt="?" src="neurons_%s_%s.png"/></td><td><img alt="?" src="traces_neuron_%s_%s.png"/></td></tr>\n'%(c,p,p,c)
                html2+='<tr><td><img alt=" " src="neuron_activity_%s_%s.png"/></td><td><img alt=" " src="traces_neuron_activity_%s_%s.png"/></td></tr>\n'%(c,p,p,c)
                html2+='<tr><td><img alt=" " src="muscles_%s_%s.png"/></td><td><img alt=" " src="traces_muscles_%s_%s.png"/></td></tr>\n'%(c,p,p,c)
                html2+='<tr><td><img alt=" " src="muscle_activity_%s_%s.png"/></td><td><img alt=" " src="traces_muscles_activity_%s_%s.png"/></td></tr>\n'%(c,p,p,c)
                
                f2 = open('examples/'+save_fig_dir+'summary_%s_%s.html'%(c,p),'w')
                f2.write('<html><body>%s</body></html>'%html2)
                f3 = open('examples/'+save_fig_dir+'summary_%s_%s.md'%(c,p),'w')
                f3.write('### Parameter config summary \n%s'%html2)
                
                main(p,c,'',durations[p],0.05,'jNeuroML_NEURON',save=True,show_plot_already=False)
                html+='</td>'
                
            html+='</tr>\n'
        
        html+='</table>\n'
        html2+='</table>\n'
                
        f = open('examples/'+save_fig_dir+'info.html','w')
        f.write('<html><body>\n%s\n</body></html>'%html)
        f2 = open('examples/'+save_fig_dir+'README.md','w')
        f2.write('### c302 activity summary \n%s'%(html.replace('.html','.md')))
        
    else:
        main('Syns','C','',500,0.05,'jNeuroML')
        
        
    
        
