import sys
import os
from pyneuroml import pynml
import matplotlib.pyplot as plt
import numpy as np
from c302 import c302
import re
import multiprocessing
import time
import cProfile

natsort = lambda s: [int(t) if t.isdigit() else t for t in re.split('(\d+)', s)]


def plots(a_n, info, cells, dt, heightened=False):
    
    #import cProfile, pstats, StringIO
    #pr = cProfile.Profile()
    #pr.enable()
    
   
    #import time
    #start = time.time()

    c302.print_('Generating plots for: %s'%info)

    if heightened:
        #fontsize_pt = plt.rcParams['ytick.labelsize']
        #dpi = 72.27

        # comput the matrix height in points and inches
        ##matrix_height_pt = fontsize_pt * a_n.shape[0]
        ##matrix_height_in = float(matrix_height_pt) / dpi
        matrix_height_in = 10

        # compute the required figure height
        top_margin = 0.04  # in percentage of the figure height
        bottom_margin = 0.04  # in percentage of the figure height
        figure_height = matrix_height_in / (1 - top_margin - bottom_margin)

        fig, ax = plt.subplots(
            figsize=(6, figure_height),
            gridspec_kw=dict(top=1 - top_margin, bottom=bottom_margin))
    else:
        fig, ax = plt.subplots()

    #fig = plt.figure()
    #ax = fig.gca()
    downscale = 10
    #print a_n.shape
    a_n_ = a_n[:,::downscale]
    #c302.print_(a_n_.shape) 

    plot0 = ax.pcolormesh(a_n_)
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

    #print "TIME: %s" % (time.time() - start)

    #pr.disable()
    #s = StringIO.StringIO()
    #sortby = 'cumulative'
    #ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    #ps.print_stats()
    #print s.getvalue()
    
def plots_prof(a_n, info, cells, dt):
    cProfile.run('real_plots(a_n, info, cells, dt)')
    
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
                        cols_in_legend_box=8,
                        title_above_plot=True)
    
    
