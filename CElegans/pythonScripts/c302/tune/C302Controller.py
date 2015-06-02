'''

    Still under developemnt!!
    
    Subject to change without notice!!
    
'''


import os.path
import sys

import numpy as np

from collections import OrderedDict

if not os.path.isfile('c302.py'):
    print('This script should be run from dir: CElegansNeuroML/CElegans/pythonScripts/c302')
    exit()
        
sys.path.append(".")

from C302Simulation import C302Simulation

class C302Controller():

    def __init__(self, sim_time=1000, dt=0.05):
        
        self.sim_time = sim_time
        self.dt = dt

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
        
        sim = C302Simulation('SimpleTest', 'C', sim_time=self.sim_time, dt=self.dt)
        
        for var_name in sim_var.keys():
            bp = sim.params.get_bioparameter(var_name)
            print("Changing param %s: %s -> %s"%(var_name, bp.value, sim_var[var_name]))
            bp.change_magnitude(sim_var[var_name])
        
        sim.go()
        
        if show:
            sim.show()
    
        return sim.t, sim.volts


if __name__ == '__main__':
    
    cont = C302Controller()
    
    sim_vars = OrderedDict([('leak_cond_density', 0.05), 
                            ('k_slow_cond_density', 0.5), 
                            ('k_fast_cond_density', 0.05), 
                            ('ca_boyle_cond_density', 0.5), 
                            ('specific_capacitance', 1.05), 
                            ('leak_erev', -50), 
                            ('k_slow_erev', -60), 
                            ('k_fast_erev', -60), 
                            ('ca_boyle_erev', 40)])
                            
    cont.run_individual(sim_vars, show=True)