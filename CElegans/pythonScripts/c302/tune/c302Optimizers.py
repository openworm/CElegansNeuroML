import os
from neurotune.optimizers import __Optimizer
from inspyred import ec
from inspyred.ec import observers
from inspyred.ec import terminators
from inspyred.ec import selectors
from inspyred.ec import replacers
from inspyred.ec import variators
from random import Random
from time import time
import logging

class CustomOptimizerA(__Optimizer):
    def __init__(self, max_constraints,
                 min_constraints,
                 evaluator,
                 mutation_rate=0.2,
                 max_evaluations=100,
                 population_size=10,
                 num_selected=None,
                 tourn_size=2,
                 num_elites=1,
                 maximize=False,
                 num_offspring=None,
                 seeds=[],
                 verbose=False,
                 max_generation_without_improvement=False):

        super(CustomOptimizerA, self).__init__(max_constraints, min_constraints,
                                               evaluator, mutation_rate,
                                               maximize, seeds, population_size)

        self.max_evaluations = max_evaluations
        self.tourn_size = tourn_size
        self.num_elites = num_elites
        self.mutation_rate = mutation_rate
        self.verbose = verbose

        if num_selected == None:
            self.num_selected = population_size
        else:
            self.num_selected = num_selected
        if num_offspring == None:
            self.num_offspring = population_size - self.num_selected
        else:
            self.num_offspring = num_offspring

        self.max_generation_without_improvement=max_generation_without_improvement

    def optimize(self, do_plot=True, seed=int(time()), summary_dir=None):

        rand = Random()
        rand.seed(seed)

        if summary_dir is None:
            cwd = os.getcwd()
            summary_dir = os.path.dirname(cwd) + '/data/'

        if not os.path.exists(summary_dir):
            os.mkdir(summary_dir)

        stat_file_name = summary_dir + '/ga_statistics.csv'
        ind_file_name = summary_dir + '/ga_individuals.csv'

        stat_file = open(stat_file_name, 'w')
        ind_file = open(ind_file_name, 'w')
        print("Created files: %s and %s" % (stat_file_name, ind_file_name))

        if self.verbose:
            logger = logging.getLogger('inspyred.ec')
            logger.setLevel(logging.DEBUG)

            ch = logging.StreamHandler()
            # ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter('>>> EC: - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            logger.addHandler(ch)

        algorithm = ec.EvolutionaryComputation(rand)
        algorithm.observer = observers.file_observer
        algorithm.terminator = [terminators.evaluation_termination, terminators.no_improvement_termination]
        algorithm.selector = selectors.tournament_selection
        algorithm.replacer = replacers.steady_state_replacement
        algorithm.variator = [variators.blend_crossover, variators.gaussian_mutation]

        final_pop = algorithm.evolve(generator=self.uniform_random_chromosome,
                                     evaluator=self.evaluator.evaluate,
                                     pop_size=self.population_size,
                                     maximize=self.maximize,
                                     bounder=ec.Bounder(lower_bound=self.min_constraints,
                                                        upper_bound=self.max_constraints),
                                     num_selected=self.num_selected,
                                     tourn_size=self.tourn_size,
                                     #num_elites=self.num_elites,
                                     num_offspring=self.num_offspring,
                                     max_evaluations=self.max_evaluations,
                                     mutation_rate=self.mutation_rate,
                                     statistics_file=stat_file,
                                     seeds=self.seeds,
                                     individuals_file=ind_file)

        stat_file.close()
        ind_file.close()

        self.print_report(final_pop, do_plot, stat_file_name)

        # return the parameter set for the best individual

        return final_pop[0].candidate, final_pop[0].fitness