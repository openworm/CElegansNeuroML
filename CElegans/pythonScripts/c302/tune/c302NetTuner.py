'''

    Still under developemnt!!

    Subject to change without notice!!

'''

from neurotune import optimizers
from neurotune import evaluators
from neurotune import utils
from matplotlib import pyplot as plt
from pyelectro import analysis

import sys
import os
import shutil
import os.path
import time

import pprint

from collections import OrderedDict
pp = pprint.PrettyPrinter(indent=4)


if not os.path.isfile('c302.py'):
    print('This script should be run from dir: CElegansNeuroML/CElegans/pythonScripts/c302')
    exit()

sys.path.append(".")


from C302Controller import C302Controller


def scale(scale, number, min=1):
    return max(min, int(scale*number))

def run_optimisation(prefix,
                     config,
                     level,
                     parameters,
                     max_constraints,
                     min_constraints,
                     weights,
                     target_data,
                     sim_time =            500,
                     dt =                  0.05,
                     analysis_start_time = 0,
                     population_size =     20,
                     max_evaluations =     20,
                     num_selected =        10,
                     num_offspring =       20,
                     mutation_rate =       0.5,
                     num_elites =          1,
                     seed =                12345,
                     simulator =           'jNeuroML',
                     nogui =               False,
                     num_local_procesors_to_use = 1):  
                         
    ref = prefix+config
    
    run_dir = "NT_%s_%s"%(ref, time.ctime().replace(' ','_' ).replace(':','.' ))
    os.mkdir(run_dir)

    my_controller = C302Controller(ref, 
                                   level, 
                                   config, 
                                   sim_time, 
                                   dt, 
                                   simulator = simulator, 
                                   generate_dir=run_dir,
                                   num_local_procesors_to_use = num_local_procesors_to_use)

    peak_threshold = -31 if level is 'A' or level is 'B' else (-20 if level is 'C1' else 0)

    analysis_var = {'peak_delta':     0,
                    'baseline':       0,
                    'dvdt_threshold': 0, 
                    'peak_threshold': peak_threshold}

    data = ref+'.dat'

    sim_var = OrderedDict()
    for i in range(len(parameters)):
        sim_var[parameters[i]] = max_constraints[i]/2 + min_constraints[i]/2



    #make an evaluator, using automatic target evaluation:
    my_evaluator=evaluators.NetworkEvaluator(controller=my_controller,
                                            analysis_start_time=analysis_start_time,
                                            analysis_end_time=sim_time,
                                            parameters=parameters,
                                            analysis_var=analysis_var,
                                            weights=weights,
                                            targets=target_data)


    #make an optimizer
    my_optimizer = optimizers.CustomOptimizerA(max_constraints,
                                             min_constraints,
                                             my_evaluator,
                                             population_size=population_size,
                                             max_evaluations=max_evaluations,
                                             num_selected=num_selected,
                                             num_offspring=num_offspring,
                                             num_elites=num_elites,
                                             mutation_rate=mutation_rate,
                                             seeds=None,
                                             verbose=False)

    start = time.time()
    #run the optimizer
    best_candidate, fitness = my_optimizer.optimize(do_plot=False, 
                                                    seed=seed,
                                                    summary_dir = run_dir)

    secs = time.time()-start
    
    reportj = {}
    info = "Ran %s evaluations (pop: %s) in %f seconds (%f mins total; %fs per eval)\n\n"%(max_evaluations, population_size, secs, secs/60.0, (secs/max_evaluations))
    report = "----------------------------------------------------\n\n"+ info
             
             
    reportj['comment'] = info
    reportj['time'] = secs

    for key,value in zip(parameters,best_candidate):
        sim_var[key]=value


    best_candidate_t, best_candidate_v = my_controller.run_individual(sim_var,show=False)

    best_candidate_analysis = analysis.NetworkAnalysis(best_candidate_v,
                                               best_candidate_t,
                                               analysis_var,
                                               start_analysis=analysis_start_time,
                                               end_analysis=sim_time)

    best_cand_analysis_full = best_candidate_analysis.analyse()
    best_cand_analysis = best_candidate_analysis.analyse(weights.keys())

    report+="---------- Best candidate ------------------------------------------\n"
    
    report+=pp.pformat(best_cand_analysis_full)+"\n"
    report+=pp.pformat(best_cand_analysis)+"\n\n"
    report+="FITNESS: %f\n\n"%fitness
    
    print(report)
    
    reportj['fitness']=fitness
    reportj['fittest vars']=dict(sim_var)
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
    report_file.write(pp.pformat(reportj))
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
        for wref in weights.keys():
            ref = wref.split(':')[0]
            if not ref in added:
                added.append(ref)
                best_candidate_plot = plt.plot(best_candidate_t,best_candidate_v[ref], label="%s - %i evaluations"%(ref,max_evaluations))

        plt.legend()

        plt.ylim(-80.0,80.0)
        plt.xlim(0.0,sim_time)
        plt.title("Models")
        plt.xlabel("Time (ms)")
        plt.ylabel("Membrane potential(mV)")

        plt.show()

        utils.plot_generation_evolution(sim_var.keys(), individuals_file_name = '%s/ga_individuals.csv'%run_dir)




