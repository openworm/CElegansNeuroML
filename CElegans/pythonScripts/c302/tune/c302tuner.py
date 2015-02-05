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

from pyneuroml import pynml

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
        

        self.params.set_bioparameter("unphysiological_offset_current", "0.21nA", "Testing IClamp", "0")
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
        results = pynml.run_lems_with_jneuroml(self.lems_file, nogui=True, load_saved_data=True)
        
        self.rec_t = results['neurons_v']['t']
        self.rec_v = results['neurons_v']['%s_v'%self.target_cell]
        

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

    def set_bio_parameter(self, name, value):

        print("Setting %s = %s"%(name, value))
    
    def run_individual(self,sim_var,show=False):
        """
        Run an individual simulation.

        The candidate data has been flattened into the sim_var dict. The
        sim_var dict contains parameter:value key value pairs, which are
        applied to the model before it is simulated.

        The simulation itself is carried out via the instantiation of a
        Simulation object (see Simulation class above).

        """
    
        
        sim=C302Simulation('SimpleTest', 'A')
        
        sim.go()

        if show:
            sim.show()
    
        return np.array(sim.rec_t), np.array(sim.rec_v)


if __name__ == '__main__':

    if len(sys.argv) == 2:
        if sys.argv[1] == '-sim':
            sim = C302Simulation('SimpleTest', 'A')
            sim.go()
            sim.show()
        if sys.argv[1] == '-cont':
            
            my_controller = C302Controller()
            
            parameters = ['iaf_leak_reversal',
                  'iaf_reset',
                  'iaf_thresh',
                  'iaf_C',
                  'iaf_conductance']
    
            #above parameters will not be modified outside these bounds:
            min_constraints = [-80, -80, -60, 0.1, 0.005]
            max_constraints = [-50, -50, -20, 2, 0.02]
            
            analysis_var={'peak_delta':1,'baseline':0,'dvdt_threshold':2}

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
                     
            data = 'SimpleTest.dat'
            
            sim_var = {}
            
            surrogate_t, surrogate_v = my_controller.run_individual(sim_var,show=False)
            

            analysis_var={'peak_delta':1e-4,'baseline':0,'dvdt_threshold':0.0}

            surrogate_analysis=analysis.IClampAnalysis(surrogate_v,
                                                       surrogate_t,
                                                       analysis_var,
                                                       start_analysis=0,
                                                       end_analysis=900,
                                                       smooth_data=False,
                                                       show_smoothed_data=True)
                                                       
            '''

            # The output of the analysis will serve as the basis for model optimization:
            surrogate_targets = surrogate_analysis.analyse()
                     

            #make an evaluator, using automatic target evaluation:
            my_evaluator=evaluators.IClampEvaluator(controller=my_controller,
                                                    analysis_start_time=0,
                                                    analysis_end_time=900,
                                                    target_data_path=data,
                                                    parameters=parameters,
                                                    analysis_var=analysis_var,
                                                    weights=weights,
                                                    targets=targets,
                                                    automatic=False)
                                                    '''
            