'''

    Still under developemnt!!
    
    Subject to change without notice!!
    
'''


import os.path
import sys

from collections import OrderedDict

if not os.path.isfile('c302.py'):
    print('This script should be run from dir: CElegansNeuroML/CElegans/pythonScripts/c302')
    exit()
        
sys.path.append(".")

from C302Simulation import C302Simulation

class C302Controller():

    def __init__(self, ref, params, config, sim_time=1000, dt=0.05, generate_dir = './', simulator='jNeuroML'):
        
        self.ref = ref
        self.params = params
        self.config = config
        self.sim_time = sim_time
        self.dt = dt
        self.simulator = simulator
        self.generate_dir = generate_dir if generate_dir.endswith('/') else generate_dir+'/'

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
            print('\nRunning with variables: %s'%sim_var)
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
        
        sim = C302Simulation(self.ref, 
                             self.params, 
                             self.config, 
                             sim_time = self.sim_time, 
                             dt = self.dt, 
                             simulator = self.simulator, 
                             generate_dir = self.generate_dir)
        
        for var_name in sim_var.keys():
            bp = sim.params.get_bioparameter(var_name)
            print("Changing param %s: %s -> %s"%(var_name, bp.value, sim_var[var_name]))
            bp.change_magnitude(sim_var[var_name])
        
        sim.go()
        
        if show:
            sim.show()
    
        return sim.t, sim.volts


if __name__ == '__main__':
    
    if len(sys.argv) == 2 and sys.argv[1] == '-net':
                
        cont = C302Controller('NetTest', 'B', 'Muscles')

        sim_vars = OrderedDict([('chem_exc_syn_gbase',0.4),
                  ('chem_exc_syn_decay',10),
                  ('chem_inh_syn_gbase',1),
                  ('chem_inh_syn_decay',40)])

        cont.run_individual(sim_vars, show=True)
        
    elif len(sys.argv) == 2 and sys.argv[1] == '-phar':
                
        cont = C302Controller('PharTest', 'B', 'Pharyngeal', generate_dir = 'temp')

        sim_vars = OrderedDict([('chem_exc_syn_gbase',0.2),
                  ('chem_exc_syn_decay',20),
                  ('chem_inh_syn_gbase',0.5),
                  ('chem_inh_syn_decay',40)])

        t, volts = cont.run_individual(sim_vars, show=True)
        print(volts.keys())
        
    else:
    
        cont = C302Controller('SimpleTest', 'C', 'IClamp')

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