if __name__ == '__main__':
    
    nogui = '-nogui' in sys.argv
        

    if '-musc' in sys.argv or '-muscone' in sys.argv:

        parameters = ['leak_cond_density',
                      'k_slow_cond_density',
                      'k_fast_cond_density',
                      'ca_boyle_cond_density',
                      'exc_syn_conductance',
                      'inh_syn_conductance',
                      'elec_syn_gbase',
                      'unphysiological_offset_current']

        #above parameters will not be modified outside these bounds:
        min_constraints = [.005,.1, 0.005, .1, .01, .01, 0.0005, 1]
        max_constraints = [.2,  2, 0.1,   2, .1, .1, 0.01,  8]
        
        weights = {}
        target_data = {}
        
        
        for cell in ['DB3','VB3','DB4','VB4','PVCL']:
            var = '%s/0/GenericCell/v:mean_spike_frequency'%cell
            weights[var] = 1
            target_data[var] = 4
            

        simulator  = 'jNeuroML_NEURON'
        
        if '-musc' in sys.argv:
            
            scalem = 1
            run_optimisation('Test',
                             'Muscles',
                             'C1',
                             parameters,
                             max_constraints,
                             min_constraints,
                             weights,
                             target_data,
                             sim_time = 500,
                             dt = 0.1,
                             population_size =  scale(scalem,100),
                             max_evaluations =  scale(scalem,500),
                             num_selected =     scale(scalem,20),
                             num_offspring =    scale(scalem,20),
                             mutation_rate =    0.9,
                             num_elites =       scale(scalem,3),
                             nogui =            nogui,
                             simulator = simulator,
                             num_local_procesors_to_use =10)
        else:
            
            sim_time = 1000
            simulator  = 'jNeuroML_NEURON'
            
            my_controller = C302Controller('TestOsc', 'C1', 'Muscles', sim_time, 0.1, simulator = simulator)

            #test = [0.030982235821054638, 0.7380672812995235, 0.07252703867293844, 0.8087106170838071, 0.045423417312661474, 0.011449079144697817, 0.0049614426482976716, 2.361816408316808]
            sim_var = OrderedDict({   'ca_boyle_cond_density': 2,
                        'elec_syn_gbase': 0.0005,
                        'exc_syn_conductance': 0.1,
                        'inh_syn_conductance': 0.1,
                        'k_fast_cond_density': 0.1,
                        'k_slow_cond_density': 2,
                        'leak_cond_density': 0.005,
                        'unphysiological_offset_current': 7.083369886548855})
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

            pp.pprint(analysis)

            analysis = example_run_analysis.analyse(weights.keys())

            pp.pprint(analysis)
                         
    elif '-osc' in sys.argv:

        parameters = ['chem_exc_syn_gbase',
                      'chem_exc_syn_decay',
                      'chem_inh_syn_gbase',
                      'chem_inh_syn_decay',
                      'elec_syn_gbase',
                      'unphysiological_offset_current']

        #above parameters will not be modified outside these bounds:
        min_constraints = [0.001, 3,   0.001, 3,    0.01,   2]
        max_constraints = [0.02,  40, 0.02,   100,  0.2,    5]
        
        weights = {}
        target_data = {}
        
        
        for cell in ['DB3','VB3','DB4','VB4']:
            var = '%s/0/generic_iaf_cell/v:mean_spike_frequency'%cell
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
                         mutation_rate =    0.1,
                         num_elites =       1,
                         seed =             123477,
                         nogui =            nogui,
                         num_local_procesors_to_use =10)
                         
    elif '-oscC1' in sys.argv or '-oscC1one' in sys.argv:

        parameters = ['leak_cond_density',
                      'k_slow_cond_density',
                      'k_fast_cond_density',
                      'ca_boyle_cond_density',
                      'exc_syn_conductance',
                      'inh_syn_conductance',
                      'elec_syn_gbase',
                      'unphysiological_offset_current']

        #above parameters will not be modified outside these bounds:
        min_constraints = [.01,.1, 0.01, .1, .01, .01, 0.0005, 1]
        max_constraints = [.2,  1, 0.1,   1, .05, .05, 0.005,  6]
        
        weights = {}
        target_data = {}
        
        
        for cell in ['DB3','VB3','DB4','VB4','PVCL']:
            var = '%s/0/GenericCell/v:mean_spike_frequency'%cell
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
                             population_size =  1000,
                             max_evaluations =  5000,
                             num_selected =     100,
                             num_offspring =    100,
                             mutation_rate =    0.1,
                             num_elites =       6,
                             seed =             123477,
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

            pp.pprint(analysis)

            analysis = example_run_analysis.analyse(weights.keys())

            pp.pprint(analysis)
  
    elif '-icC1' in sys.argv or '-icC1one' in sys.argv:

        '''
        self.add_bioparameter("leak_cond_density", "0.1 mS_per_cm2", "BlindGuess", "0.1")
        self.add_bioparameter("k_slow_cond_density", "0.5 mS_per_cm2", "BlindGuess", "0.1")
        self.add_bioparameter("k_fast_cond_density", "0.05 mS_per_cm2", "BlindGuess", "0.1")
        self.add_bioparameter("ca_boyle_cond_density", "0.5 mS_per_cm2", "BlindGuess", "0.1")'''
        
        parameters = ['leak_cond_density',
                      'k_slow_cond_density',
                      'k_fast_cond_density',
                      'ca_boyle_cond_density',
                      'unphysiological_offset_current']

        #above parameters will not be modified outside these bounds:
        min_constraints = [.01,.1, 0.01, .1, 3]
        max_constraints = [.2,  1, 0.1,   1, 8]
        
        weights = {}
        target_data = {}
        
        for cell in ['ADAL']:
            var = '%s/0/GenericCell/v:mean_spike_frequency'%cell
            weights[var] = 1
            target_data[var] = 4
            
        if '-icC1' in sys.argv:

            simulator  = 'jNeuroML_NEURON'
            run_optimisation('Test',
                             'IClamp',
                             'C1',
                             parameters,
                             max_constraints,
                             min_constraints,
                             weights,
                             target_data,
                             sim_time = 1000,
                             dt = 0.1,
                             population_size =  50,
                             max_evaluations =  120,
                             num_selected =     10,
                             num_offspring =    15,
                             mutation_rate =    0.1,
                             num_elites =       1,
                             seed =             123477,
                             nogui =            nogui,
                             simulator = simulator)
        else:
               
            sim_time = 1000
            simulator  = 'jNeuroML_NEURON'
            
            my_controller = C302Controller('TestOsc', 'C1', 'IClamp', sim_time, 0.1, simulator = simulator)

            sim_var = OrderedDict([('leak_cond_density',0.1),
                                   ('k_slow_cond_density',0.5),
                                   ('k_fast_cond_density',0.05),
                                   ('ca_boyle_cond_density',0.5)])
                  
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

            pp.pprint(analysis)

            analysis = example_run_analysis.analyse(weights.keys())

            pp.pprint(analysis)

    elif '-phar' in sys.argv:

        parameters = ['chem_exc_syn_gbase',
                                  'chem_exc_syn_decay',
                                  'elec_syn_gbase']

        #above parameters will not be modified outside these bounds:
        min_constraints = [0.05, 3, 0.01]
        max_constraints = [1,    50, 1]

        M5_max_peak = 'M5[0]/v:max_peak_no'
        I6_max_peak = 'I6[0]/v:max_peak_no'
        MCL_max_peak = 'MCL[0]/v:max_peak_no'


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
                         mutation_rate =    0.5,
                         num_elites =       1,
                         nogui =            nogui)


    elif '-simple' in sys.argv or '-simpleN' in sys.argv:


        parameters = ['unphysiological_offset_current']

        #above parameters will not be modified outside these bounds:
        min_constraints = [0.20]
        max_constraints = [0.35]


        ADAL_max_peak = 'ADAL[0]/v:max_peak_no'

        weights = {ADAL_max_peak: 1}

        target_data = {ADAL_max_peak:  8}

        simulator  = 'jNeuroML_NEURON' if '-simpleN' in sys.argv else 'jNeuroML'

        run_optimisation('Test',
                         'IClamp',
                         'C',
                         parameters,
                         max_constraints,
                         min_constraints,
                         weights,
                         target_data,
                         sim_time = 1000,
                         population_size =  10,
                         max_evaluations =  20,
                         num_selected =     5,
                         num_offspring =    5,
                         mutation_rate =    0.1,
                         num_elites =       1,
                         simulator =        simulator,
                         nogui =            nogui)

    else:

        level = 'B'
        config = 'Muscles'
        sim_time = 300

        my_controller = C302Controller('Test', level, config, sim_time, 0.1)

        sim_var = OrderedDict([('chem_exc_syn_gbase',0.5),
                  ('chem_exc_syn_decay',10),
                  ('chem_inh_syn_gbase',0.5),
                  ('chem_inh_syn_decay',40),
                  ('unphysiological_offset_current',0.38)])

        weights = {'PVCL[0]/v:max_peak_no': 3}


        example_run_t, example_run_v = my_controller.run_individual(sim_var, show=True)

        print("Have run individual instance...")

        peak_threshold = -31 if level is 'A' or level is 'B' else 0

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

        pp.pprint(analysis)

        analysis = example_run_analysis.analyse(weights.keys())

        pp.pprint(analysis)



