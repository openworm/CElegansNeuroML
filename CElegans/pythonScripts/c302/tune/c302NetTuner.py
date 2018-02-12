'''

    Still under developemnt!!

    Subject to change without notice!!

'''

from neurotune import optimizers
from neurotune import utils
from matplotlib import pyplot as plt
from pyelectro import analysis

import sys
import os
import os.path
import time
import c302Evaluators
import c302Analysis
import c302Optimizers

import pprint

from collections import OrderedDict
#from memory_profiler import profile

prpr = pprint.PrettyPrinter(indent=4)


if not os.path.isfile('c302.py'):
    print('This script should be run from dir: CElegansNeuroML/CElegans/pythonScripts/c302')
    exit()

sys.path.append(".")

import c302
import c302_utils

from C302Controller import C302Controller

from c302ESOptimizer import ESOptimizer
from c302CustomOptimizer import CustomOptimizerA


def scale(scale, number, min=1):
    return max(min, int(scale*number))

#@profile
def run_optimisation(prefix,
                     config,
                     level,
                     parameters,
                     max_constraints,
                     min_constraints,
                     weights,
                     target_data,
                     data_reader="SpreadsheetDataReader",
                     config_package=None,
                     sim_time =            500,
                     dt =                  0.05,
                     analysis_start_time = 0,
                     population_size =     20,
                     max_evaluations =     20,
                     num_selected =        10,
                     num_offspring =       20,
                     mutation_rate =       0.9,
                     num_elites =          1,
                     seed =                12345,
                     input_list=None,
                     simulator =           'jNeuroML',
                     nogui =               False,
                     num_local_procesors_to_use = 4,
                     conns_to_include=[],
                     conns_to_exclude=[],
                     param_overrides=None,
                     max_generation_without_improvement=False):
                         
    print("Running optimisation...")
    print("parameters: %s"%parameters)
    print("max_constraints: %s"%max_constraints)
    print("min_constraints: %s"%min_constraints)
    print("simulator: %s"%simulator)
    ref = prefix+config

    run_dir = "NT_%s_%s"%(ref, time.ctime().replace(' ','_' ).replace(':','.' ))
    os.mkdir(run_dir)

    pool = None
    """if num_local_procesors_to_use > 1:
        import multiprocessing
        import signal

        original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)

        pool = multiprocessing.Pool(num_local_procesors_to_use)

        signal.signal(signal.SIGINT, original_sigint_handler)"""


    if int(num_local_procesors_to_use) != num_local_procesors_to_use or num_local_procesors_to_use < 1:
        raise Exception(
            'Error with num_local_procesors_to_use = %s\nPlease use an integer value greater then 1.' % num_local_procesors_to_use)

    job_server = None
    if num_local_procesors_to_use > 1:
        import pp
        ppservers = ()
        print("Starting pp job server with %i local processors" % num_local_procesors_to_use)
        job_server = pp.Server(num_local_procesors_to_use, ppservers=ppservers, secret="password")



    my_controller = C302Controller(ref, 
                                   level, 
                                   config, 
                                   sim_time,
                                   dt,
                                   data_reader=data_reader,
                                   config_package=config_package,
                                   input_list=input_list,
                                   simulator = simulator, 
                                   generate_dir=run_dir,
                                   pool=pool,
                                   job_server=job_server,
                                   num_local_procesors_to_use=num_local_procesors_to_use,
                                   conns_to_include=conns_to_include,
                                   conns_to_exclude=conns_to_exclude,
                                   param_overrides=param_overrides)

    peak_threshold = -31 if level.startswith('A') or level.startswith('B') else -10

    analysis_var = {'peak_delta':     0,
                    'baseline':       0,
                    'dvdt_threshold': 0, 
                    'peak_threshold': peak_threshold}

    data = ref+'.dat'

    sim_var = OrderedDict()
    if isinstance(parameters, list):
        # old version: parameter list with only param values
        for i in range(len(parameters)):
            sim_var[parameters[i]] = max_constraints[i] / 2 + min_constraints[i] / 2
    elif isinstance(parameters, dict):
        # new version: parameter dict with key=[name_of_param] and value={'value':'...', 'default_unit':'...'}
        idx = 0
        for k, v in parameters.iteritems():
            sim_var[k] = {'value': max_constraints[idx]/2 + min_constraints[idx]/2,
                          'unit': v['default_unit']}
            idx = idx + 1



    #make an evaluator, using automatic target evaluation:
    my_evaluator = c302Evaluators.EnhancedNetworkEvaluator(controller=my_controller,
                                                analysis_start_time=analysis_start_time,
                                                analysis_end_time=sim_time,
                                                parameters=parameters,
                                                analysis_var=analysis_var,
                                                weights=weights,
                                                targets=target_data,
                                                           job_server=job_server,)


    #make an optimizer
    my_optimizer = CustomOptimizerA(max_constraints,
                                             min_constraints,
                                             my_evaluator,
                                             population_size=population_size,
                                             max_evaluations=max_evaluations,
                                             num_selected=num_selected,
                                             num_offspring=num_offspring,
                                             num_elites=num_elites,
                                             mutation_rate=mutation_rate,
                                             seeds=None,
                                             verbose=True)

    """my_optimizer = ESOptimizer(max_constraints,
                               min_constraints,
                               my_evaluator,
                               population_size=population_size,
                               max_evaluations=max_evaluations,
                               num_selected=num_selected,
                               num_offspring=num_offspring,
                               num_elites=num_elites,
                               mutation_rate=mutation_rate,
                               seeds=None,
                               verbose=True)"""

    if max_generation_without_improvement:
        my_optimizer = c302Optimizers.CustomOptimizerA(max_constraints,
                                                 min_constraints,
                                                 my_evaluator,
                                                 population_size=population_size,
                                                 max_evaluations=max_evaluations,
                                                 num_selected=num_selected,
                                                 num_offspring=num_offspring,
                                                 num_elites=num_elites,
                                                 mutation_rate=mutation_rate,
                                                 seeds=None,
                                                 verbose=True,
                                                 max_generation_without_improvement=max_generation_without_improvement)

    start = time.time()
    #run the optimizer

    best_candidate, fitness = my_optimizer.optimize(do_plot=False,
                                                    seed=seed,
                                                    summary_dir = run_dir)

    if pool:
        pool.close()
        pool.join()

    if job_server:
        job_server.destroy()


    secs = time.time()-start
    
    reportj = {}
    info = "Ran %s evaluations (pop: %s) in %f seconds (%f mins total; %fs per eval)\n\n"%(max_evaluations, population_size, secs, secs/60.0, (secs/max_evaluations))
    report = "----------------------------------------------------\n\n"+ info
             
             
    reportj['comment'] = info
    reportj['time'] = secs


    #sim_var = OrderedDict()
    if isinstance(parameters, list):
        # old version: parameter list with only param values
        for key, value in zip(parameters, best_candidate):
            sim_var[key] = value
    elif isinstance(parameters, dict):
        idx = 0
        for k, v in parameters.iteritems():
            sim_var[k] = {'value': best_candidate[idx],
                          'unit': v['default_unit']}
            idx = idx + 1

    best_candidate_t, best_candidate_v = my_controller.run_individual(sim_var,show=False)
    
    best_candidate_results = my_controller.last_results

    best_candidate_analysis = c302Analysis.Data_Analyser(best_candidate_v,
                                               best_candidate_t,
                                               analysis_var,
                                               start_analysis=analysis_start_time,
                                               end_analysis=sim_time)

    best_cand_analysis_full = best_candidate_analysis.analyse()
    best_cand_analysis = best_candidate_analysis.analyse(target_data)

    report+="---------- Best candidate ------------------------------------------\n"
    
    report+=prpr.pformat(best_candidate)+"\n\n"
    report+=prpr.pformat(best_cand_analysis_full)+"\n"
    report+=prpr.pformat(best_cand_analysis)+"\n\n"
    report+="FITNESS: %f\n\n"%fitness
    
    print(report)
    
    reportj['fitness']=fitness
    reportj['fittest vars']=dict(sim_var)
    reportj['best_cand_details']=best_candidate
    reportj['best_cand_analysis_full']=best_cand_analysis_full
    reportj['best_cand_analysis']=best_cand_analysis
    reportj['parameters']=parameters
    reportj['analysis_var']=analysis_var
    reportj['target_data']=target_data
    reportj['weights']=weights
    
    reportj['analysis_start_time']=analysis_start_time
    
    reportj['population_size']=population_size
    reportj['max_evaluations']=max_evaluations
    reportj['num_selected']=num_selected
    reportj['num_offspring']=num_offspring
    reportj['mutation_rate']=mutation_rate
    reportj['num_elites']=num_elites
    reportj['seed']=seed
    reportj['simulator']=simulator
    
    reportj['sim_time']=sim_time
    reportj['dt']=dt
    
    reportj['run_directory'] = run_dir
    reportj['reference'] = ref
    
    report_file = open("%s/report.json"%run_dir,'w')
    report_file.write(prpr.pformat(reportj))
    report_file.close()
    
    plot_file = open("%s/plotgens.py"%run_dir,'w')
    plot_file.write('from neurotune.utils import plot_generation_evolution\nimport os\n')
    plot_file.write('\n')
    plot_file.write('parameters = %s\n'%parameters)
    plot_file.write('\n')
    plot_file.write("curr_dir = os.path.dirname(__file__) if len(os.path.dirname(__file__))>0 else '.'\n")
    plot_file.write("plot_generation_evolution(parameters, individuals_file_name = '%s/ga_individuals.csv'%curr_dir)\n")
    plot_file.close()



    if not nogui:
        added =[]
        save_to = "%s/best.png" % run_dir
        for wref in weights.keys():
            ref = wref.split(':')[0]
            if not ref in added and not "phase_offset" in ref:
                added.append(ref)
                best_candidate_plot = plt.plot(best_candidate_t,best_candidate_v[ref], label="%s - %i evaluations"%(ref,max_evaluations))



        plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True)

        plt.ylim(-80.0,80.0)
        plt.xlim(0.0,sim_time)
        plt.title("Models")
        plt.xlabel("Time (ms)")
        plt.ylabel("Membrane potential(mV)")

        plt.savefig(save_to, bbox_inches='tight')

        utils.plot_generation_evolution(sim_var.keys(), individuals_file_name='%s/ga_individuals.csv'%run_dir, save_to_file="%s/evo.png"%run_dir)

        c302_utils.plot_c302_results(best_candidate_results, config, level, directory=run_dir,save=True)



