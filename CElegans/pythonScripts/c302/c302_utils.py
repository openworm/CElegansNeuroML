import sys
import os
from pyneuroml import pynml
import matplotlib.pyplot as plt
import numpy as np
import c302


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
    ax.tick_params(axis='y', labelsize=6)
    #plt.setp(ax.get_yticklabels(), rotation=45)

    
    fig.colorbar(plot0)
    
    fig.canvas.set_window_title(info)
    plt.title(info)
    plt.xlabel('Time (ms)')
 
    fig.canvas.draw()



    labels = [] #issue is with unicode
    for label in ax.get_xticklabels():
        if(len(label.get_text()) >0):
            labels.append(float( str((label.get_text())) )*dt*downscale*1000)
        # except:
        #     print "Error value on forming axis values, value: ", label.get_text(), ", length: ",len(label.get_text())
    
    #labels = [float(label.get_text())*dt*downscale*1000 for item in ax.get_xticklabels()]
    ax.set_xticklabels(labels)
    #print labels
    #print plt.xlim()
    plt.xlim(0,a_n_.shape[1])
    #print plt.xlim()
    

    
def generate_traces_plot(config,parameter_set,xvals,yvals,info,labels,save,save_fig_path,voltage,muscles):
                         
    file_name = 'traces_%s%s_%s_%s.png'%(('muscles' if muscles else 'neuron'),('' if voltage else '_activity'),config,parameter_set)
    
    pynml.generate_plot(xvals,
                        yvals,
                        info,
                        labels=labels,
                        xaxis="Time (ms)",
                        yaxis="Membrane potential (mV)" if voltage else "Activity",
                        show_plot_already=False,
                        save_figure_to=(None if not save else save_fig_path%(file_name)),
                        cols_in_legend_box=8)
    
