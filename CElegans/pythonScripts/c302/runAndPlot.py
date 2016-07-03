import sys
import os
from pyneuroml import pynml
import matplotlib.pyplot as plt
import numpy as np
import c302

save_fig_path = 'summary/%s'

def plots(a_n, info, cells, dt):
    print('Generating plots for: %s'%info)
    
    fig, ax = plt.subplots()
    downscale = 10
    #print a_n.shape
    a_n_ = a_n[:,::downscale]
    #print(a_n_.shape) 
    
    plot0 = ax.pcolor(a_n_)
    ax.set_yticks(np.arange(a_n_.shape[0]) + 0.5, minor=False)
    ax.set_yticklabels(cells)
    
    fig.colorbar(plot0)
    
    fig.canvas.set_window_title(info)
    plt.title(info)
    plt.xlabel('Time (ms)')
 
    fig.canvas.draw()
    labels = [float(item.get_text())*dt*downscale for item in ax.get_xticklabels()]

    ax.set_xticklabels(labels)
    #print labels
    #print plt.xlim()
    plt.xlim(0,a_n_.shape[1])
    #print plt.xlim()
    

def main(config, parameter_set, prefix, duration, dt, simulator, save_only=False):
    
    
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
        
    info = 'Membrane potentials of %i cells (%s %s)'%(len(cells),config,parameter_set)
    
    plots(volts_n, info, cells, dt)

    if save_only:
        plt.savefig(save_fig_path%('neurons_%s_%s.png'%(parameter_set,config)),bbox_inches='tight')
    
    ################################################
    ## Plot voltages muscles
    mneurons, all_muscles, muscle_conns = c302.get_cell_muscle_names_and_connection(test=True)
    all_muscles.remove('MANAL')
    all_muscles.remove('MVULVA')
    all_muscles.remove('MVR24')
    all_muscles.sort()
    all_muscles.reverse()

    if muscles:

        print("Plotting muscle voltages")
        for muscle in all_muscles:
            mv = results[template%muscle]
            if muscle==all_muscles[0]:
                mvolts_n = np.array([mv])
            else:
                mvolts_n = np.append(mvolts_n,[mv],axis=0)

        info = 'Membrane potentials of %i muscles (%s %s)'%(len(all_muscles),config,parameter_set)

        plots(mvolts_n, info, cells, dt)
        
        if save_only:
            plt.savefig(save_fig_path%('muscles_%s_%s.png'%(parameter_set,config)),bbox_inches='tight')
    
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

        info = '%s of %i cells (%s %s)'%(description, len(cells),config,parameter_set)
        for cell in cells:
            a = results[template%(cell,variable)]
            if cell==cells[0]:
                activities_n = np.array([a])
            else:
                activities_n = np.append(activities_n,[a],axis=0)

        plots(activities_n, info, cells, dt)
        
        if save_only:
            plt.savefig(save_fig_path%('neuron_activity_%s_%s.png'%(parameter_set,config)),bbox_inches='tight')
    
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

        info = '%s of %i muscles (%s %s)'%(description, len(all_muscles),config,parameter_set)
        for m in all_muscles:
            a = results[template%(m,variable)]
            if m==all_muscles[0]:
                activities_n = np.array([a])
            else:
                activities_n = np.append(activities_n,[a],axis=0)

        plots(activities_n, info, cells, dt)
    
        if save_only:
            plt.savefig(save_fig_path%('muscle_activity_%s_%s.png'%(parameter_set,config)),bbox_inches='tight')
    
    
    os.chdir('..')

    if not save_only:
        plt.show()
    
