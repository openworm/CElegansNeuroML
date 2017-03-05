import sys
import os
from pyneuroml import pynml
import matplotlib.pyplot as plt
import numpy as np
import c302
import collections


def plots(a_n, info, cells, dt):
    
    c302.print_('Generating plots for: %s'%info)
    
    fig, ax = plt.subplots()
    downscale = 10
    #print a_n.shape
    a_n_ = a_n[:,::downscale]
    #c302.print_(a_n_.shape) 
    
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
    
    cells.sort()
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
        
        plots(volts_n, info, cells, dt)
    
        if save:
            f = save_fig_path%('neurons_%s_%s.png'%(parameter_set,config))
            c302.print_("Saving figure to: %s"%os.path.abspath(f))
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

 
    muscles.sort()
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

        plots(mvolts_n, info, muscles, dt)
        
        if save:
            f = save_fig_path%('muscles_%s_%s.png'%(parameter_set,config))
            c302.print_("Saving figure to: %s"%os.path.abspath(f))
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

        plots(activities_n, info, cells, dt)
    
        if save:
            f = save_fig_path%('neuron_activity_%s_%s.png'%(parameter_set,config))
            c302.print_("Saving figure to: %s"%os.path.abspath(f))
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

        plots(activities_n, info, muscles, dt)
    
        if save:
            f = save_fig_path%('muscle_activity_%s_%s.png'%(parameter_set,config))
            c302.print_("Saving figure to: %s"%os.path.abspath(f))
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
        
        
def _show_conn_matrix(data, t, all_info_pre,all_info_post, type, save=False):
    
    fig, ax = plt.subplots()
    title = '%s: %s'%(type,t)
    plt.title(title)
    fig.canvas.set_window_title(title)
    import matplotlib
    cm = matplotlib.cm.get_cmap('gist_stern_r')
    
    if data.shape[0]>0 and data.shape[1]>0 and np.amax(data)>0:
        ##norm = matplotlib.colors.LogNorm(vmin=1, vmax=np.amax(data))
        maxn = int(np.amax(data))
    else:
        ##norm = None
        maxn = 0 
    print("Plotting data of size %s, max %s: %s"%(str(data.shape),maxn, t))
    im = plt.imshow(data, cmap=cm, interpolation='nearest',norm=None)
    
    ax = plt.gca();
    # Gridlines based on minor ticks
    ax.grid(which='minor', color='grey', linestyle='-', linewidth=.3)
    
    xt = np.arange(data.shape[1]) + 0
    ax.set_xticks(xt)
    ax.set_xticks(xt[:-1]+0.5,minor=True)
    ax.set_yticks(np.arange(data.shape[0]) + 0)
    ax.set_yticks(np.arange(data.shape[0]) + 0.5,minor=True)
    
    
    ax.set_yticklabels([all_info_pre[k][4] for k in all_info_pre.keys()])
    ax.set_xticklabels([all_info_post[k][4] for k in all_info_post.keys()])
    ax.set_ylabel('presynaptic')
    ax.set_xlabel('postsynaptic')
    fig.autofmt_xdate()
    
    
    #heatmap = ax.pcolor(data, cmap='gist_stern')
    cbar = plt.colorbar(im, ticks=range(maxn+1))
    cbar.set_ticklabels(range(maxn+1))