def plot_c302_results(lems_results, config, parameter_set, directory='./',save=True,show_plot_already=True, data_reader="SpreadsheetDataReader"):
    
    params = {'legend.fontsize': 8,
              'font.size': 10}
    plt.rcParams.update(params)

    if not directory.endswith('/'):
        directory += '/'
    save_fig_path = directory+'%s'

    print("Reloaded data: %s"%lems_results.keys())
    cells = []
    muscles = False
    times = [t*1000 for t in lems_results['t']]
    for cm in lems_results.keys():
        if not cm=='t' and not cm.startswith('MD') and not cm.startswith('MV') and cm.endswith('/v'):
            cells.append(cm.split('/')[0])
        if 'MDL' in cm:
            muscles = True
    
    cells.sort()
    cells.reverse()
            
    print("All cells: %s"%cells)
    dt = lems_results['t'][1]
    
    ################################################
    ## Plot voltages cells
    
    print("Plotting neuron voltages")
    
    template = '{0}/0/GenericNeuronCell/{1}'
    template_m = '{0}/0/GenericMuscleCell/{1}'
    if parameter_set.startswith('A') or parameter_set.startswith('B'):
        template = '{0}/0/generic_neuron_iaf_cell/{1}'
        template_m = '{0}/0/generic_muscle_iaf_cell/{1}'
    if parameter_set.startswith('D'):
        template = '{0}/0/{0}/{1}'

    
    xvals = []
    yvals = []
    labels = []
    
    for cell in cells:
        v = lems_results[template.format(cell,'v')]
        
        xvals.append(times)
        labels.append(cell)
        
        if cell==cells[0]:
            volts_n = np.array([[vv*1000 for vv in v]])
        else:
            volts_n = np.append(volts_n,[[vv*1000 for vv in v]],axis=0)
        yvals.append(volts_n[-1])
        
    info = 'Membrane potentials of %i cells (%s %s)'%(len(cells),config,parameter_set)
    
    plots(volts_n, info, cells, dt)

    if save:
        f = save_fig_path%('neurons_%s_%s.png'%(parameter_set,config))
        print("Saving figure to: %s"%os.path.abspath(f))
        plt.savefig(f,bbox_inches='tight')
    
    generate_traces_plot(config,
                         parameter_set,
                         xvals,
                         yvals,
                         info,
                         labels,
                         save=save,
                         save_fig_path=save_fig_path,
                         voltage=True,
                         muscles=False)
        
    
    ################################################
    ## Plot voltages muscles
    mneurons, all_muscles, muscle_conns = c302.get_cell_muscle_names_and_connection(data_reader=data_reader, test=True)
    if ("MANAL" in all_muscles):
        all_muscles.remove('MANAL')
    if ("MVULVA" in all_muscles):
        all_muscles.remove('MVULVA')
    if ("MVR24" in all_muscles):
        all_muscles.remove('MVR24')
    all_muscles.sort()
    all_muscles.reverse()

    xvals = []
    yvals = []
    labels = []
    
    if muscles:

        print("Plotting muscle voltages")

        for muscle in all_muscles:
            mv = lems_results[template_m.format(muscle,'v')]

            xvals.append(times)
            labels.append(muscle)
        
            if muscle==all_muscles[0]:
                mvolts_n = np.array([[vv*1000 for vv in mv]])
            else:
                mvolts_n = np.append(mvolts_n,[[vv*1000 for vv in mv]],axis=0)
            yvals.append(mvolts_n[-1])

        info = 'Membrane potentials of %i muscles (%s %s)'%(len(all_muscles),config,parameter_set)

        plots(mvolts_n, info, all_muscles, dt)
        
        if save:
            f = save_fig_path%('muscles_%s_%s.png'%(parameter_set,config))
            print("Saving figure to: %s"%os.path.abspath(f))
            plt.savefig(f,bbox_inches='tight')

        generate_traces_plot(config,
                             parameter_set,
                             xvals,
                             yvals,
                             info,
                             labels,
                             save=save,
                             save_fig_path=save_fig_path,
                             voltage=True,
                             muscles=True)
    
    ################################################
    ## Plot activity/[Ca2+] in cells
    
    if parameter_set!='A':
        
        print("Plotting neuron activities")
        variable = 'activity'
        description = 'Activity'
            
        if parameter_set.startswith('C') or parameter_set.startswith('D'):
            variable = 'caConc'
            description = '[Ca2+]'

        xvals = []
        yvals = []
        labels = []

        info = '%s of %i cells (%s %s)'%(description, len(cells),config,parameter_set)
        for cell in cells:
            a = lems_results[template.format(cell,variable)]
            
            xvals.append(times)
            yvals.append(a)
            labels.append(cell)
            
            if cell==cells[0]:
                activities_n = np.array([a])
            else:
                activities_n = np.append(activities_n,[a],axis=0)

        plots(activities_n, info, cells, dt)
        
        if save:
            f = save_fig_path%('neuron_activity_%s_%s.png'%(parameter_set,config))
            print("Saving figure to: %s"%os.path.abspath(f))
            plt.savefig(f,bbox_inches='tight')
            
        generate_traces_plot(config,
                             parameter_set,
                             xvals,
                             yvals,
                             info,
                             labels,
                             save=save,
                             save_fig_path=save_fig_path,
                             voltage=False,
                             muscles=False)
    
    ################################################
    ## Plot activity/[Ca2+] in muscles
    
    if parameter_set!='A' and muscles:
        
        print("Plotting muscle activities")
        variable = 'activity'
        description = 'Activity'
            
        if parameter_set.startswith('C') or parameter_set.startswith('D'):
            variable = 'caConc'
            description = '[Ca2+]'
            
        xvals = []
        yvals = []
        labels = []

        info = '%s of %i muscles (%s %s)'%(description, len(all_muscles),config,parameter_set)
        for m in all_muscles:
            a = lems_results[template_m.format(m,variable)]
            
            xvals.append(times)
            yvals.append(a)
            labels.append(m)
            
            if m==all_muscles[0]:
                activities_n = np.array([a])
            else:
                activities_n = np.append(activities_n,[a],axis=0)

        plots(activities_n, info, all_muscles, dt)
    
        if save:
            f = save_fig_path%('muscle_activity_%s_%s.png'%(parameter_set,config))
            print("Saving figure to: %s"%os.path.abspath(f))
            plt.savefig(f,bbox_inches='tight')
    
        generate_traces_plot(config,
                             parameter_set,
                             xvals,
                             yvals,
                             info,
                             labels,
                             save=save,
                             save_fig_path=save_fig_path,
                             voltage=False,
                             muscles=True)
    
    ##os.chdir('..')

    if show_plot_already:
        plt.show()
    else:
        plt.close("all")
      