if __name__ == '__main__':


    if '-full' in sys.argv or '-muscles' in sys.argv:
        main('Full','C','',300,0.05,'jNeuroML_NEURON')
        
    if '-fullC1' in sys.argv or '-muscles' in sys.argv:
        main('Full','C1','',1000,0.05,'jNeuroML_NEURON')
        
    elif '-muscle' in sys.argv or '-muscles' in sys.argv:
        main('Muscles','C','',500,0.05,'jNeuroML_NEURON')
        
    elif '-musclesA' in sys.argv:
        main('Muscles','A','',1000,0.05,'jNeuroML_NEURON')
        
    elif '-musclesC1' in sys.argv:
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
        
    elif '-social' in sys.argv:
        main('Social','C','',2500,0.05,'jNeuroML_NEURON')
        
    elif '-oscA' in sys.argv:
        main('Oscillator','A','',600,0.05,'jNeuroML_NEURON')
        
    elif '-oscB' in sys.argv:
        main('Oscillator','B','',600,0.05,'jNeuroML_NEURON')
        
    elif '-oscC' in sys.argv:
        main('Oscillator','C','',600,0.05,'jNeuroML_NEURON')
        
    elif '-oscC1' in sys.argv:
        main('Oscillator','C1','',600,0.05,'jNeuroML_NEURON')
        
    elif '-KatoC1' in sys.argv:
        main('Kato','C1','',1080,0.05,'jNeuroML_NEURON')

    elif '-iA' in sys.argv:
        main('IClamp','A','',1000,0.05,'jNeuroML')
    elif '-iB' in sys.argv:
        main('IClamp','B','',1000,0.05,'jNeuroML')
    elif '-iC' in sys.argv:
        main('IClamp','C','',1000,0.05,'jNeuroML')
    elif '-iC1' in sys.argv:
        main('IClamp','C1','',1000,0.05,'jNeuroML')
        
    elif '-all' in sys.argv:
        
        html = '<table>\n'
        
        param_sets = ['IClamp','Syns']
        param_sets = ['IClamp']
        param_sets = ['IClamp','Syns','Pharyngeal','Social']
        param_sets = ['IClamp','Syns','Pharyngeal','Social','Oscillator','Muscles','Full']
        
        durations = {'IClamp':1000,
                     'Syns':500,
                     'Pharyngeal':500,
                     'Social':2500,
                     'Oscillator':600,
                     'Muscles':500,
                     'Full':500}
            
        html+='<tr>'
        html+='<td>&nbsp;</td>'
        for p in param_sets:
            html+='<td align="center"><b><a href="https://github.com/openworm/CElegansNeuroML/blob/master/CElegans/pythonScripts/c302/c302_%s.py">%s</a></b></td>'%(p,p)

        html+='</tr>\n'
        for c in ['A','B','C','C1']:
            
            
            html+='<tr>'
            html+='<td><b><a href="https://github.com/openworm/CElegansNeuroML/blob/master/CElegans/pythonScripts/c302/parameters_%s.py">Params %s</a></b></td>'%(c,c)
            for p in param_sets:
                html+='<td>'
                html+='<a href="summary_%s_%s.html"/>'%(c,p)
                html+='<img alt="?" src="neurons_%s_%s.png" height="80"/></a>'%(c,p)
                
                html+='<br/><a href="https://github.com/openworm/CElegansNeuroML/blob/master/CElegans/pythonScripts/c302/examples/c302_%s_%s.nml"/>NML</a>'%(c,p)
                html+='&nbsp;<a href="http://opensourcebrain.org/projects/celegans?explorer=https://raw.githubusercontent.com/openworm/CElegansNeuroML/master/CElegans/pythonScripts/c302/examples/c302_%s_%s.nml"/>OSB</a>'%(c,p)
                
                html2=''
                html2+='<p><img alt="?" src="neurons_%s_%s.png"/></p>\n'%(c,p)
                html2+='<p><img alt=" " src="neuron_activity_%s_%s.png"/></p>\n'%(c,p)
                html2+='<p><img alt=" " src="muscles_%s_%s.png"/></p>\n'%(c,p)
                html2+='<p><img alt=" " src="muscle_activity_%s_%s.png"/></p>\n'%(c,p)
                
                f2 = open('examples/'+save_fig_path%('summary_%s_%s.html'%(c,p)),'w')
                f2.write('<html><body>%s</body></html>'%html2)
                f3 = open('examples/'+save_fig_path%('summary_%s_%s.md'%(c,p)),'w')
                f3.write('### Parameter config summary \n%s'%html2)
                
                #main(p,c,'',durations[p],0.05,'jNeuroML_NEURON',save_only=True)
                html+='</td>'
                
            html+='</tr>\n'
        
        html+='</table>\n'
                
        f = open('examples/'+save_fig_path%'info.html','w')
        f.write('<html><body>\n%s\n</body></html>'%html)
        f2 = open('examples/'+save_fig_path%'README.md','w')
        f2.write('### c302 activity summary \n%s'%(html.replace('.html','.md')))
        
    else:
        main('Syns','C','',500,0.05,'jNeuroML')
        
        
    
        
