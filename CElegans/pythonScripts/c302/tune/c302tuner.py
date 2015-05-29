'''

    Still under developemnt!!
    
    Subject to change without notice!!
    
'''


from neurotune import optimizers
from neurotune import evaluators
from neurotune import utils
from matplotlib import pyplot as plt
from pyelectro import analysis

import numpy as np
import sys
import os.path
import time



if not os.path.isfile('c302.py'):
    print('This script should be run from dir: CElegansNeuroML/CElegans/pythonScripts/c302')
    exit()
        
sys.path.append(".")

from C302Simulation import C302Simulation

from C302Controller import C302Controller


def get_target_muscle_cell_data(analysis_var, analysis_start_time, sim_time):
        # Based on: https://github.com/openworm/muscle_model/blob/master/pyramidal_implementation/data_analysis.py
        data_fname = "tune/redacted_data.txt"
        data_dt = 0.0002

        #load the voltage:
        file=open(data_fname)

        #make voltage into a numpy array in mV:
        v = np.array([float(i) for i in file.readlines()])*1000

        t_init = 0.0
        t_final = len(v)*data_dt

        t = np.linspace(t_init,t_final,len(v))*1000


        analysis_i=analysis.IClampAnalysis(v,t,analysis_var,
                                        start_analysis=analysis_start_time,
                                        end_analysis=sim_time,
                                        smooth_data=True,
                                        show_smoothed_data=False,
                                        smoothing_window_len=33)

        target_data = analysis_i.analyse()
        
        return target_data, v, t

if __name__ == '__main__':
    
    sim_time = 1000
    analysis_start_time = 0
    dt = 0.05
    
    my_controller = C302Controller()

    parameters = ['leak_cond_density',
                  'k_slow_cond_density',
	              'k_fast_cond_density',
                  'ca_boyle_cond_density', 
                  'specific_capacitance',
                  'leak_erev',
                  'k_slow_erev',
                  'k_fast_erev',
                  'ca_boyle_erev']

    #above parameters will not be modified outside these bounds:
    min_constraints = [0.0001, 0.01,   0.01,   0.01, 0.1, -60, -70, -70, 30]
    max_constraints = [0.2,    1,      1,      1,    3,   -40, -50, -50, 50]

    analysis_var={'peak_delta':0,'baseline':0,'dvdt_threshold':0, 'peak_threshold':0}

             
    weights = {'peak_linear_gradient': 0,
               'average_minimum': 0.5, 
               'spike_frequency_adaptation': 0.0, 
               'trough_phase_adaptation': 0.0, 
               'mean_spike_frequency': 10.0, 
               'average_maximum': 5.0, 
               'trough_decay_exponent': 0.0, 
               'interspike_time_covar': 0.0, 
               'min_peak_no': 0.0, 
               'spike_width_adaptation': 0.0, 
               'max_peak_no': 50.0, 
               'first_spike_time': 10.0, 
               'peak_decay_exponent': 0.0,
               'spike_broadening': 0.0}

    data = 'SimpleTest.dat'


    sim_var = {}
    for i in range(len(parameters)):
        sim_var[parameters[i]] = max_constraints[i]/2 - min_constraints[i]/2
    print(sim_var)
        

    if len(sys.argv) == 2 and sys.argv[1] == '-sim':
        sim = C302Simulation('SimpleTest', 'C')
        sim.go()
        sim.show()
        
    elif len(sys.argv) == 2 and sys.argv[1] == '-opt':
        
        target_data, v, t = get_target_muscle_cell_data(analysis_var, analysis_start_time, sim_time)

        #make an evaluator, using automatic target evaluation:
        my_evaluator=evaluators.IClampEvaluator(controller=my_controller,
                                                analysis_start_time=analysis_start_time,
                                                analysis_end_time=sim_time,
                                                target_data_path=data,
                                                parameters=parameters,
                                                analysis_var=analysis_var,
                                                weights=weights,
                                                targets=target_data,
                                                automatic=False)

        population_size =  30
        max_evaluations =  150
        num_selected =     15
        num_offspring =    10
        mutation_rate =    0.5
        num_elites =       1
        
        #make an optimizer
        my_optimizer=optimizers.CustomOptimizerA(max_constraints,
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
                                                 
        start = time.time()
        #run the optimizer
        best_candidate = my_optimizer.optimize(do_plot=True, seed=1234567)
        
        secs = time.time()-start
        print("----------------------------------------------------\n\nRan %s evaluations in %f seconds (%f mins)\n"%(max_evaluations, secs, secs/60.0))
        
        for key,value in zip(parameters,best_candidate):
            sim_var[key]=value
        best_candidate_t,best_candidate_v = my_controller.run_individual(sim_var,show=False)
        
        best_candidate_analysis=analysis.IClampAnalysis(best_candidate_v,
                                                   best_candidate_t,
                                                   analysis_var,
                                                   start_analysis=analysis_start_time,
                                                   end_analysis=sim_time,
                                                   smooth_data=False,
                                                   show_smoothed_data=False)
                                                   
        best_candidate_analysis.analyse()
                                                   
        best_candidate_analysis.evaluate_fitness(target_data, weights)                                           
        
        data_plot = plt.plot(np.array(t),np.array(v))
        best_candidate_plot = plt.plot(np.array(best_candidate_t),np.array(best_candidate_v))

        plt.legend([data_plot,best_candidate_plot],
                   ["Original data","Best model - %i evaluations"%max_evaluations])

        plt.ylim(-80.0,80.0)
        plt.xlim(0.0,1000.0)
        plt.title("Models optimized from data")
        plt.xlabel("Time (ms)")
        plt.ylabel("Membrane potential(mV)")
        plt.savefig("data_vs_candidate.png",bbox_inches='tight',format='png')
        plt.show()

        utils.plot_generation_evolution(sim_var.keys())

    else:


        target_data, v, t = get_target_muscle_cell_data(analysis_var, analysis_start_time, sim_time)
        print("target_data: %s"%target_data)
        
        example_run_t, example_run_v = my_controller.run_individual(sim_var, show=False)

        print("Have run individual instance...")


        example_run_analysis=analysis.IClampAnalysis(example_run_v,
                                                   example_run_t,
                                                   analysis_var,
                                                   start_analysis=analysis_start_time,
                                                   end_analysis=sim_time,
                                                   smooth_data=False,
                                                   show_smoothed_data=True)

        print(example_run_analysis.max_min_dictionary)