if __name__ == '__main__':

    parameters_B = ['neuron_to_neuron_chem_exc_syn_gbase',
                    'neuron_to_neuron_chem_inh_syn_gbase',
                    'neuron_to_neuron_elec_syn_gbase',
                    'chem_exc_syn_decay',
                    'chem_inh_syn_decay',
                    'unphysiological_offset_current']

    # above parameters will not be modified outside these bounds:
    min_constraints_B = [0.005, 0.005, 0.001, 3, 3, 2]
    max_constraints_B = [0.03, 0.03, 0.02, 20, 50, 6]

    weights_B = {}
    target_data_B = {}

    for cell in ['DB1', 'VB1', 'DB3', 'VB3', 'DB5', 'VB5', 'DB7', 'VB7']:
        var = '%s/0/generic_neuron_iaf_cell/v:mean_spike_frequency' % cell
        weights_B[var] = 1
        target_data_B[var] = 50
        var = '%s/0/generic_neuron_iaf_cell/v:average_minimum' % cell
        weights_B[var] = 1
        target_data_B[var] = -50

    parameters_C_based_neuron = ['neuron_leak_cond_density',
                                 'neuron_k_slow_cond_density',
                                 'neuron_k_fast_cond_density',
                                 'neuron_ca_boyle_cond_density']

    parameters_C_based_muscle = ['muscle_leak_cond_density',
                                 'muscle_k_slow_cond_density',
                                 'muscle_k_fast_cond_density',
                                 'muscle_ca_boyle_cond_density',
                                 'ca_conc_decay_time',
                                 'unphysiological_offset_current']

    parameters_C_based_net = ['neuron_to_neuron_exc_syn_conductance',
                              'neuron_to_neuron_inh_syn_conductance',
                              'neuron_to_neuron_elec_syn_gbase',
                              'neuron_to_muscle_exc_syn_conductance',
                              'neuron_to_muscle_inh_syn_conductance']  # No neuron -> muscle elect syns

    parameters_C_based = parameters_C_based_neuron + parameters_C_based_muscle + parameters_C_based_net

    min_constraints_neuron_loose = [.005, .1, 0.005, .1]
    max_constraints_neuron_loose = [.2, 2, 0.1, 2]
    min_constraints_muscle_loose = [.005, .1, 0.005, .1, 10, 2]
    max_constraints_muscle_loose = [.2, 2, 0.1, 2, 100, 8]

    min_constraints_neuron_tight = [0.0045, 1.8, 0.07, 1.6]
    max_constraints_neuron_tight = [0.0055, 1.9, 0.08, 1.7]
    min_constraints_muscle_tight = [0.0045, 1.8, 0.07, 1.6, 10, 6]
    max_constraints_muscle_tight = [0.0055, 1.9, 0.08, 1.7, 12, 7]

    min_constraints_net_loose = [.01, .01, 0.0005, .01, .01]
    max_constraints_net_loose = [.1, .1, 0.01, .1, .1]

    min_constraints_net_tight = [0.09, 0.09, 0.00048, 0.09, 0.09]
    max_constraints_net_tight = [0.11, 0.11, 0.00052, 0.11, 0.11]

    from parameters_C0 import ParameterisedModel as ParameterisedModelC0

    pmC0 = ParameterisedModelC0()

    parameters_C0_based_neuron = ['neuron_leak_cond_density',
                                  'neuron_k_slow_cond_density',
                                  'neuron_ca_simple_cond_density']

    parameters_C0_based_muscle = ['muscle_leak_cond_density',
                                  'muscle_k_slow_cond_density',
                                  'muscle_ca_simple_cond_density']

    parameters_C0_based_net = ['neuron_to_neuron_exc_syn_conductance',
                               'neuron_to_neuron_inh_syn_conductance',
                               'neuron_to_neuron_elec_syn_gbase',
                               'neuron_to_muscle_exc_syn_conductance',
                               'neuron_to_muscle_inh_syn_conductance']  # No neuron -> muscle elect syns

    parameters_C0_based_net = ['neuron_to_neuron_exc_syn_conductance',
                               'neuron_to_neuron_inh_syn_conductance',
                               'exc_syn_k',
                               'inh_syn_k']

    parameters_C0_based_net = ['neuron_to_neuron_exc_syn_conductance',
                               'neuron_to_neuron_inh_syn_conductance',
                               'exc_syn_vth',
                               'inh_syn_vth',
                               'exc_syn_ad',
                               'inh_syn_ad',
                               'unphysiological_offset_current']

    parameters_C0_based_net = ['neuron_to_neuron_exc_syn_conductance',
                               'neuron_to_neuron_inh_syn_conductance',
                               'exc_syn_ad',
                               'inh_syn_ad']

    parameters_C0_based = parameters_C0_based_neuron + parameters_C0_based_muscle + parameters_C0_based_net

    tight_min = 0.95
    tight_max = 1.05
    loose_min = 0.1
    loose_max = 10

    min_constraints_neuron_tight_C0 = [pmC0.get_bioparameter(p).x() * tight_min for p in parameters_C0_based_neuron]
    max_constraints_neuron_tight_C0 = [pmC0.get_bioparameter(p).x() * tight_max for p in parameters_C0_based_neuron]

    min_constraints_neuron_loose_C0 = [pmC0.get_bioparameter(p).x() * loose_min for p in parameters_C0_based_neuron]
    max_constraints_neuron_loose_C0 = [pmC0.get_bioparameter(p).x() * loose_max for p in parameters_C0_based_neuron]

    min_constraints_muscle_tight_C0 = [pmC0.get_bioparameter(p).x() * tight_min for p in parameters_C0_based_muscle]
    max_constraints_muscle_tight_C0 = [pmC0.get_bioparameter(p).x() * tight_max for p in parameters_C0_based_muscle]

    min_constraints_net_tight_C0 = [pmC0.get_bioparameter(p).x() * tight_min for p in parameters_C0_based_net]
    max_constraints_net_tight_C0 = [pmC0.get_bioparameter(p).x() * tight_max for p in parameters_C0_based_net]

    min_constraints_net_loose_C0 = [pmC0.get_bioparameter(p).x() * loose_min for p in parameters_C0_based_net]
    max_constraints_net_loose_C0 = [pmC0.get_bioparameter(p).x() * loose_max for p in parameters_C0_based_net]

    weights0 = {}
    target_data0 = {}

    cells = ['DB1', 'VB1', 'DB2', 'VB2', 'DB3', 'VB3', 'DB4', 'VB4', 'DB5', 'VB5', 'DB6', 'VB6', 'DB7', 'VB7']

    for cell in cells:
        var = '%s/0/GenericNeuronCell/v:mean_spike_frequency' % cell
        weights0[var] = 1
        target_data0[var] = 4  # Hz

    # phase offset

    i = 0
    while i < len(cells):

        if len(cells) % 2 != 0:
            raise Exception(
                "Error in phase target and weight formation, cells array does not contain a valid number of pairs")

        var = '%s/0/GenericNeuronCell/v' % cells[i] + ';%s/0/GenericNeuronCell/v' % cells[i + 1] + ';phase_offset'
        i += 2

        weights0[var] = 1

        target_data0[var] = 180

    
    nogui = '-nogui' in sys.argv
        
    simulator  = 'jNeuroML_NEURON'

    if '-full' in sys.argv:

        scalem = 5
        max_c = max_constraints_neuron_tight + max_constraints_muscle_tight + max_constraints_net_loose
        min_c = min_constraints_neuron_tight + min_constraints_muscle_tight + min_constraints_net_loose
        
        max_c = max_constraints_neuron_loose + max_constraints_muscle_tight + max_constraints_net_loose
        min_c = min_constraints_neuron_loose + min_constraints_muscle_tight + min_constraints_net_loose
        
        run_optimisation('Test',
                         'Full',
                         'C1',
                         parameters_C_based,
                         max_c,
                         min_c,
                         weights0,
                         target_data0,
                         sim_time = 1000,
                         dt = 0.1,
                         population_size =  scale(scalem,100),
                         max_evaluations =  scale(scalem,500),
                         num_selected =     scale(scalem,20),
                         num_offspring =    scale(scalem,20),
                         mutation_rate =    0.9,
                         num_elites =       scale(scalem,3),
                         nogui =            nogui,
                         simulator = simulator,
                         num_local_procesors_to_use =8)
        
    if '-muscB' in sys.argv:
            
            scalem = 1
        
            run_optimisation('Test',
                             'Muscles',
                             'B',
                             parameters_B,
                             max_constraints_B,
                             min_constraints_B,
                             weights_B,
                             target_data_B,
                             sim_time = 1000,
                             dt = 0.1,
                             population_size =  scale(scalem,100),
                             max_evaluations =  scale(scalem,500),
                             num_selected =     scale(scalem,20),
                             num_offspring =    scale(scalem,20),
                             mutation_rate =    0.9,
                             num_elites =       scale(scalem,3),
                             nogui =            nogui,
                             seed =             1245637,
                             simulator = simulator,
                             num_local_procesors_to_use = 10)
        
        
    elif '-musc' in sys.argv or '-muscC0' in sys.argv or '-muscone' in sys.argv:
        
        if '-musc' in sys.argv:
            
            scalem = 5
            max_c = max_constraints_neuron_tight + max_constraints_muscle_tight + max_constraints_net_loose
            min_c = min_constraints_neuron_tight + min_constraints_muscle_tight + min_constraints_net_loose

            max_c = max_constraints_neuron_loose + max_constraints_muscle_tight + max_constraints_net_loose
            min_c = min_constraints_neuron_loose + min_constraints_muscle_tight + min_constraints_net_loose
        
            run_optimisation('Test',
                             'Muscles',
                             'C1',
                             parameters_C_based,
                             max_c,
                             min_c,
                             weights0,
                             target_data0,
                             sim_time = 1000,
                             dt = 0.1,
                             population_size =  scale(scalem,100),
                             max_evaluations =  scale(scalem,500),
                             num_selected =     scale(scalem,20),
                             num_offspring =    scale(scalem,20),
                             mutation_rate =    0.9,
                             num_elites =       scale(scalem,3),
                             nogui =            nogui,
                             seed =             1234,
                             simulator = simulator,
                             num_local_procesors_to_use = 8)
                             
        elif '-muscC0' in sys.argv:
            
            scalem =10
            max_c0 = max_constraints_neuron_tight_C0 + max_constraints_muscle_tight_C0 + max_constraints_net_loose_C0
            min_c0 = min_constraints_neuron_tight_C0 + min_constraints_muscle_tight_C0 + min_constraints_net_loose_C0
            
            weights = {}
            target_data = {}
            
            simulator  = 'jNeuroML_NEURON'
            
            for cell in ['DB2','VB2','DB3','VB3']:
                var = '%s/0/GenericNeuronCell/v:max_peak_no'%cell
                target_data[var] = 4
                var = '%s/0/GenericNeuronCell/v:min_peak_no'%cell
                target_data[var] = 4
            
            for c in ['DB2','VB2','DB3','VB3']:
                var = '%s/0/GenericNeuronCell/v:maximum'%c
                target_data[var] = 0
                var = '%s/0/GenericNeuronCell/v:minimum'%c
                target_data[var] = -70

            for key in target_data.keys():
                weights[key] = 1
                if 'imum' in key:
                    weights[key] = .1
        
            run_optimisation('Test',
                             'Muscles',
                             'C0',
                             parameters_C0_based,
                             max_c0,
                             min_c0,
                             weights,
                             target_data,
                             sim_time = 1000,
                             dt = 0.1,
                             population_size =  scale(scalem,100),
                             max_evaluations =  scale(scalem,500),
                             num_selected =     scale(scalem,20),
                             num_offspring =    scale(scalem,20),
                             mutation_rate =    0.9,
                             num_elites =       scale(scalem,2),
                             nogui =            nogui,
                             seed =             1234,
                             simulator = simulator,
                             num_local_procesors_to_use = 12)
        else:
            
            sim_time = 1000
            simulator  = 'jNeuroML_NEURON'
            
            my_controller = C302Controller('TestOsc', 'C1', 'Muscles', sim_time, 0.1, simulator = simulator)

            #test = [0.030982235821054638, 0.7380672812995235, 0.07252703867293844, 0.8087106170838071, 0.045423417312661474, 0.011449079144697817, 0.0049614426482976716, 2.361816408316808]
            sim_var = OrderedDict({   'ca_boyle_cond_density': 1.6862775772264702,
                        'neuron_to_muscle_elec_syn_gbase': 0.0005,
                        'neuron_to_muscle_exc_syn_conductance': 0.1,
                        'neuron_to_muscle_inh_syn_conductance': 0.1,
                        'muscle_k_fast_cond_density': 0.0711643917483308,
                        'muscle_k_slow_cond_density': 1.8333751019872582,
                        'muscle_leak_cond_density': 0.005,
                        'unphysiological_offset_current': 6.076428433117039})
            #for i in range(len(parameters)):
            #    sim_var[parameters[i]] = test[i]
                  
            example_run_t, example_run_v = my_controller.run_individual(sim_var, show=True)

            print("Have run individual instance...")

            peak_threshold = 0

            analysis_var = {'peak_delta':     0,
                            'baseline':       0,
                            'dvdt_threshold': 0, 
                            'peak_threshold': peak_threshold}

            example_run_analysis=analysis.NetworkAnalysis(example_run_v,
                                                       example_run_t,
                                                       analysis_var,
                                                       start_analysis=0,
                                                       end_analysis=sim_time)

            analysis = example_run_analysis.analyse()

            prpr.pprint(analysis)

            analysis = example_run_analysis.analyse(weights0.keys())

            prpr.pprint(analysis)
            
                         
    elif '-osc' in sys.argv:

        parameters = ['neuron_to_muscle_chem_exc_syn_gbase',
                      'chem_exc_syn_decay',
                      'neuron_to_muscle_chem_inh_syn_gbase',
                      'chem_inh_syn_decay',
                      'neuron_to_muscle_elec_syn_gbase',
                      'unphysiological_offset_current']

        #above parameters will not be modified outside these bounds:
        min_constraints = [0.001, 3,   0.001, 3,    0.01,   2]
        max_constraints = [0.02,  40, 0.02,   100,  0.2,    5]
        
        weights = {}
        target_data = {}
        
        
        for cell in ['DB3','VB3','DB4','VB4']:
            var = '%s/0/generic_neuron_iaf_cell/v:mean_spike_frequency'%cell
            weights[var] = 1
            target_data[var] = 30

        run_optimisation('Test',
                         'Oscillator',
                         'B',
                         parameters,
                         max_constraints,
                         min_constraints,
                         weights,
                         target_data,
                         sim_time = 500,
                         dt = 0.1,
                         population_size =  10,
                         max_evaluations =  20,
                         num_selected =     5,
                         num_offspring =    5,
                         mutation_rate =    0.9,
                         num_elites =       1,
                         seed =             123477,
                         nogui =            nogui,
                         num_local_procesors_to_use =10)
                         
    elif '-oscC0' in sys.argv:
        
        scalem = 1
        max_c0 = max_constraints_neuron_tight_C0 + max_constraints_muscle_tight_C0 + max_constraints_net_loose_C0
        min_c0 = min_constraints_neuron_tight_C0 + min_constraints_muscle_tight_C0 + min_constraints_net_loose_C0
        
        max_c0 = max_constraints_neuron_loose_C0 + max_constraints_muscle_tight_C0 + max_constraints_net_tight_C0
        min_c0 = min_constraints_neuron_loose_C0 + min_constraints_muscle_tight_C0 + min_constraints_net_tight_C0
        
        max_c0 = max_constraints_neuron_loose_C0 + max_constraints_muscle_tight_C0 + max_constraints_net_loose_C0
        min_c0 = min_constraints_neuron_loose_C0 + min_constraints_muscle_tight_C0 + min_constraints_net_loose_C0
        
        print("Max: %s"%max_c0)
        print("Min: %s"%min_c0)

        weights = {}
        target_data = {}
        
        for cell in ['DB2','VB2','DB3','VB3']:
            var = '%s/0/GenericNeuronCell/v:max_peak_no'%cell
            target_data[var] = 4
            var = '%s/0/GenericNeuronCell/v:min_peak_no'%cell
            target_data[var] = 4
        
        for c in ['DB2','VB2','DB3','VB3']:
            var = '%s/0/GenericNeuronCell/v:maximum'%c
            target_data[var] = -10
            var = '%s/0/GenericNeuronCell/v:minimum'%c
            target_data[var] = -70
        
        for key in target_data.keys():
            weights[key] = 1
            if 'imum' in key:
                weights[key] = .02
            
        #simulator = 'jNeuroML'
        simulator  = 'jNeuroML_NEURON'
        
        run_optimisation('Test',
                         'Oscillator',
                         'C0',
                         parameters_C0_based,
                         max_c0,
                         min_c0,
                         weights,
                         target_data,
                         sim_time = 2000,
                         dt = 0.1,
                         population_size =  scale(scalem,100),
                         max_evaluations =  scale(scalem,500),
                         num_selected =     scale(scalem,20),
                         num_offspring =    scale(scalem,20),
                         mutation_rate =    0.9,
                         num_elites =       scale(scalem,4),
                         nogui =            nogui,
                         seed =             123445,
                         simulator = simulator,
                         num_local_procesors_to_use = 8)

    elif '-oscC1' in sys.argv or '-oscC1one' in sys.argv:

        parameters = ['muscle_leak_cond_density',
                      'muscle_k_slow_cond_density',
                      'muscle_k_fast_cond_density',
                      'muscle_ca_boyle_cond_density',
                      'neuron_to_muscle_exc_syn_conductance',
                      'neuron_to_muscle_inh_syn_conductance',
                      'neuron_to_muscle_elec_syn_gbase',
                      'unphysiological_offset_current']

        #above parameters will not be modified outside these bounds:
        min_constraints = [.01,.1, 0.01, .1, .01, .01, 0.0005, 1]
        max_constraints = [.2,  1, 0.1,   1, .05, .05, 0.005,  6]
        
        weights = {}
        target_data = {}
        
        
        for cell in ['DB3','VB3','DB4','VB4','PVCL']:
            var = '%s/0/GenericNeuronCell/v:mean_spike_frequency'%cell
            weights[var] = 1
            target_data[var] = 4
            
        if '-oscC1' in sys.argv:

            simulator  = 'jNeuroML_NEURON'
            run_optimisation('Test',
                             'Oscillator',
                             'C1',
                             parameters,
                             max_constraints,
                             min_constraints,
                             weights,
                             target_data,
                             sim_time = 1000,
                             dt = 0.1,
                             population_size =  20,
                             max_evaluations =  20,
                             num_selected =     100,
                             num_offspring =    100,
                             mutation_rate =    0.9,
                             num_elites =       6,
                             seed =             12347,
                             nogui =            nogui,
                             simulator = simulator,
                             num_local_procesors_to_use = 10)
        else:
               
            sim_time = 1000
            simulator  = 'jNeuroML_NEURON'
            
            my_controller = C302Controller('TestOsc', 'C1', 'Oscillator', sim_time, 0.1, simulator = simulator)

            test = [0.030982235821054638, 0.7380672812995235, 0.07252703867293844, 0.8087106170838071, 0.045423417312661474, 0.011449079144697817, 0.0049614426482976716, 2.361816408316808]
            sim_var = OrderedDict()
            for i in range(len(parameters)):
                sim_var[parameters[i]] = test[i]
                  
            example_run_t, example_run_v = my_controller.run_individual(sim_var, show=True)

            print("Have run individual instance...")

            peak_threshold = 0

            analysis_var = {'peak_delta':     0,
                            'baseline':       0,
                            'dvdt_threshold': 0, 
                            'peak_threshold': peak_threshold}

            example_run_analysis=analysis.NetworkAnalysis(example_run_v,
                                                       example_run_t,
                                                       analysis_var,
                                                       start_analysis=0,
                                                       end_analysis=sim_time)

            analysis = example_run_analysis.analyse()

            prpr.pprint(analysis)

            analysis = example_run_analysis.analyse(weights.keys())

            prpr.pprint(analysis)

        print("Running opt on muscle...")
        parameters = ['muscle_leak_cond_density',
                'muscle_k_slow_cond_density',
                'muscle_ca_simple_cond_density', 
                'muscle_specific_capacitance',
                'leak_erev',
                'k_slow_erev',
                'ca_simple_erev']

        #above parameters will not be modified outside these bounds:
        min_constraints = [0.0003,    0.05,   0.05,       0.2,   -70, -90,  30]
        max_constraints = [0.01,    0.7,      0.5,     1.8,     -40, -60,  60]

        analysis_var={'peak_delta':0,'baseline':0,'dvdt_threshold':0, 'peak_threshold':0}

        cell_ref = 'MDR01/0/GenericMuscleCell/v'
             
        weights = {cell_ref+':average_minimum': 1, 
                   cell_ref+':mean_spike_frequency': 1, 
                   cell_ref+':average_maximum': 1,  
                   cell_ref+':max_peak_no': 1}
        
        
        target_data = {cell_ref+':average_minimum': -70,
                       cell_ref+':mean_spike_frequency': 4, 
                       cell_ref+':average_maximum': 40,  
                       cell_ref+':max_peak_no': 8}

        simulator  = 'jNeuroML_NEURON'
        
        scalem = 10
        run_optimisation('Test',
                         'IClampMuscle',
                         'C0',
                         parameters,
                         max_constraints,
                         min_constraints,
                         weights,
                         target_data,
                         sim_time = 2000,
                         dt = 0.1,
                         population_size =  scale(scalem,100),
                         max_evaluations =  scale(scalem,500),
                         num_selected =     scale(scalem,20),
                         num_offspring =    scale(scalem,30),
                         mutation_rate =    0.9,
                         num_elites =       scale(scalem,5),
                         seed =             1234778,
                         nogui =            nogui,
                         simulator = simulator,
                         num_local_procesors_to_use = 12)


    elif '-avb-vb-C2' in sys.argv:

        parameters = OrderedDict()
        min_constraints = []
        max_constraints = []

        for vbx in range(1, 12):
            if 'vbx' != 3:
                parameters['AVBL_to_VB%s_elec_syn_gbase_mirrored' % vbx] = {'default_unit': 'nS'}
                min_constraints.append(0.001)
                max_constraints.append(0.1)
                parameters['AVBL_to_VB%s_elec_syn_sigma_mirrored' % vbx] = {'default_unit': 'per_mV'}
                min_constraints.append(0.001)
                max_constraints.append(0.8)
                parameters['AVBL_to_VB%s_elec_syn_mu_mirrored' % vbx] = {'default_unit': 'mV'}
                #min_constraints.append(-80 + 4*vbx-1)
                #max_constraints.append(-40 + 5*vbx-1)
                min_constraints.append(-80)
                max_constraints.append(20)
        for vbx in range(1, 12):
            if 'vbx' != 1:
                parameters['AVBR_to_VB%s_elec_syn_gbase_mirrored' % vbx] = {'default_unit': 'nS'}
                min_constraints.append(0.001)
                max_constraints.append(0.1)
                parameters['AVBR_to_VB%s_elec_syn_sigma_mirrored' % vbx] = {'default_unit': 'per_mV'}
                min_constraints.append(0.001)
                max_constraints.append(0.8)
                parameters['AVBR_to_VB%s_elec_syn_mu_mirrored' % vbx] = {'default_unit': 'mV'}
                #min_constraints.append(-80 + 4 * vbx - 1)
                #max_constraints.append(-40 + 5 * vbx - 1)
                min_constraints.append(-80)
                max_constraints.append(20)

        for vbx in range(1, 11):
            parameters['VB%s_to_VB%s_elec_syn_gbase_mirrored' % (vbx, vbx+1)] = {'default_unit': 'nS'}
            min_constraints.append(0.001)
            max_constraints.append(0.05)
        parameters['VB2_to_VB4_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.001)
        max_constraints.append(0.05)

        target_data = {}
        target_data['VB1/0/GenericNeuronCell/v' + ':first_spike_time'] = 125
        target_data['VB2/0/GenericNeuronCell/v' + ':first_spike_time'] = 133
        target_data['VB3/0/GenericNeuronCell/v' + ':first_spike_time'] = 141
        target_data['VB4/0/GenericNeuronCell/v' + ':first_spike_time'] = 149
        target_data['VB5/0/GenericNeuronCell/v' + ':first_spike_time'] = 157
        target_data['VB6/0/GenericNeuronCell/v' + ':first_spike_time'] = 165
        target_data['VB7/0/GenericNeuronCell/v' + ':first_spike_time'] = 173
        target_data['VB8/0/GenericNeuronCell/v' + ':first_spike_time'] = 181
        target_data['VB9/0/GenericNeuronCell/v' + ':first_spike_time'] = 189
        target_data['VB10/0/GenericNeuronCell/v' + ':first_spike_time'] = 197
        target_data['VB11/0/GenericNeuronCell/v' + ':first_spike_time'] = 205

        weights = {}
        weights['VB1/0/GenericNeuronCell/v' + ':first_spike_time'] = 10
        weights['VB2/0/GenericNeuronCell/v' + ':first_spike_time'] = 10
        weights['VB3/0/GenericNeuronCell/v' + ':first_spike_time'] = 10
        weights['VB4/0/GenericNeuronCell/v' + ':first_spike_time'] = 10
        weights['VB5/0/GenericNeuronCell/v' + ':first_spike_time'] = 10
        weights['VB6/0/GenericNeuronCell/v' + ':first_spike_time'] = 10
        weights['VB7/0/GenericNeuronCell/v' + ':first_spike_time'] = 10
        weights['VB8/0/GenericNeuronCell/v' + ':first_spike_time'] = 10
        weights['VB9/0/GenericNeuronCell/v' + ':first_spike_time'] = 10
        weights['VB10/0/GenericNeuronCell/v' + ':first_spike_time'] = 10
        weights['VB11/0/GenericNeuronCell/v' + ':first_spike_time'] = 10

        input_list = [
            ('AVBL', '50ms', '600ms', '15pA'),
            ('AVBR', '50ms', '600ms', '15pA'),
        ]

        simulator = 'jNeuroML_NEURON'
        run_optimisation('Delay_AVB_VB_Case1_800_10k_200_200_0.1_20',
                         'AVB_VB',
                         'C2',
                         parameters,
                         max_constraints,
                         min_constraints,
                         weights,
                         target_data,
                         config_package='notebooks.configs.AVB',
                         data_reader='UpdatedSpreadsheetDataReader',
                         sim_time=700,
                         dt=0.05,
                         population_size=800,
                         max_evaluations=10000,
                         num_selected=200,
                         num_offspring=200,
                         mutation_rate=0.1,
                         num_elites=20,
                         seed=12347,
                         nogui=nogui,
                         simulator=simulator,
                         input_list=input_list,
                         num_local_procesors_to_use=20)



    elif '-avb-vb-p-C2' in sys.argv:

        parameters = OrderedDict()
        min_constraints = []
        max_constraints = []

        for vbx in range(1, 12):
            if 'vbx' != 3:
                parameters['AVBL_to_VB%s_elec_syn_gbase_mirrored' % vbx] = {'default_unit': 'nS'}
                min_constraints.append(0.001)
                max_constraints.append(0.1)

        for vbx in range(1, 12):
            if 'vbx' != 1:
                parameters['AVBR_to_VB%s_elec_syn_gbase_mirrored' % vbx] = {'default_unit': 'nS'}
                min_constraints.append(0.001)
                max_constraints.append(0.1)


        for vbx in range(1, 11):
            parameters['VB%s_to_VB%s_elec_syn_gbase_mirrored' % (vbx, vbx+1)] = {'default_unit': 'nS'}
            min_constraints.append(0.001)
            max_constraints.append(0.1)
            parameters['VB%s_to_VB%s_elec_syn_sigma_mirrored' % (vbx, vbx + 1)] = {'default_unit': 'per_mV'}
            min_constraints.append(0.01)
            max_constraints.append(0.8)
            parameters['VB%s_to_VB%s_elec_syn_mu_mirrored' % (vbx, vbx + 1)] = {'default_unit': 'mV'}
            min_constraints.append(-80)
            max_constraints.append(30)
        parameters['VB2_to_VB4_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.001)
        max_constraints.append(0.1)
        parameters['VB2_to_VB4_elec_syn_sigma_mirrored'] = {'default_unit': 'per_mV'}
        min_constraints.append(0.01)
        max_constraints.append(0.8)
        parameters['VB2_to_VB4_elec_syn_mu_mirrored'] = {'default_unit': 'mV'}
        min_constraints.append(-80)
        max_constraints.append(30)

        target_data = {}
        target_data['VB1/0/GenericNeuronCell/v' + ':first_spike_time'] = 125
        target_data['VB2/0/GenericNeuronCell/v' + ':first_spike_time'] = 133
        target_data['VB3/0/GenericNeuronCell/v' + ':first_spike_time'] = 141
        target_data['VB4/0/GenericNeuronCell/v' + ':first_spike_time'] = 149
        target_data['VB5/0/GenericNeuronCell/v' + ':first_spike_time'] = 157
        target_data['VB6/0/GenericNeuronCell/v' + ':first_spike_time'] = 165
        target_data['VB7/0/GenericNeuronCell/v' + ':first_spike_time'] = 173
        target_data['VB8/0/GenericNeuronCell/v' + ':first_spike_time'] = 181
        target_data['VB9/0/GenericNeuronCell/v' + ':first_spike_time'] = 189
        target_data['VB10/0/GenericNeuronCell/v' + ':first_spike_time'] = 197
        target_data['VB11/0/GenericNeuronCell/v' + ':first_spike_time'] = 205

        weights = {}
        weights['VB1/0/GenericNeuronCell/v' + ':first_spike_time'] = 10
        weights['VB2/0/GenericNeuronCell/v' + ':first_spike_time'] = 10
        weights['VB3/0/GenericNeuronCell/v' + ':first_spike_time'] = 10
        weights['VB4/0/GenericNeuronCell/v' + ':first_spike_time'] = 10
        weights['VB5/0/GenericNeuronCell/v' + ':first_spike_time'] = 10
        weights['VB6/0/GenericNeuronCell/v' + ':first_spike_time'] = 10
        weights['VB7/0/GenericNeuronCell/v' + ':first_spike_time'] = 10
        weights['VB8/0/GenericNeuronCell/v' + ':first_spike_time'] = 10
        weights['VB9/0/GenericNeuronCell/v' + ':first_spike_time'] = 10
        weights['VB10/0/GenericNeuronCell/v' + ':first_spike_time'] = 10
        weights['VB11/0/GenericNeuronCell/v' + ':first_spike_time'] = 10

        input_list = [
            ('AVBL', '50ms', '600ms', '15pA'),
            ('AVBR', '50ms', '600ms', '15pA'),
        ]

        simulator = 'jNeuroML_NEURON'
        run_optimisation('Delay_AVB_VB_Case2_800_10k_200_200_0.1_20',
                         'AVB_VB',
                         'C2',
                         parameters,
                         max_constraints,
                         min_constraints,
                         weights,
                         target_data,
                         config_package='notebooks.configs.AVB',
                         data_reader='UpdatedSpreadsheetDataReader',
                         sim_time=700,
                         dt=0.05,
                         population_size=800,
                         max_evaluations=10000,
                         num_selected=200,
                         num_offspring=200,
                         mutation_rate=0.1,
                         num_elites=20,
                         seed=12347,
                         nogui=nogui,
                         simulator=simulator,
                         input_list=input_list,
                         num_local_procesors_to_use=20)


    elif '-fw-C2' in sys.argv:

        sim_time = 4000

        parameters = OrderedDict()
        min_constraints = []
        max_constraints = []

        parameters['AVBL_to_AVBR_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['AVBL_to_VB2_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.02)
        parameters['AVBR_to_AVBL_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['AVBR_to_DB4_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.02)
        parameters['AVBR_to_VD3_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.02)
        parameters['DB1_to_DD1_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB1_to_VD2_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB1_to_VD3_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB2_to_DD1_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB2_to_DD2_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB2_to_VD3_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB2_to_VD4_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB3_to_DD2_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB3_to_DD3_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB3_to_DD5_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB3_to_VD4_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB3_to_VD5_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB3_to_VD6_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB4_to_DD3_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB4_to_DD4_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB4_to_DD5_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB4_to_DD6_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB4_to_VD6_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB5_to_VD4_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB5_to_VD5_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB5_to_VD6_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB5_to_VD7_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB6_to_VD7_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB6_to_VD8_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB6_to_VD9_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB7_to_VD8_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB7_to_VD9_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB7_to_VD10_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB7_to_VD11_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB7_to_VD12_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['DB7_to_VD13_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)

        parameters['DD1_to_VB2_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.4)
        parameters['DD1_to_VD2_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.4)
        parameters['DD2_to_VD3_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.4)
        parameters['DD2_to_VD4_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.4)

        parameters['VB1_to_DD1_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB1_to_VD1_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB1_to_VD2_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB2_to_DD1_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB2_to_DD2_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB2_to_VD2_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB2_to_VD3_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB3_to_DD2_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB3_to_VD3_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB3_to_VD4_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB4_to_DD2_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB4_to_DD3_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB4_to_VB5_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.02)
        parameters['VB4_to_VD4_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB4_to_VD5_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB5_to_DD3_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB5_to_VD6_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB6_to_DD4_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB6_to_VD6_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB6_to_VD7_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB7_to_DD5_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB7_to_VD8_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB7_to_VD9_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB8_to_DD5_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB8_to_DD6_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB8_to_VD9_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB8_to_VD10_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB9_to_DD5_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB9_to_DD6_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB9_to_VD10_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB9_to_VD11_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB10_to_DD6_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB10_to_VD11_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB10_to_VD12_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB11_to_DD6_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB11_to_VD12_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)
        parameters['VB11_to_VD13_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(2.0)

        parameters['VD1_to_DD1_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.4)
        parameters['VD1_to_VB1_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.4)
        parameters['VD2_to_DD1_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.4)
        parameters['VD2_to_VB2_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.4)
        parameters['VD3_to_DD1_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.4)
        parameters['VD3_to_VB2_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.4)
        parameters['VD3_to_VB3_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.4)
        parameters['VD4_to_VB3_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.4)
        parameters['VD5_to_VB1_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.4)
        parameters['VD5_to_VB4_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.4)
        parameters['VD6_to_VB5_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.4)
        parameters['VD7_to_VB6_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.4)
        parameters['VD7_to_VB7_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.4)
        parameters['VD8_to_VB7_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.4)
        parameters['VD9_to_VB8_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.4)
        parameters['VD10_to_VB9_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.4)
        parameters['VD11_to_DD6_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.4)
        parameters['VD11_to_VB10_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.4)
        parameters['VD12_to_DD6_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.4)
        parameters['VD12_to_VB11_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.4)
        parameters['VD13_to_DD6_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.4)
        parameters['VD13_to_VD12_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.4)

        parameters['AVBL_to_AVBR_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)
        parameters['AVBL_to_DB2_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBL_to_DB3_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBL_to_DB4_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBL_to_DB5_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBL_to_DB6_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBL_to_DB7_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBL_to_VB1_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBL_to_VB2_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBL_to_VB4_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBL_to_VB5_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBL_to_VB6_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBL_to_VB7_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBL_to_VB8_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBL_to_VB9_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBL_to_VB10_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBL_to_VB11_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBR_to_DB1_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBR_to_DB2_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBR_to_DB3_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBR_to_DB4_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBR_to_DB5_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBR_to_DB6_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBR_to_DB7_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBR_to_VB2_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBR_to_VB3_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBR_to_VB4_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBR_to_VB5_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBR_to_VB6_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBR_to_VB7_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBR_to_VB8_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBR_to_VB9_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBR_to_VB10_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['AVBR_to_VB11_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['DB1_to_DB2_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['DB1_to_VB3_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.0005)
        parameters['DB2_to_DB3_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['DB2_to_VB4_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.0005)
        parameters['DB3_to_DB4_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['DB3_to_DD3_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.0005)
        parameters['DB3_to_VB6_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.0005)
        parameters['DB4_to_DD3_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.0005)
        parameters['DB4_to_DB5_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['DB5_to_DB6_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['DB6_to_DB7_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['DD1_to_DD2_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)
        parameters['DD1_to_VD2_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)
        parameters['DD1_to_VD3_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)
        parameters['DD2_to_DD3_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)
        parameters['DD2_to_VD3_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)
        parameters['DD2_to_VD4_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)
        parameters['DD2_to_VD5_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)

        parameters['DD3_to_DD4_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)
        parameters['DD4_to_DD5_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)
        parameters['DD5_to_DD6_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)
        parameters['DD6_to_VD11_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)
        parameters['DD6_to_VD12_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)
        parameters['DD6_to_VD13_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)
        parameters['VB1_to_VB2_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['VB2_to_VB3_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['VB2_to_VB4_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['VB3_to_VB4_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['VB4_to_VB5_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['VB5_to_VB6_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['VB6_to_VB7_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['VB7_to_VB8_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['VB8_to_VB9_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['VB9_to_VB10_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['VB10_to_VB11_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.004)
        parameters['VB10_to_VD11_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.0005)
        parameters['VB10_to_VD12_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.0005)
        parameters['VD1_to_VD2_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)
        parameters['VD2_to_VD2_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)
        parameters['VD2_to_VD3_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)
        parameters['VD3_to_VD4_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)
        parameters['VD4_to_VD5_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)
        parameters['VD5_to_VD6_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)
        parameters['VD6_to_VD7_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)
        parameters['VD7_to_VD8_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)
        parameters['VD8_to_VD9_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)
        parameters['VD9_to_VD10_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)
        parameters['VD10_to_VD11_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)
        parameters['VD11_to_VD12_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)
        parameters['VD12_to_VD13_elec_syn_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.05)

        parameters['AVBR_to_MVL16_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.012)
        parameters['DB1_to_MDL06_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB1_to_MDL08_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB1_to_MDL09_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB1_to_MDR08_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB1_to_MDR09_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB2_to_MDL09_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB2_to_MDL10_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB2_to_MDL11_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB2_to_MDL12_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB2_to_MDR09_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB2_to_MDR10_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB2_to_MDR11_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB3_to_MDL11_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB3_to_MDL12_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB3_to_MDL13_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB3_to_MDL14_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB3_to_MDR11_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB3_to_MDR12_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB3_to_MDR13_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB4_to_MDL13_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB4_to_MDL14_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB4_to_MDL15_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB4_to_MDL16_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB4_to_MDR13_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB4_to_MDR14_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB4_to_MDR15_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB4_to_MDR16_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB5_to_MDL14_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB5_to_MDL15_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB5_to_MDL16_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB5_to_MDL17_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB5_to_MDL18_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB5_to_MDL19_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB5_to_MDR14_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB5_to_MDR15_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB5_to_MDR16_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB5_to_MDR17_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB5_to_MDR18_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB5_to_MDR19_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB6_to_MDL16_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB6_to_MDL17_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB6_to_MDL18_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB6_to_MDL19_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB6_to_MDL20_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB6_to_MDL21_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB6_to_MDR16_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB6_to_MDR17_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB6_to_MDR18_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB6_to_MDR19_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB6_to_MDR20_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB6_to_MDR21_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB7_to_MDL19_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB7_to_MDL20_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB7_to_MDL21_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB7_to_MDL22_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB7_to_MDL23_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB7_to_MDL24_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB7_to_MDR19_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB7_to_MDR20_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB7_to_MDR21_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB7_to_MDR22_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['DB7_to_MDR23_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)

        parameters['DB7_to_MDR24_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB1_to_MVL07_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB1_to_MVR07_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB1_to_MVR09_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB2_to_MVL08_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB2_to_MVL09_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB2_to_MVL10_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB2_to_MVL11_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB2_to_MVR08_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB2_to_MVR10_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB2_to_MVR11_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB3_to_MVL10_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB3_to_MVL11_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB3_to_MVL12_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB3_to_MVL13_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB3_to_MVR10_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB3_to_MVR11_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB3_to_MVR12_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB3_to_MVR13_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB4_to_MVL12_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB4_to_MVL13_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB4_to_MVR12_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB4_to_MVR13_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB4_to_MVR14_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB5_to_MVL12_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB5_to_MVL13_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB5_to_MVL14_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB5_to_MVL15_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB5_to_MVR13_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB5_to_MVR14_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB5_to_MVR15_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB6_to_MVL15_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB6_to_MVL16_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB6_to_MVR14_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB6_to_MVR15_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB6_to_MVR16_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB7_to_MVL16_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB7_to_MVL17_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB7_to_MVL18_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB7_to_MVR16_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB7_to_MVR17_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB7_to_MVR18_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB8_to_MVL18_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB8_to_MVL19_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB8_to_MVL20_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB8_to_MVR18_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB8_to_MVR19_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB8_to_MVR20_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB9_to_MVL19_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB9_to_MVL20_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB9_to_MVL21_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB9_to_MVR19_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB9_to_MVR20_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB9_to_MVR21_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB10_to_MVL20_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB10_to_MVL21_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB10_to_MVL22_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB10_to_MVR20_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB10_to_MVR21_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB10_to_MVR22_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB11_to_MVL21_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB11_to_MVL22_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB11_to_MVL23_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB11_to_MVR21_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB11_to_MVR22_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)
        parameters['VB11_to_MVR23_exc_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(1.2)

        parameters['DD1_to_MDL06_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD1_to_MDL07_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD1_to_MDL08_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD1_to_MDL09_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD1_to_MDR06_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD1_to_MDR07_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD1_to_MDR08_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD1_to_MDR09_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD1_to_MDR10_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD2_to_MDL10_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD2_to_MDL11_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD2_to_MDL12_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD2_to_MDR10_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD2_to_MDR11_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD2_to_MDR12_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD3_to_MDL12_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD3_to_MDL13_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD3_to_MDL14_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD3_to_MDL15_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD3_to_MDR11_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD3_to_MDR12_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD3_to_MDR13_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD3_to_MDR14_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD3_to_MDR15_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD4_to_MDL16_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD4_to_MDL17_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD4_to_MDL18_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD4_to_MDR13_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD4_to_MDR14_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD4_to_MDR15_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD4_to_MDR16_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD4_to_MDR17_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD4_to_MDR18_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD5_to_MDL19_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD5_to_MDL20_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD5_to_MDL21_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD5_to_MDR19_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD5_to_MDR20_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD5_to_MDR21_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD6_to_MDL22_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD6_to_MDL23_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD6_to_MDL24_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD6_to_MDR22_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD6_to_MDR23_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['DD6_to_MDR24_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)

        parameters['VD1_to_MVL07_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD1_to_MVL08_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD2_to_MVL07_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD2_to_MVL08_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD2_to_MVL09_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD2_to_MVR07_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD2_to_MVR08_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD2_to_MVR09_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD3_to_MVL10_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD3_to_MVL11_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD3_to_MVR10_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD3_to_MVR11_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD4_to_MVL12_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD4_to_MVL13_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD4_to_MVR11_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD4_to_MVR12_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD4_to_MVR13_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD5_to_MVL12_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD5_to_MVL13_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD5_to_MVL14_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD5_to_MVR12_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD5_to_MVR13_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD6_to_MVL13_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD6_to_MVL14_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD6_to_MVL15_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD6_to_MVL16_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD6_to_MVR13_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD6_to_MVR14_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD6_to_MVR15_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD7_to_MVL14_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD7_to_MVL15_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD7_to_MVL16_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD7_to_MVR14_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD7_to_MVR15_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD7_to_MVR16_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD8_to_MVL15_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD8_to_MVL16_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD8_to_MVL17_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD8_to_MVR16_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD8_to_MVR17_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD8_to_MVR18_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD9_to_MVL17_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD9_to_MVL18_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD9_to_MVL19_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD9_to_MVR18_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD9_to_MVR19_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD9_to_MVR20_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD10_to_MVL18_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD10_to_MVL19_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD10_to_MVL20_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD10_to_MVR19_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD10_to_MVR20_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD10_to_MVR21_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD11_to_MVL19_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD11_to_MVL20_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD11_to_MVL21_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD11_to_MVR20_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD11_to_MVR21_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD11_to_MVR22_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD12_to_MVL20_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD12_to_MVL21_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD12_to_MVL22_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD12_to_MVR21_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD12_to_MVR22_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD12_to_MVR23_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD13_to_MVL21_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD13_to_MVL22_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD13_to_MVL23_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD13_to_MVR22_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)
        parameters['VD13_to_MVR23_inh_syn_conductance'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.8)

        parameters['DD1_to_MVL08_elec_syn_gbase'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.0005)
        parameters['VD2_to_MDL09_elec_syn_gbase'] = {'default_unit': 'nS'}
        min_constraints.append(0.0)
        max_constraints.append(0.0005)

        parameters['VB1_to_VB2_elec_syn_p_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.01)
        max_constraints.append(0.2)
        parameters['VB2_to_VB3_elec_syn_p_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.01)
        max_constraints.append(0.2)
        parameters['VB3_to_VB4_elec_syn_p_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.01)
        max_constraints.append(0.2)
        parameters['VB4_to_VB5_elec_syn_p_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.01)
        max_constraints.append(0.2)
        parameters['VB5_to_VB6_elec_syn_p_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.01)
        max_constraints.append(0.2)
        parameters['VB6_to_VB7_elec_syn_p_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.01)
        max_constraints.append(0.2)
        parameters['VB7_to_VB8_elec_syn_p_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.01)
        max_constraints.append(0.2)
        parameters['VB8_to_VB9_elec_syn_p_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.01)
        max_constraints.append(0.2)
        parameters['VB9_to_VB10_elec_syn_p_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.01)
        max_constraints.append(0.2)
        parameters['VB10_to_VB11_elec_syn_p_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.01)
        max_constraints.append(0.2)

        parameters['DB1_to_DB2_elec_syn_p_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.01)
        max_constraints.append(0.16)
        parameters['DB2_to_DB3_elec_syn_p_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.01)
        max_constraints.append(0.16)
        parameters['DB3_to_DB4_elec_syn_p_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.01)
        max_constraints.append(0.16)
        parameters['DB4_to_DB5_elec_syn_p_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.01)
        max_constraints.append(0.16)
        parameters['DB5_to_DB6_elec_syn_p_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.01)
        max_constraints.append(0.16)
        parameters['DB6_to_DB7_elec_syn_p_gbase_mirrored'] = {'default_unit': 'nS'}
        min_constraints.append(0.01)
        max_constraints.append(0.16)


        target_data = {}

        mdr = 'MDR'
        mvr = 'MVR'
        mvl = 'MVL'
        mdl = 'MDL'

        frequ = 1.7

        target_data['MDL06/0/GenericMuscleCell/v:first_spike_time'] = 240
        target_data['MDL06/0/GenericMuscleCell/v:mean_spike_frequency'] = frequ
        mdl_time = 324
        for i in range(8,24):
            target_data[
                '%s%s/0/GenericMuscleCell/v:first_spike_time' % (mdl, i + 1 if i > 8 else ("0%i" % (i + 1)))] = mdl_time
            target_data[
                '%s%s/0/GenericMuscleCell/v:mean_spike_frequency' % (mdl, i + 1 if i > 8 else ("0%i" % (i + 1)))] = frequ
            mdl_time += 42

        mdr_time = 324
        for i in range(8, 24):
            target_data[
                '%s%s/0/GenericMuscleCell/v:first_spike_time' % (mdl, i + 1 if i > 8 else ("0%i" % (i + 1)))] = mdr_time
            target_data[
                '%s%s/0/GenericMuscleCell/v:mean_spike_frequency' % (mdr, i + 1 if i > 8 else ("0%i" % (i + 1)))] = frequ
            mdr_time += 42


        mvl_time = 582
        for i in range(7, 24):
            target_data[
                '%s%s/0/GenericMuscleCell/v:first_spike_time' % (mvl, i + 1 if i > 8 else ("0%i" % (i + 1)))] = mvl_time
            mvl_time += 42
            target_data[
                '%s%s/0/GenericMuscleCell/v:mean_spike_frequency' % (mvl, i + 1 if i > 8 else ("0%i" % (i + 1)))] = frequ
        mvr_time = 582
        for i in range(7, 23):
            target_data[
                '%s%s/0/GenericMuscleCell/v:first_spike_time' % (mvr, i + 1 if i > 8 else ("0%i" % (i + 1)))] = mvr_time
            mvr_time += 42
            target_data[
                '%s%s/0/GenericMuscleCell/v:mean_spike_frequency' % (mvr, i + 1 if i > 8 else ("0%i" % (i + 1)))] = frequ


        weights = {}
        for target in target_data.keys():
            if target.endswith('frequency'):
                weights[target] = 1
            else:
                weights[target] = 1

        input_list = []

        """input_list.append(('MDL01', '0ms', '40ms', '3pA'))
        input_list.append(('MDL02', '15ms', '40ms', '3pA'))
        input_list.append(('MDL03', '30ms', '40ms', '3pA'))
        input_list.append(('MDL04', '45ms', '40ms', '3pA'))
        input_list.append(('MDL05', '60ms', '40ms', '3pA'))
        input_list.append(('MDL06', '75ms', '40ms', '3pA'))
        input_list.append(('MDL07', '90ms', '40ms', '3pA'))

        input_list.append(('MDR01', '0ms', '40ms', '3pA'))
        input_list.append(('MDR02', '15ms', '40ms', '3pA'))
        input_list.append(('MDR03', '30ms', '40ms', '3pA'))
        input_list.append(('MDR04', '45ms', '40ms', '3pA'))
        input_list.append(('MDR05', '60ms', '40ms', '3pA'))
        input_list.append(('MDR06', '75ms', '40ms', '3pA'))
        input_list.append(('MDR07', '90ms', '40ms', '3pA'))

        input_list.append(('MVL01', '180ms', '40ms', '3pA'))
        input_list.append(('MVL02', '195ms', '40ms', '3pA'))
        input_list.append(('MVL03', '210ms', '40ms', '3pA'))
        input_list.append(('MVL04', '225ms', '40ms', '3pA'))
        input_list.append(('MVL05', '240ms', '40ms', '3pA'))
        input_list.append(('MVL06', '255ms', '40ms', '3pA'))

        input_list.append(('MVR01', '180ms', '40ms', '3pA'))
        input_list.append(('MVR02', '195ms', '40ms', '3pA'))
        input_list.append(('MVR03', '210ms', '40ms', '3pA'))
        input_list.append(('MVR04', '225ms', '40ms', '3pA'))
        input_list.append(('MVR05', '240ms', '40ms', '3pA'))
        input_list.append(('MVR06', '255ms', '40ms', '3pA'))

        i = 320
        j = 470
        for start in range(1, 10):
            input_list.append(('MDL01', '%sms' % (i + 15), '40ms', '3pA'))
            input_list.append(('MDL02', '%sms' % (i + 30), '40ms', '3pA'))
            input_list.append(('MDL03', '%sms' % (i + 45), '40ms', '3pA'))
            input_list.append(('MDL04', '%sms' % (i + 60), '40ms', '3pA'))
            input_list.append(('MDL05', '%sms' % (i + 75), '40ms', '3pA'))
            input_list.append(('MDL06', '%sms' % (i + 90), '40ms', '3pA'))
            input_list.append(('MDL07', '%sms' % (i + 105), '40ms', '3pA'))
            input_list.append(('MDR01', '%sms' % (i + 15), '40ms', '3pA'))
            input_list.append(('MDR02', '%sms' % (i + 30), '40ms', '3pA'))
            input_list.append(('MDR03', '%sms' % (i + 45), '40ms', '3pA'))
            input_list.append(('MDR04', '%sms' % (i + 60), '40ms', '3pA'))
            input_list.append(('MDR05', '%sms' % (i + 75), '40ms', '3pA'))
            input_list.append(('MDR06', '%sms' % (i + 90), '40ms', '3pA'))
            input_list.append(('MDR07', '%sms' % (i + 105), '40ms', '3pA'))

            input_list.append(('MVL01', '%sms' % (j + 15), '40ms', '3pA'))
            input_list.append(('MVL02', '%sms' % (j + 30), '40ms', '3pA'))
            input_list.append(('MVL03', '%sms' % (j + 45), '40ms', '3pA'))
            input_list.append(('MVL04', '%sms' % (j + 60), '40ms', '3pA'))
            input_list.append(('MVL05', '%sms' % (j + 75), '40ms', '3pA'))
            input_list.append(('MVL06', '%sms' % (j + 90), '40ms', '3pA'))
            input_list.append(('MVR01', '%sms' % (j + 15), '40ms', '3pA'))
            input_list.append(('MVR02', '%sms' % (j + 30), '40ms', '3pA'))
            input_list.append(('MVR03', '%sms' % (j + 45), '40ms', '3pA'))
            input_list.append(('MVR04', '%sms' % (j + 60), '40ms', '3pA'))
            input_list.append(('MVR05', '%sms' % (j + 75), '40ms', '3pA'))
            input_list.append(('MVR06', '%sms' % (j + 90), '40ms', '3pA'))
            i += 300
            j += 300
        """

        input_list.append(('AVBL', '0ms', '%sms'%sim_time, '15pA'))
        input_list.append(('AVBR', '0ms', '%sms'%sim_time, '15pA'))
        input_list.append(('DB1', '200ms', '40ms', '5pA'))
        input_list.append(('VB1', '500ms', '40ms', '5pA'))

        i = 780
        j = 1080
        for start in range(1, 6):
            input_list.append(('DB1', '%sms' % i, '40ms', '5pA'))
            input_list.append(('VB1', '%sms' % j, '40ms', '5pA'))
            i += 580
            j += 580

        conns_to_exclude = [
            '^M..\d+-M..\d+_GJ$',
        ]

        param_overrides = {
            'mirrored_elec_conn_params': {

                #'^AVB._to_DB\d+\_GJ$_elec_syn_gbase': '0.001 nS',
                #'^AVB._to_VB\d+\_GJ$_elec_syn_gbase': '0.001 nS',

                #'^DB\d+_to_DB\d+\_GJ$_elec_syn_gbase': '0.001 nS',
                '^DB\d+_to_DB\d+\_GJ$_elec_syn_p_gbase': '0.08 nS',
                '^DB\d+_to_DB\d+\_GJ$_elec_syn_sigma': '0.2 per_mV',
                '^DB\d+_to_DB\d+\_GJ$_elec_syn_mu': '-20 mV',

                #'^VB\d+_to_VB\d+\_GJ$_elec_syn_gbase': '0.001 nS',
                '^VB\d+_to_VB\d+\_GJ$_elec_syn_p_gbase': '0.1 nS',
                '^VB\d+_to_VB\d+\_GJ$_elec_syn_sigma': '0.3 per_mV',
                '^VB\d+_to_VB\d+\_GJ$_elec_syn_mu': '-30 mV',

                # 'VB2_to_VB4_elec_syn_gbase': '0 nS',

                #'^DB\d+_to_VB\d+\_GJ$_elec_syn_gbase': '0 nS',
                #'^DB\d+_to_DD\d+\_GJ$_elec_syn_gbase': '0 nS',
                #'^VB\d+_to_VD\d+\_GJ$_elec_syn_gbase': '0 nS',

                #'DD1_to_MVL08_elec_syn_gbase': '0 nS',
                #'VD2_to_MDL09_elec_syn_gbase': '0 nS',
            },

            #'AVBR_to_DB4_exc_syn_conductance': '0 nS',

            #'VB4_to_VB5_exc_syn_conductance': '0 nS',
            #'AVBL_to_VB2_exc_syn_conductance': '0 nS',

            #'AVBR_to_VD3_exc_syn_conductance': '0 nS',

            #'^DB\d+_to_DD\d+$_exc_syn_conductance': '0.0001252 nS',
            #'^DD\d+_to_DB\d+$_inh_syn_conductance': '0.0001252 nS',
            #'^VB\d+_to_VD\d+$_exc_syn_conductance': '0.0001252 nS',
            #'^VD\d+_to_VB\d+$_inh_syn_conductance': '0.0001252 nS',

            #'DD1_to_VB2_inh_syn_conductance': '0 nS',

            'neuron_to_muscle_exc_syn_conductance': '0.3 nS',
            'neuron_to_muscle_exc_syn_vth': '37 mV',
            'neuron_to_muscle_inh_syn_conductance': '0.2 nS',
            'neuron_to_neuron_inh_syn_conductance': '0.1 nS',

            #'AVBR_to_MVL16_exc_syn_conductance': '0 nS',
            'ca_conc_decay_time_muscle': '85 ms',
            'ca_conc_rho_muscle': '0.000338919 mol_per_m_per_A_per_s',

        }

        simulator = 'jNeuroML_NEURON'
        run_optimisation('FW_Case1_',
                         'AVB_FW',
                         'C2',
                         parameters,
                         max_constraints,
                         min_constraints,
                         weights,
                         target_data,
                         config_package='notebooks.configs.AVB',
                         data_reader='UpdatedSpreadsheetDataReader',
                         sim_time=sim_time,
                         dt=0.05,
                         conns_to_exclude=conns_to_exclude,
                         param_overrides=param_overrides,
                         population_size=642,
                         max_evaluations=4000,
                         num_selected=361,
                         num_offspring=361,
                         mutation_rate=0.1,
                         num_elites=20,
                         seed=12347,
                         nogui=nogui,
                         simulator=simulator,
                         input_list=input_list,
                         num_local_procesors_to_use=19)
  
    elif '-icC1' in sys.argv or '-icC1one' in sys.argv:

        
        weights = {}
        target_data = {}
        
        for cell in ['ADAL']:
            var = '%s/0/GenericNeuronCell/v:mean_spike_frequency'%cell
            weights[var] = 1
            target_data[var] = 4
            var = '%s/0/GenericNeuronCell/v:max_peak_no'%cell
            weights[var] = 1
            target_data[var] = 4
            
        if '-icC1' in sys.argv:

            simulator  = 'jNeuroML_NEURON'
            run_optimisation('Test',
                             'IClamp',
                             'C1',
                             parameters_C_based,
                             max_constraints0,
                             min_constraints0,
                             weights,
                             target_data,
                             sim_time = 1000,
                             dt = 0.1,
                             population_size =  200,
                             max_evaluations =  500,
                             num_selected =     20,
                             num_offspring =    20,
                             mutation_rate =    0.9,
                             num_elites =       4,
                             seed =             12347,
                             nogui =            nogui,
                             simulator = simulator,
                             num_local_procesors_to_use = 10)
        else:

            sim_time = 1000
            simulator  = 'jNeuroML_NEURON'
            
            my_controller = C302Controller('TestIClamp', 'C1', 'IClamp', sim_time, 0.1, simulator = simulator)

            sim_var = OrderedDict([('muscle_leak_cond_density',0.1),
                                   ('muscle_k_slow_cond_density',0.5),
                                   ('muscle_k_fast_cond_density',0.05),
                                   ('muscle_ca_boyle_cond_density',0.5)])
                  
            example_run_t, example_run_v = my_controller.run_individual(sim_var, show=True)

            print("Have run individual instance...")

            peak_threshold = -10

            analysis_var = {'peak_delta':     0,
                            'baseline':       0,
                            'dvdt_threshold': 0, 
                            'peak_threshold': peak_threshold}

            example_run_analysis=analysis.NetworkAnalysis(example_run_v,
                                                       example_run_t,
                                                       analysis_var,
                                                       start_analysis=0,
                                                       end_analysis=sim_time)

            analysis = example_run_analysis.analyse()

            prpr.pprint(analysis)

            analysis = example_run_analysis.analyse(weights.keys())

            prpr.pprint(analysis)

    elif '-phar' in sys.argv:

        parameters = ['neuron_to_muscle_chem_exc_syn_gbase',
                                  'chem_exc_syn_decay',
                                  'neuron_to_muscle_elec_syn_gbase']

        #above parameters will not be modified outside these bounds:
        min_constraints = [0.05, 3, 0.01]
        max_constraints = [1,    50, 1]

        M5_max_peak = 'M5/0/GenericCell/v:max_peak_no'
        I6_max_peak = 'I6/0/GenericCell/v:max_peak_no'
        MCL_max_peak = 'MCL/0/GenericCell/v:max_peak_no'


        weights = {M5_max_peak: 1,
                   MCL_max_peak: 1,
                   I6_max_peak: 1}


        target_data = {M5_max_peak:  8,
                       MCL_max_peak: 8,
                       I6_max_peak: 8}



        run_optimisation('Test',
                         'Pharyngeal',
                         'C',
                         parameters,
                         max_constraints,
                         min_constraints,
                         weights,
                         target_data,
                         population_size =  10,
                         max_evaluations =  20,
                         num_selected =     10,
                         num_offspring =    20,
                         mutation_rate =    0.9,
                         num_elites =       1,
                         nogui =            nogui,
                         num_local_procesors_to_use = 10)


    elif '-simple' in sys.argv or '-simpleN' in sys.argv:


        parameters = ['unphysiological_offset_current']

        #above parameters will not be modified outside these bounds:
        min_constraints = [0.0]
        max_constraints = [5]


        ADAL_max_peak = 'MDR01/0/GenericMuscleCell/v:max_peak_no'

        weights = {ADAL_max_peak: 1}

        target_data = {ADAL_max_peak:  8}

        simulator  = 'jNeuroML_NEURON' if '-simpleN' in sys.argv else 'jNeuroML'

        scale = 3
        run_optimisation('Test',
                         'IClamp',
                         'C0',
                         parameters,
                         max_constraints,
                         min_constraints,
                         weights,
                         target_data,
                         sim_time = 1000,
                         population_size =  10*scale,
                         max_evaluations =  20*scale,
                         num_selected =     5*scale,
                         num_offspring =    5*scale,
                         mutation_rate =    0.9,
                         num_elites =       1,
                         simulator =        simulator,
                         nogui =            nogui,
                         num_local_procesors_to_use = 10)

    else:

        level = 'B'
        config = 'Muscles'
        sim_time = 300

        my_controller = C302Controller('Test', level, config, sim_time, 0.1)

        sim_var = OrderedDict([('neuron_to_muscle_chem_exc_syn_gbase',0.5),
                  ('chem_exc_syn_decay',10),
                  ('neuron_to_muscle_chem_inh_syn_gbase',0.5),
                  ('chem_inh_syn_decay',40),
                  ('unphysiological_offset_current',0.38)])

        weights = {'PVCL[0]/v:max_peak_no': 3}


        example_run_t, example_run_v = my_controller.run_individual(sim_var, show=True)

        print("Have run individual instance...")

        peak_threshold = -31 if level.startswith('A') or level.startswith('B') else -20

        analysis_var = {'peak_delta':     0,
                        'baseline':       0,
                        'dvdt_threshold': 0, 
                        'peak_threshold': peak_threshold}

        example_run_analysis=analysis.NetworkAnalysis(example_run_v,
                                                   example_run_t,
                                                   analysis_var,
                                                   start_analysis=0,
                                                   end_analysis=sim_time)

        analysis = example_run_analysis.analyse()

        prpr.pprint(analysis)

        analysis = example_run_analysis.analyse(weights.keys())

        prpr.pprint(analysis)



