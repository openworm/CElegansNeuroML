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
                 targets=None):

        super(EnhancedNetworkEvaluator, self).__init__(analysis_start_time,
                                                       controller,
                                                       analysis_end_time,
                                                       parameters,
                                                       analysis_var,
                                                       weights,
                                                       targets)

        self.analysis_start_time=analysis_start_time
        self.analysis_end_time=analysis_end_time
        self.analysis_var=analysis_var
        self.targets=targets



    def evaluate(self,candidates,args):

        print("\n>>>>>  Evaluating: ")
        for cand in candidates: print(">>>>>       %s"%cand)

        simulations_data = self.controller.run(candidates,self.parameters)

        fitness = []

        for data in simulations_data:

            times = data[0]
            volts = data[1]

            data_analysis=c302Analysis.Data_Analyser(volts,
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

            print('Fitness: %s\n'%fitness_value)

        return fitness
