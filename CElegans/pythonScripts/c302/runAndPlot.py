import errno
import sys
import os
from pyneuroml import pynml
import c302_utils
import c302

from collections import OrderedDict

save_fig_dir = 'summary/'


def run_c302(config, 
             parameter_set, 
             prefix, 
             duration, 
             dt, 
             simulator, 
             save=False, 
             show_plot_already=True, 
             data_reader="SpreadsheetDataReader",
             verbose=False,
             plot_ca=True,
             plot_connectivity=False,
             param_overrides={},
             config_param_overrides={},
             config_package="",
             target_directory='examples',
             save_fig_to=None):

    if save_fig_to:
        global save_fig_dir
        save_fig_dir = save_fig_to

    print("********************\n\n   Going to generate c302_%s_%s and run for %s on %s\n\n********************"%(parameter_set,config,duration, simulator))
    if config_package:
        exec ('from %s.c302_%s import setup' % (config_package, config))
    else:
        exec ('from c302_%s import setup' % config)

    try:
        os.makedirs(target_directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    cells, cells_to_stimulate, params, muscles, nml_doc = setup(parameter_set,
                                                       data_reader=data_reader,
                                                       generate=True,
                                                       duration = duration, 
                                                       dt = dt,
                                                       target_directory=target_directory,
                                                       verbose=verbose,
                                                       param_overrides=param_overrides,
                                                       config_param_overrides=config_param_overrides)

    orig_dir = os.getcwd()

    os.chdir(target_directory)

    try:
        os.makedirs(save_fig_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    lems_file = 'LEMS_c302_%s_%s.xml'%(parameter_set,config)
    
    if simulator == 'jNeuroML':
        results = pynml.run_lems_with_jneuroml(lems_file, nogui=True, load_saved_data=True, verbose=verbose)
    elif simulator == 'jNeuroML_NEURON':
        results = pynml.run_lems_with_jneuroml_neuron(lems_file, nogui=True, load_saved_data=True, verbose=verbose)
        
    c302.print_("Finished simulation of %s and have reloaded results"%lems_file)
        
    c302_utils.plot_c302_results(results, 
                                 config, 
                                 parameter_set, 
                                 directory=save_fig_dir,
                                 save=save,
                                 show_plot_already=show_plot_already, 
                                 data_reader=data_reader,
                                 plot_ca=plot_ca)

    if plot_connectivity:
        c302_utils.generate_conn_matrix(nml_doc, save_fig_dir=save_fig_dir)

    os.chdir(orig_dir)

    return cells, cells_to_stimulate, params, muscles
    
    
if __name__ == '__main__':


    if '-full' in sys.argv:
        run_c302('Full','C','',300,0.05,'jNeuroML_NEURON')
        
    elif '-fullA' in sys.argv:
        run_c302('Full','A','',1000,0.05,'jNeuroML_NEURON')
        
    elif '-fullB' in sys.argv:
        run_c302('Full','B','',1000,0.05,'jNeuroML_NEURON')
        
    elif '-fullC0' in sys.argv:
        run_c302('Full','C0','',1000,0.05,'jNeuroML_NEURON')
        
    elif '-fullC' in sys.argv:
        run_c302('Full','C','',1000,0.05,'jNeuroML_NEURON')
        
    elif '-fullC1' in sys.argv:
        run_c302('Full','C1','',1000,0.05,'jNeuroML_NEURON')

    elif '-fw' in sys.argv:
        run_c302('AVB_FW','C2','',4000,0.05,'jNeuroML_NEURON', config_package="notebooks.configs.AVB", data_reader='UpdatedSpreadsheetDataReader')

    elif '-fw1' in sys.argv:
        run_c302('FW','C2','',5000,0.005,'jNeuroML_NEURON', data_reader='UpdatedSpreadsheetDataReader', save=True, show_plot_already=False)
        
    elif '-muscle1' in sys.argv:
        run_c302('MuscleTest','C2','',2000,0.05,'jNeuroML_NEURON', data_reader='UpdatedSpreadsheetDataReader', save=True)

    elif '-head1' in sys.argv:
        run_c302('HeadMuscleTest','C2','',4000,0.05,'jNeuroML_NEURON', config_package="notebooks.configs.Head", data_reader='UpdatedSpreadsheetDataReader')

    elif '-muscle' in sys.argv or '-muscles' in sys.argv:
        run_c302('Muscles','C','',500,0.05,'jNeuroML_NEURON')
        
    elif '-musclesA' in sys.argv or  '-muscA' in sys.argv:
        run_c302('Muscles','A','',1000,0.05,'jNeuroML_NEURON')
        
    elif '-musclesB' in sys.argv or  '-muscB' in sys.argv:
        run_c302('Muscles','B','',1000,0.05,'jNeuroML_NEURON')
        
    elif '-musclesC0' in sys.argv or  '-muscC0' in sys.argv:
        run_c302('Muscles','C0','',1000,0.05,'jNeuroML_NEURON')
        
    elif '-musclesC' in sys.argv or  '-muscC' in sys.argv:
        run_c302('Muscles','C','',2000,0.05,'jNeuroML_NEURON')
        
    elif '-musclesC1' in sys.argv or  '-muscC1' in sys.argv:
        run_c302('Muscles','C1','',2000,0.05,'jNeuroML_NEURON')
        
    elif '-musclesD' in sys.argv or  '-muscD' in sys.argv:
        run_c302('Muscles','D','',2000,0.05,'jNeuroML_NEURON')
        
    elif '-musclesD1' in sys.argv or  '-muscD1' in sys.argv:
        run_c302('Muscles','D1','',2000,0.05,'jNeuroML_NEURON')
        
    elif '-pharA' in sys.argv or '-pharyngealA' in sys.argv:
        run_c302('Pharyngeal','A','',500,0.01,'jNeuroML_NEURON')
        
    elif '-pharB' in sys.argv or '-pharyngealB' in sys.argv:
        run_c302('Pharyngeal','B','',500,0.01,'jNeuroML_NEURON')
        
    elif '-pharC0' in sys.argv or '-pharyngealC0' in sys.argv:
        run_c302('Pharyngeal','C0','',500,0.01,'jNeuroML_NEURON')
        
    elif '-pharC1' in sys.argv or '-pharyngealC1' in sys.argv:
        run_c302('Pharyngeal','C1','',500,0.01,'jNeuroML_NEURON')
        
    elif '-phar' in sys.argv or '-pharyngeal' in sys.argv:
        run_c302('Pharyngeal','C','',500,0.01,'jNeuroML_NEURON')
        
    elif '-synsA' in sys.argv:
        run_c302('Syns','A','',500,0.05,'jNeuroML_NEURON')
        
    elif '-synsB' in sys.argv:
        run_c302('Syns','B','',500,0.05,'jNeuroML_NEURON')
        
    elif '-synsC0' in sys.argv:
        run_c302('Syns','C0','',500,0.05,'jNeuroML_NEURON')
        
    elif '-synsC' in sys.argv:
        run_c302('Syns','C','',500,0.05,'jNeuroML_NEURON')
        
    elif '-synsC1' in sys.argv:
        run_c302('Syns','C1','',500,0.05,'jNeuroML_NEURON')
        
    elif '-synsD' in sys.argv:
        run_c302('Syns','D','',500,0.05,'jNeuroML_NEURON')
        
    elif '-synsD1' in sys.argv:
        run_c302('Syns','D1','',500,0.05,'jNeuroML_NEURON')
        
    elif '-socialA' in sys.argv:
        run_c302('Social','A','',2500,0.05,'jNeuroML_NEURON')
        
    elif '-socialB' in sys.argv:
        run_c302('Social','B','',2500,0.05,'jNeuroML_NEURON')
        
    elif '-socialC0' in sys.argv:
        run_c302('Social','C0','',2500,0.05,'jNeuroML_NEURON')
        
    elif '-socialC' in sys.argv:
        run_c302('Social','C','',2500,0.05,'jNeuroML_NEURON')
        
    elif '-socialC1' in sys.argv:
        run_c302('Social','C1','',2500,0.05,'jNeuroML_NEURON')
        
    elif '-oscA' in sys.argv:
        run_c302('Oscillator','A','',600,0.05,'jNeuroML_NEURON')
        
    elif '-oscB' in sys.argv:
        run_c302('Oscillator','B','',600,0.05,'jNeuroML_NEURON')
        
    elif '-oscC0' in sys.argv:
        run_c302('Oscillator','C0','',2000,0.025,'jNeuroML_NEURON')
        
    elif '-test' in sys.argv:
        run_c302('Oscillator','C0','',2000,0.025,'jNeuroML_NEURON',show_plot_already=False)
        
    elif '-oscC' in sys.argv:
        run_c302('Oscillator','C','',2000,0.05,'jNeuroML_NEURON')
        
    elif '-oscC1' in sys.argv:
        run_c302('Oscillator','C1','',2000,0.05,'jNeuroML_NEURON')
        
    elif '-KatoC1' in sys.argv:
        run_c302('Kato','C1','',1080,0.05,'jNeuroML_NEURON')
        
    elif '-twC2' in sys.argv:
        run_c302('TapWithdrawal', 'C2', '', 500, 0.05, 'jNeuroML_NEURON', data_reader="UpdatedSpreadsheetDataReader")
        
    elif '-sinusC2' in sys.argv:
        run_c302('SinusoidalInputTest', 'C2', '', 1000, 0.05, 'jNeuroML_NEURON', data_reader="UpdatedSpreadsheetDataReader")
        
    elif '-iA' in sys.argv:
        run_c302('IClamp','A','',1000,0.05,'jNeuroML')
    elif '-iB' in sys.argv:
        run_c302('IClamp','B','',1000,0.05,'jNeuroML')
    elif '-iC0' in sys.argv:
        run_c302('IClamp','C0','',1000,0.05,'jNeuroML')
    elif '-iC' in sys.argv:
        run_c302('IClamp','C','',1000,0.05,'jNeuroML')
    elif '-iC1' in sys.argv:
        run_c302('IClamp','C1','',1000,0.05,'jNeuroML',save=True)
    elif '-iD' in sys.argv:
        run_c302('IClamp','D','',1000,0.05,'jNeuroML_NEURON',save=True)
    elif '-iD1' in sys.argv:
        run_c302('IClamp','D1','',1000,0.05,'jNeuroML_NEURON',save=True)
        
    elif '-all' in sys.argv:
        print('Generating all plots')
        html = '<table>\n'
        '''
        param_sets = ['IClamp','Syns']
        #param_sets = ['IClamp']
        param_sets = ['IClamp','Syns','Pharyngeal','Social']
        param_sets = ['IClamp','Syns','Pharyngeal','Social','Oscillator','Muscles','Full']
        param_sets = ['IClamp','Syns','Pharyngeal','Social','Oscillator','Muscles']'''
        #param_sets = ['IClamp','Muscles','Full']
        levels = ['A','B','C0','C','C1','C2','D','D1']
        #levels = ['D','D1']
        #levels = ['C2']

        
        durations = OrderedDict([('IClamp',1000),
                                ('Syns',500),
                                ('Pharyngeal',500),
                                ('Social',2500),
                                ('Oscillator',1000),
                                ('Muscles',1000),
                                ('Full',1000)])
        
        #durations = OrderedDict([('IClamp',1000),
        #                        ('Syns',500),
        #                        ('Oscillator',1000)])
            
        html+='<tr>'
        html+='<td>&nbsp;</td>'
        for p in durations.keys():
            html+='<td align="center"><b><a href="https://github.com/openworm/CElegansNeuroML/blob/master/CElegans/pythonScripts/c302/c302_%s.py">%s</a></b></td>'%(p,p)

        html+='</tr>\n'
        for c in levels:
            print('Generating for: %s'%c)
            
            
            html+='<tr>'
            html+='<td><b><a href="https://github.com/openworm/CElegansNeuroML/blob/master/CElegans/pythonScripts/c302/parameters_%s.py">Params %s</a></b></td>'%(c,c)
            for p in durations.keys():
                print('Params: %s'%p)
                html2 = '<table>\n'
                html+='<td>'
                html+='<a href="summary_%s_%s.html">'%(c,p)
                html+='<img alt="?" src="neurons_%s_%s.png" height="80"/></a>'%(c,p)
                
                html+='<br/><a href="https://github.com/openworm/CElegansNeuroML/blob/master/CElegans/pythonScripts/c302/examples/c302_%s_%s.nml">NML</a>'%(c,p)
                html+='&nbsp;<a href="http://opensourcebrain.org/projects/celegans?explorer=https://raw.githubusercontent.com/openworm/CElegansNeuroML/master/CElegans/pythonScripts/c302/examples/c302_%s_%s.nml">OSB</a>'%(c,p)
                
                pres = ['neurons_','neuron_activity_','muscles_','muscle_activity_']
                for pre in pres:
                    
                    html2+='\n<tr>\n  <td><a href="%s%s_%s.png"><img alt=" " src="%s%s_%s.png" height="320"/></a></td>\n'%(pre,c,p,pre,c,p)
                    if pre == 'neurons_':
                        pre = 'neuron_'
                    if pre == 'muscle_activity_':
                        pre = 'muscles_activity_'
                    html2+='  <td><a href="traces_%s%s_%s.png"><img alt=" " src="traces_%s%s_%s.png" height="320"/></a></td>\n</tr>\n'%(pre,p,c,pre,p,c)
                    
                html2+='</table>\n'
                html2+='<table>\n'
                
                html2 += '\n<tr><td><a href="c302_%s_%s_exc_to_neurons.png"><img alt=" " src="c302_%s_%s_exc_to_neurons.png" height="320"/></a></td>\n' % (c,p,c,p)
                html2 += '\n  <td><a href="c302_%s_%s_inh_to_neurons.png"><img alt=" " src="c302_%s_%s_inh_to_neurons.png" height="320"/></a></td>\n' % (c,p,c,p)
                html2 += '\n  <td><a href="c302_%s_%s_elec_neurons_neurons.png"><img alt=" " src="c302_%s_%s_elec_neurons_neurons.png" height="320"/></a></td></tr>\n' % (c,p,c,p)
                
                html2 += '\n<tr><td><a href="c302_%s_%s_exc_to_muscles.png"><img alt=" " src="c302_%s_%s_exc_to_muscles.png" height="320"/></a></td>\n' % (c,p,c,p)
                html2 += '\n  <td><a href="c302_%s_%s_inh_to_muscles.png"><img alt=" " src="c302_%s_%s_inh_to_muscles.png" height="320"/></a></td>' % (c,p,c,p)
                if os.path.isfile('%s/%s/c302_%s_%s_elec_neurons_muscles.png' % ('examples', save_fig_dir, c, p)):
                    html2 += '\n\n  <td><a href="c302_%s_%s_elec_neurons_muscles.png"><img alt=" " src="c302_%s_%s_elec_neurons_muscles.png" height="320"/></a></td>' % (c, p, c, p)
                html2 += '</tr>\n'

                if os.path.isfile('%s/%s/c302_%s_%s_elec_muscles_muscles.png' % ('examples', save_fig_dir, c, p)):
                    html2 += '\n<tr><td><a href="c302_%s_%s_elec_muscles_muscles.png"><img alt=" " src="c302_%s_%s_elec_muscles_muscles.png" height="320"/></a></td></tr>\n' % (c, p, c, p)

                    
                html2+='</table>\n'
                
                with open('examples/'+save_fig_dir+'summary_%s_%s.html'%(c,p),'w') as f2:
                    f2.write('<html><body>%s</body></html>'%html2)
                with open('examples/'+save_fig_dir+'summary_%s_%s.md'%(c,p),'w') as f3:
                    f3.write('### Parameter config summary \n%s'%html2)

                run_c302(p,
                         c,
                         '',
                         durations[p],
                         0.05,
                         'jNeuroML_NEURON',
                         save=True,
                         show_plot_already=False,
                         plot_connectivity=True,
                         data_reader='SpreadsheetDataReader')
                
                html+='</td>'
                
            html+='</tr>\n'
        
        html+='</table>\n'
                
        with open('examples/'+save_fig_dir+'info.html','w') as f:
            f.write('<html><body>\n%s\n</body></html>'%html)
        with open('examples/'+save_fig_dir+'README.md','w') as f2:
            f2.write('### c302 activity summary \n%s'%(html.replace('.html','.md')))
        
    else:
        run_c302('Syns','C','',500,0.05,'jNeuroML')
        
        
    
        
