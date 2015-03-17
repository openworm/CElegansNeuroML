'''

    Still under developemnt!!
    
    Subject to change without notice!!
    
'''


from neurotune import optimizers
from neurotune import evaluators
from neurotune import controllers
from matplotlib import pyplot as plt
from pyelectro import io
from pyelectro import analysis

import numpy as np
import sys
import os.path

from pyneuroml import pynml


if not os.path.isfile('c302.py'):
    print('This script should be run from dir: CElegansNeuroML/CElegans/pythonScripts/c302')
    exit()
        
sys.path.append(".")
from c302 import generate

class C302Simulation(object):

    target_cell = 'ADAL'
    params = None

    def __init__(self, reference, parameter_set, sim_time=1000, dt=0.05):

        self.sim_time = sim_time
        self.dt = dt
        self.go_already = False
        
        exec('from parameters_%s import ParameterisedModel'%parameter_set)
        self.params = ParameterisedModel()
        
        self.reference = reference
        


    def show(self):
        """
        Plot the result of the simulation once it's been intialized
        """

        from matplotlib import pyplot as plt

        if self.go_already:
            x = np.array(self.rec_t)
            y = np.array(self.rec_v)

            plt.plot(x, y)
            plt.title("Simulation voltage vs time")
            plt.xlabel("Time [ms]")
            plt.ylabel("Voltage [mV]")

        else:
            print("""First you have to `go()` the simulation.""")
        plt.show()
        
    
    def go(self):
        """
        Start the simulation once it's been intialized
        """
        
        cells = [self.target_cell]
        

        self.params.set_bioparameter("unphysiological_offset_current", "0.25nA", "Testing IClamp", "0")
        self.params.set_bioparameter("unphysiological_offset_current_del", "0 ms", "Testing IClamp", "0")
        self.params.set_bioparameter("unphysiological_offset_current_dur", "%f ms"%self.sim_time, "Testing IClamp", "0")
        
        generate(self.reference, 
             self.params, 
             cells=cells, 
             cells_to_stimulate=cells, 
             duration=self.sim_time, 
             dt=self.dt, 
             vmin=-72 if self.params.level=='A' else -52, 
             vmax=-48 if self.params.level=='A' else -28,
             validate=(self.params.level!='B'))
             
        self.lems_file = "LEMS_%s.xml"%(self.reference)
        
        print("Running a simulation of %s ms with timestep %s ms"%(self.sim_time, self.dt))
        
        self.go_already = True
        results = pynml.run_lems_with_jneuroml(self.lems_file, nogui=True, load_saved_data=True, plot=False)
        
        self.rec_t = results['t']
        res_template = '%s/0/generic_iaf_cell/v'
        if self.params.level == 'C' or self.params.level == 'D':
            res_template = '%s[0]/v'
        self.rec_v = results[res_template%self.target_cell]
        

class C302Controller():


    def run(self,candidates,parameters):
        """
        Run simulation for each candidate
        
        This run method will loop through each candidate and run the simulation
        corresponding to it's parameter values. It will populate an array called
        traces with the resulting voltage traces for the simulation and return it.
        """

        traces = []
        for candidate in candidates:
            sim_var = dict(zip(parameters,candidate))
            t,v = self.run_individual(sim_var)
            traces.append([t,v])

        return traces

        
    
    def run_individual(self, sim_var, show=False):
        """
        Run an individual simulation.

        The candidate data has been flattened into the sim_var dict. The
        sim_var dict contains parameter:value key value pairs, which are
        applied to the model before it is simulated.

        The simulation itself is carried out via the instantiation of a
        Simulation object (see Simulation class above).

        """
        
        sim = C302Simulation('SimpleTest', 'C')
        
        for var_name in sim_var.keys():
            bp = sim.params.get_bioparameter(var_name)
            print("Changing param %s: %s -> %s"%(var_name, bp.value, sim_var[var_name]))
            bp.change_magnitude(sim_var[var_name])
        
        sim.go()
        
        if show:
            sim.show()
    
        return np.array(sim.rec_t)*1000, np.array(sim.rec_v)*1000