def plot_c302_results(lems_results, 
                      config, 
                      parameter_set, 
                      directory='./',
                      save=True,
                      show_plot_already=True, 
                      data_reader="SpreadsheetDataReader",
                      plot_ca=True):
    
    #pool = multiprocessing.Pool(2)
    #tasks = []
    #gen_traces_tasks = []
    
    params = {'legend.fontsize': 8,
              'font.size': 10}
    plt.rcParams.update(params)

    if not directory.endswith('/'):
        directory += '/'
    save_fig_path = directory+'%s'

    c302.print_("Reloaded data: %s"%lems_results.keys())
    cells = []
    muscles = []
    times = [t*1000 for t in lems_results['t']]
    for cm in lems_results.keys():
        if not cm=='t' and cm.endswith('/v'):
            if c302.is_muscle(cm):
                muscles.append(cm.split('/')[0])
            else:
                cells.append(cm.split('/')[0])
    
    cells.sort(key=natsort)
    cells.reverse()
            
    c302.print_("All cells: %s"%cells)
    dt = lems_results['t'][1]
    
    ################################################
    ## Plot voltages cells
    
    if len(cells) > 0:
        c302.print_("Plotting neuron voltages")
        
        template = '{0}/0/GenericNeuronCell/{1}'
        if parameter_set.startswith('A') or parameter_set.startswith('B'):
            template = '{0}/0/generic_neuron_iaf_cell/{1}'
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
            
        info = 'Membrane potentials of %i neuron(s) (%s %s)'%(len(cells),config,parameter_set)

        #tasks.append((volts_n, info, cells, dt))
        if len(cells) > 24:
            plots(volts_n, info, cells, dt, heightened=True)
        else:
            plots(volts_n, info, cells, dt, heightened=False)

        if save:
            f = save_fig_path%('neurons_%s_%s.png'%(parameter_set,config))
            c302.print_("Saving figure to: %s"%os.path.abspath(f))
            plt.savefig(f,bbox_inches='tight')

        #gen_traces_tasks.append( (config, parameter_set, xvals, yvals, info, labels, save, save_fig_path, True, False) )
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

 
    muscles.sort(key=natsort)
    muscles.reverse()

    xvals = []
    yvals = []
    labels = []
    
    if len(muscles)>0:

        c302.print_("Plotting muscle voltages")

        template_m = '{0}/0/GenericMuscleCell/{1}'
        if parameter_set.startswith('A') or parameter_set.startswith('B'):
            template_m = '{0}/0/generic_muscle_iaf_cell/{1}'

        for muscle in muscles:
            mv = lems_results[template_m.format(muscle,'v')]

            xvals.append(times)
            labels.append(muscle)
        
            if muscle==muscles[0]:
                mvolts_n = np.array([[vv*1000 for vv in mv]])
            else:
                mvolts_n = np.append(mvolts_n,[[vv*1000 for vv in mv]],axis=0)
            yvals.append(mvolts_n[-1])

        info = 'Membrane potentials of %i muscle(s) (%s %s)'%(len(muscles),config,parameter_set)

        #tasks.append((mvolts_n, info, muscles, dt))
        if len(muscles) > 24:
            plots(mvolts_n, info, muscles, dt, heightened=True)
        else:
            plots(mvolts_n, info, muscles, dt, heightened=False)
        
        if save:
            f = save_fig_path%('muscles_%s_%s.png'%(parameter_set,config))
            c302.print_("Saving figure to: %s"%os.path.abspath(f))
            plt.savefig(f,bbox_inches='tight')

        #gen_traces_tasks.append((config, parameter_set, xvals, yvals, info, labels, save, save_fig_path, True, True))
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
    
    if plot_ca and parameter_set!='A' and len(cells) > 0:
        
        c302.print_("Plotting neuron activities ([Ca2+])")
        variable = 'activity'
        description = 'Activity'
            
        if parameter_set.startswith('C') or parameter_set.startswith('D'):
            variable = 'caConc'
            description = '[Ca2+]'

        xvals = []
        yvals = []
        labels = []

        info = '%s of %i neurons (%s %s)'%(description, len(cells),config,parameter_set)
        for cell in cells:
            a = lems_results[template.format(cell,variable)]
            
            xvals.append(times)
            yvals.append(a)
            labels.append(cell)
            
            if cell==cells[0]:
                activities_n = np.array([a])
            else:
                activities_n = np.append(activities_n,[a],axis=0)

        #tasks.append((activities_n, info, cells, dt))
        if len(cells) > 24:
            plots(activities_n, info, cells, dt, heightened=True)
        else:
            plots(activities_n, info, cells, dt, heightened=False)
    
        if save:
            f = save_fig_path%('neuron_activity_%s_%s.png'%(parameter_set,config))
            c302.print_("Saving figure to: %s"%os.path.abspath(f))
            plt.savefig(f,bbox_inches='tight')

        #gen_traces_tasks.append((config, parameter_set, xvals, yvals, info, labels, save, save_fig_path, True, False))
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
    
    if plot_ca and parameter_set!='A' and len(muscles)>0:
        
        c302.print_("Plotting muscle activities ([Ca2+])")
        variable = 'activity'
        description = 'Activity'
            
        if parameter_set.startswith('C') or parameter_set.startswith('D'):
            variable = 'caConc'
            description = '[Ca2+]'
            
        xvals = []
        yvals = []
        labels = []

        info = '%s of %i muscles (%s %s)'%(description, len(muscles),config,parameter_set)
        for m in muscles:
            a = lems_results[template_m.format(m,variable)]
            
            xvals.append(times)
            yvals.append(a)
            labels.append(m)
            
            if m==muscles[0]:
                activities_n = np.array([a])
            else:
                activities_n = np.append(activities_n,[a],axis=0)

        #tasks.append((activities_n, info, muscles, dt))

        if len(muscles) > 24:
            plots(activities_n, info, muscles, dt, heightened=True)
        else:
            plots(activities_n, info, muscles, dt, heightened=False)
    
        if save:
            f = save_fig_path%('muscle_activity_%s_%s.png'%(parameter_set,config))
            c302.print_("Saving figure to: %s"%os.path.abspath(f))
            plt.savefig(f,bbox_inches='tight')

        #gen_traces_tasks.append((config, parameter_set, xvals, yvals, info, labels, save, save_fig_path, False, False))
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

    #results = [pool.apply_async(plots, t) for t in tasks]
    #gen_traces_plot_results = [pool.apply_async(generate_traces_plot, t) for t in gen_traces_tasks]

    #pool.close()
    #pool.join()

    if show_plot_already:
        try:
            plt.show()
        except KeyboardInterrupt:
            print("Interrupt received, stopping...")
    else:
        plt.close("all")
      
