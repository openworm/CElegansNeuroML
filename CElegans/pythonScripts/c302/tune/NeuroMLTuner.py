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
import os.path
import time

import pprint

from collections import OrderedDict
pp = pprint.PrettyPrinter(indent=4)



from NeuroMLController import NeuroMLController


def run_optimisation(prefix,
                     neuroml_file, 
                     target, 
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
                     nogui =               False):  
                         
    ref = prefix
    
    run_dir = "NT_%s_%s"%(ref, time.ctime().replace(' ','_' ).replace(':','.' ))
    os.mkdir(run_dir)

    my_controller = NeuroMLController(ref, neuroml_file, target, sim_time, dt, simulator = simulator, generate_dir=run_dir)

    peak_threshold = 0

    analysis_var = {'peak_delta':     0,
                    'baseline':       0,
                    'dvdt_threshold': 0, 
                    'peak_threshold': peak_threshold}

    sim_var = OrderedDict()



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
    info = "Ran %s evaluations (pop: %s) in %f seconds (%f mins)\n\n"%(max_evaluations, population_size, secs, secs/60.0)
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
    report+="FITTEST: %s\n\n"%sim_var
    
    print(report)
    
    reportj['fitness']=fitness
    reportj['fittest vars']=sim_var
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
    
    reportj['sim_time']=sim_time
    reportj['dt']=dt
    
    
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
        

    if '-net' in sys.argv:

        ''''''
  


    else:

        parameters = ['cell:hhcell/channelDensity:naChans/mS_per_cm2',
                      'cell:hhcell/channelDensity:kChans/mS_per_cm2']

        #above parameters will not be modified outside these bounds:
        min_constraints = [50,   10]
        max_constraints = [200, 60]


        max_peak_no = 'hhpop[0]/v:max_peak_no'

        weights = {max_peak_no: 1}

        target_data = {max_peak_no:  30}

        simulator  = 'jNeuroML'
        
        run_optimisation('TestHH', 
                         'tune/test_data/HHCellNetwork.net.nml',
                         'HHCellNetwork',
                         parameters,
                         max_constraints,
                         min_constraints,
                         weights,
                         target_data,
                         sim_time = 700,
                         population_size =  10,
                         max_evaluations =  30,
                         num_selected =     5,
                         num_offspring =    5,
                         mutation_rate =    0.9,
                         num_elites =       1,
                         simulator =        simulator,
                         nogui =            nogui)