if __name__ == '__main__':
    
    my_controller = C302Controller()

    parameters = ['leak_cond_density','k_slow_cond_density','k_fast_cond_density','ca_boyle_cond_density', 'specific_capacitance']

    #above parameters will not be modified outside these bounds:
    min_constraints = [0.001, 0.01,   0.01,   0.01, 0.1]
    max_constraints = [0.05,  0.6,    0.2,    0.6,  3]

    analysis_var={'peak_delta':0,'baseline':0,'dvdt_threshold':0, 'peak_threshold':-6.82}

    weights={'average_minimum': 1.0,
             'spike_frequency_adaptation': 1.0,
             'trough_phase_adaptation': 1.0,
             'mean_spike_frequency': 1.0,
             'average_maximum': 1.0,
             'trough_decay_exponent': 1.0,
             'interspike_time_covar': 1.0,
             'min_peak_no': 1.0,
             'spike_broadening': 1.0,
             'spike_width_adaptation': 1.0,
             'max_peak_no': 1.0,
             'first_spike_time': 1.0,
             'peak_decay_exponent': 1.0,
             'pptd_error':1.0}
             
    weights = {'peak_linear_gradient': 20,
               'average_minimum': 5.0, 
               'spike_frequency_adaptation': 0.0, 
               'trough_phase_adaptation': 0.0, 
               'mean_spike_frequency': 1.0, 
               'average_maximum': 2.0, 
               'trough_decay_exponent': 0.0, 
               'interspike_time_covar': 0.0, 
               'min_peak_no': 1.0, 
               'spike_width_adaptation': 0.0, 
               'max_peak_no': 50.0, 
               'first_spike_time': 1.0, 
               'peak_decay_exponent': 0.0}

    data = 'SimpleTest.dat'


    sim_var = {}
    for i in range(len(parameters)):
        sim_var[parameters[i]] = max_constraints[i]
    print(sim_var)
        

    if len(sys.argv) == 2 and sys.argv[1] == '-sim':
        sim = C302Simulation('SimpleTest', 'C')
        sim.go()
        sim.show()
        
    elif len(sys.argv) == 2 and sys.argv[1] == '-opt':
        
        # Based on: https://github.com/openworm/muscle_model/blob/master/pyramidal_implementation/data_analysis.py
        data_fname = "tune/redacted_data.txt"
        dt = 0.0002

        #load the voltage:
        file=open(data_fname)

        #make voltage into a numpy array in mV:
        v = np.array([float(i) for i in file.readlines()])*1000

        t_init = 0.0
        t_final = len(v)*dt

        t = np.linspace(t_init,t_final,len(v))*1000

        #pyplot.plot(t,v)
        #pyplot.show()

        analysis_var={'peak_delta':0.0,'baseline':5,'dvdt_threshold':0.0}

        analysis_i=analysis.IClampAnalysis(v,t,analysis_var,
                              start_analysis=0,
                              end_analysis=900,
                              smooth_data=True,
                              show_smoothed_data=False,
                              smoothing_window_len=33)

        target_data = analysis_i.analyse()


        #make an evaluator, using automatic target evaluation:
        my_evaluator=evaluators.IClampEvaluator(controller=my_controller,
                                                analysis_start_time=0,
                                                analysis_end_time=900,
                                                target_data_path=data,
                                                parameters=parameters,
                                                analysis_var=analysis_var,
                                                weights=weights,
                                                targets=target_data,
                                                automatic=False)

        evals = 100
        #make an optimizer
        my_optimizer=optimizers.CustomOptimizerA(max_constraints,
                                                 min_constraints,
                                                 my_evaluator,
                                                 population_size=50,
                                                 max_evaluations=evals,
                                                 num_selected=5,
                                                 num_offspring=5,
                                                 num_elites=1,
                                                 mutation_rate=0.5,
                                                 seeds=None,
                                                 verbose=True)

        #run the optimizer
        best_candidate = my_optimizer.optimize(do_plot=False)
        
        for key,value in zip(parameters,best_candidate):
            sim_var[key]=value
        best_candidate_t,best_candidate_v = my_controller.run_individual(sim_var,show=False)

        
        data_plot = plt.plot(np.array(t),np.array(v))
        best_candidate_plot = plt.plot(np.array(best_candidate_t),np.array(best_candidate_v))

        plt.legend([data_plot,best_candidate_plot],
                   ["Original data","Best model - %i evaluations"%evals])

        plt.ylim(-80.0,80.0)
        plt.xlim(0.0,1000.0)
        plt.title("Models optimized from data")
        plt.xlabel("Time (ms)")
        plt.ylabel("Membrane potential(mV)")
        plt.savefig("data_vs_candidate.png",bbox_inches='tight',format='png')
        plt.show()

    else:

        surrogate_t, surrogate_v = my_controller.run_individual(sim_var, show=False)

        print("Have run individual instance...")


        surrogate_analysis=analysis.IClampAnalysis(surrogate_v,
                                                   surrogate_t,
                                                   analysis_var,
                                                   start_analysis=0,
                                                   end_analysis=900,
                                                   smooth_data=False,
                                                   show_smoothed_data=True)

        print(surrogate_analysis.max_min_dictionary)



