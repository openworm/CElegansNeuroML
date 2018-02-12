import math

from neurotune import evaluators
import c302Analysis

class EnhancedNetworkEvaluator(evaluators.NetworkEvaluator):

    def __init__(self,
                 analysis_start_time,
                 controller,
                 analysis_end_time,
                 parameters,
                 analysis_var,
                 weights,
                 targets=None,
                 job_server=None):

        super(EnhancedNetworkEvaluator, self).__init__(analysis_start_time,
                                                       controller,
                                                       analysis_end_time,
                                                       parameters,
                                                       analysis_var,
                                                       weights,
                                                       targets)

        self.analysis_start_time = analysis_start_time
        self.analysis_end_time = analysis_end_time
        self.analysis_var = analysis_var
        self.targets = targets
        self.job_server = job_server

    def evaluate(self, candidates, args):

        print("\n>>>>>  Evaluating: ")
        for cand in candidates:
            print(">>>>>       %s" % cand)

        simulations_data = self.controller.run(candidates, self.parameters)

        fitness = []

        #job_server = pp.Server(ppservers=(), secret="password")

        # TODO: do in parallel?

        jobs = []

        for data in simulations_data:

            if self.job_server:
                vars = (data,
                        self.analysis_var,
                        self.analysis_start_time,
                        self.analysis_end_time,
                        self.targets,
                        self.weights)
                job = self.job_server.submit(do_evaluation, vars, modules=('math', 'c302Analysis', 'from neurotune import evaluators', ))
                jobs.append(job)
            else:
                fitness_value = do_evaluation(data,
                              self.analysis_var,
                              self.analysis_start_time,
                              self.analysis_end_time,
                              self.targets,
                              self.weights)

                fitness.append(fitness_value)
                print('Fitness: %s\n' % fitness_value)

            """times = data[0]
            volts = data[1]

            data_analysis = c302Analysis.Data_Analyser(volts,
                                                       times,
                                                       self.analysis_var,
                                                       start_analysis=self.analysis_start_time,
                                                       end_analysis=self.analysis_end_time)

            data_analysis.analyse(self.targets)

            fitness_value = self.evaluate_fitness(data_analysis,
                                                  self.targets,
                                                  self.weights,
                                                  cost_function=evaluators.normalised_cost_function)
            fitness.append(fitness_value)

            print('Fitness: %s\n' % fitness_value)"""


        del simulations_data[:]

        for job in jobs:
            fitness_value = job()
            fitness.append(fitness_value)
            print('Fitness: %s\n' % fitness_value)

        #self.job_server.destroy()

        return fitness



def do_evaluation(data, analysis_var, analysis_start_time, analysis_end_time, targets, weights,):
    times = data[0]
    volts = data[1]

    #import c302Analysis
    #from neurotune import evaluators

    data_analysis = c302Analysis.Data_Analyser(volts,
                                               times,
                                               analysis_var,
                                               start_analysis=analysis_start_time,
                                               end_analysis=analysis_end_time)

    data_analysis.analyse(targets)

    #import math

    fitness = 0

    for target in targets.keys():

        target_value = targets[target]

        if weights == None:
            target_weight = 1
        else:
            if target in weights.keys():
                target_weight = weights[target]
            else:
                target_weight = 0  # If it's not mentioned assunme weight = 0!

        if target_weight > 0:
            inc = target_weight  # default...
            if data_analysis.analysis_results.has_key(target):
                value = data_analysis.analysis_results[target]
                if not math.isnan(value):
                    # let function pick Q automatically
                    inc = target_weight * evaluators.normalised_cost_function(value, target_value)
                else:
                    value = '<<infinite value!>>'
                    inc = target_weight
            else:
                value = '<<cannot be calculated! (only: %s; peak_threshold: %s)>>' % (
                    data_analysis.analysis_results.keys(), analysis_var['peak_threshold'])

            fitness += inc

            print('Target %s (weight %s): target val: %s, actual: %s, fitness increment: %s' % (
                target, target_weight, target_value, value, inc))





    return fitness