def generate_conn_matrix(nml_doc, save=False):
    
    net = nml_doc.networks[0]
    
    cc_exc_conns = {}
    cc_inh_conns = {}
    all_cells = []
    
    for cp in net.continuous_projections:
        if not cp.presynaptic_population in cc_exc_conns.keys():
            cc_exc_conns[cp.presynaptic_population] = {}
        if not cp.presynaptic_population in cc_inh_conns.keys():
            cc_inh_conns[cp.presynaptic_population] = {}
            
        if not cp.presynaptic_population in all_cells:
            all_cells.append(cp.presynaptic_population)
        if not cp.postsynaptic_population in all_cells:
            all_cells.append(cp.postsynaptic_population)
        
        for c in cp.continuousConnectionInstanceW:
            if 'inh' in c.post_component:
                cc_inh_conns[cp.presynaptic_population][cp.postsynaptic_population] = float(c.weight)
            else:
                cc_exc_conns[cp.presynaptic_population][cp.postsynaptic_population] = float(c.weight)
                
    print cc_exc_conns
    print cc_inh_conns
    
    gj_conns = {}
    for ep in net.electrical_projections:
        if not ep.presynaptic_population in gj_conns.keys():
            gj_conns[ep.presynaptic_population] = {}
            
        if not ep.presynaptic_population in all_cells:
            all_cells.append(ep.presynaptic_population)
        if not ep.postsynaptic_population in all_cells:
            all_cells.append(ep.postsynaptic_population)
        
        for e in ep.electricalConnectionInstanceW:
            gj_conns[ep.presynaptic_population][ep.postsynaptic_population] = float(e.weight)
            
            
    all_cells = sorted(all_cells)
    
    all_neuron_info, all_muscle_info = _get_cell_info(all_cells)
    all_neurons = [] 
    all_muscles = []
    for c in all_cells:
        if _is_muscle(c):
            all_muscles.append(c)
        else:
            all_neurons.append(c)
        
    
    data_exc_n = np.zeros((len(all_neurons),len(all_neurons)))
    data_exc_m = np.zeros((len(all_neurons),len(all_muscles)))
    
    data_inh_n = np.zeros((len(all_neurons),len(all_neurons)))
    data_inh_m = np.zeros((len(all_neurons),len(all_muscles)))
    
    for pre in cc_exc_conns.keys():
        for post in cc_exc_conns[pre].keys():
            print("Exc Conn %s -> %s: %s"%(pre,post,cc_exc_conns[pre][post]))
            if post in all_neurons:
                data_exc_n[all_neurons.index(pre),all_neurons.index(post)] = cc_exc_conns[pre][post]
            else:
                data_exc_m[all_neurons.index(pre),all_muscles.index(post)] = cc_exc_conns[pre][post]
            if pre in all_muscles:
                raise Exception("Unexpected...")
                
    for pre in cc_inh_conns.keys():
        for post in cc_inh_conns[pre].keys():
            print("Inh Conn %s -> %s: %s"%(pre,post,cc_inh_conns[pre][post]))
            if post in all_neurons:
                data_inh_n[all_neurons.index(pre),all_neurons.index(post)] = cc_inh_conns[pre][post]
            else:
                data_inh_m[all_neurons.index(pre),all_muscles.index(post)] = cc_inh_conns[pre][post]
            if pre in all_muscles:
                raise Exception("Unexpected...")
                
        
    print data_exc_n
    print data_exc_m
    print data_inh_n
    print data_inh_m
    
    _show_conn_matrix(data_exc_n, 'Excitatory (non GABA) conns to neurons',all_neuron_info,all_neuron_info, net.id)
    _show_conn_matrix(data_exc_m, 'Excitatory (non GABA) conns to muscles',all_neuron_info,all_muscle_info, net.id)
    
    _show_conn_matrix(data_inh_n, 'Inhibitory (GABA) conns to neurons',all_neuron_info,all_neuron_info, net.id)
    _show_conn_matrix(data_inh_m, 'Inhibitory (GABA) conns to muscles',all_neuron_info,all_muscle_info, net.id)
    
    
    data_n = np.zeros((len(all_neurons),len(all_neurons)))
    #data_m = np.zeros((len(all_neurons),len(all_muscles)))
    
    for pre in gj_conns.keys():
        for post in gj_conns[pre].keys():
            print("Elect Conn %s -> %s: %s"%(pre,post,gj_conns[pre][post]))
            
            if post in all_neurons:
                data_n[all_neurons.index(pre),all_neurons.index(post)] = gj_conns[pre][post]
            if post in all_muscles:
                raise Exception("Unexpected...")
            if pre in all_muscles:
                raise Exception("Unexpected...")
        
    
    _show_conn_matrix(data_n, 'Electrical (gap junction) conns to neurons',all_neuron_info,all_neuron_info, net.id)
    #_show_conn_matrix(data_m, 'Electrical (gap junction) conns to muscles',all_neuron_info,all_muscle_info, net.id)
        
def _get_cell_info(cells):

    import PyOpenWorm as P
    print("Connecting to the PyOpenWorm database...")
    P.connect()

    #Get the worm object.
    worm = P.Worm()

    #Extract the network object from the worm object.
    net = worm.neuron_network()

    #Go through our list and get the neuron object associated with each name.
    #Store these in another list.
    some_neurons = [P.Neuron(name) for name in cells]
    all_neuron_info = collections.OrderedDict()
    all_muscle_info = collections.OrderedDict()
    
    for neuron in some_neurons: 
        print("=====Checking properties of: %s"%neuron)
        print neuron.triples()
        print neuron.__class__
        short = ') %s'%neuron.name()
        if 'motor' in neuron.type():
            short = 'Mo%s'%short
        if 'sensory' in neuron.type():
            short = 'Se%s'%short
        if 'interneuron' in neuron.type():
            short = 'In%s'%short
        if _is_muscle(neuron.name()):
            short = 'Mu%s'%short
            
            
        short = '(%s'%short
        
        
        if 'GABA' in neuron.neurotransmitter():
            short = '- %s'%short
        elif len(neuron.neurotransmitter())==0:
            short = '? %s'%short
        else:
            short = '+ %s'%short
            
        info = (neuron, neuron.type(), neuron.receptor(), neuron.neurotransmitter(), short)
        #print dir(neuron)
        
        if _is_muscle(neuron.name()):
            all_muscle_info[neuron.name()] = info
        else:
            all_neuron_info[neuron.name()] = info
        
    return all_neuron_info, all_muscle_info
  
def _is_muscle(name):
    return name.startswith('MD') or name.startswith('MV')
            
if __name__ == '__main__':

    from neuroml.loaders import read_neuroml2_file
    
    configs = ['c302_C0_Syns.nml', 'c302_C0_Social.nml','c302_C0_Muscles.nml','c302_C0_Pharyngeal.nml','c302_C0_Oscillator.nml','c302_C0_Full.nml']
    configs = ['c302_C0_Syns.nml', 'c302_C0_Social.nml']
    configs = ['c302_C0_Muscles.nml']
    configs = ['c302_C0_Oscillator.nml']
    
    for c in configs:

        nml_doc = read_neuroml2_file('examples/%s'%c)

        generate_conn_matrix(nml_doc, save=True)
    
    
    plt.show()