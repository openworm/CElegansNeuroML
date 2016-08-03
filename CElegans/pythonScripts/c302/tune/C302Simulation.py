'''

    Still under developemnt!!
    
    Subject to change without notice!!
    
'''

import sys
import os.path
import time

from pyneuroml import pynml


if not os.path.isfile('c302.py'):
    print('This script should be run from dir: CElegansNeuroML/CElegans/pythonScripts/c302')
    exit()
        
sys.path.append(".")
import c302

class C302Simulation(object):

    target_cell = 'ADAL'
    params = None
    
    results = None

    def __init__(self, reference, parameter_set, config, sim_time=1000, dt=0.05, simulator='jNeuroML', generate_dir = './'):

        self.sim_time = sim_time
        self.dt = dt
        self.simulator = simulator
        self.already_run = False
        self.generate_dir = generate_dir if generate_dir.endswith('/') else generate_dir+'/'
        
        exec('from c302_%s import setup'%config)
        
        self.cells, self.cells_to_stimulate, self.params, self.include_muscles = setup(parameter_set)
        
        self.reference = reference
        


    def show(self):
        """
        Plot the result of the simulation once it's been intialized
        """

        from matplotlib import pyplot as plt

        if self.already_run:
            
            for ref in self.volts.keys():
            
                plt.plot(self.t, self.volts[ref], label=ref)
                plt.title("Simulation voltage vs time")
                plt.legend()
                plt.xlabel("Time [ms]")
                plt.ylabel("Voltage [mV]")

        else:
            print("""First you have to `go()` the simulation.""")
        plt.show()
        
    
    def go(self):
        """
        Start the simulation once it's been intialized
        """
        
        nml_doc = c302.generate(self.reference, 
                                self.params, 
                                cells=self.cells, 
                                cells_to_stimulate=self.cells_to_stimulate, 
                                include_muscles = self.include_muscles,
                                duration=self.sim_time, 
                                dt=self.dt, 
                                validate=(self.params.level!='B'),
                                verbose=False,
                                target_directory = self.generate_dir)
             
        self.lems_file ="LEMS_%s.xml"%(self.reference)
        
        print("Running a simulation of %s ms with timestep %s ms: %s"%(self.sim_time, self.dt, self.lems_file))
        
        self.already_run = True
        
        start = time.time()
        if self.simulator == 'jNeuroML':
            self.results = pynml.run_lems_with_jneuroml(self.lems_file, 
                                                   nogui=True, 
                                                   load_saved_data=True, 
                                                   plot=False, 
                                                   exec_in_dir = self.generate_dir,
                                                   verbose=False)
        elif self.simulator == 'jNeuroML_NEURON':
            self.results = pynml.run_lems_with_jneuroml_neuron(self.lems_file, 
                                                          nogui=True, 
                                                          load_saved_data=True, 
                                                          plot=False, 
                                                          exec_in_dir = self.generate_dir,
                                                          verbose=False)
        else:
            print('Unsupported simulator: %s'%self.simulator)
            exit()
            
        secs = time.time()-start
    
        print("Ran simulation in %s in %f seconds (%f mins)\n\n"%(self.simulator, secs, secs/60.0))
        
        self.t = [t*1000 for t in self.results['t']]
        res_template = '%s/0/generic_iaf_cell/v'
        if self.params.level == 'C' or self.params.level == 'D':
            res_template = '%s/0/GenericCell/v'
        self.volts = {}
        
        if self.cells is None:
            self.cells = []
            for pop in nml_doc.networks[0].populations:
                self.cells.append(pop.id)
            
        for cell in self.cells:
            self.volts[res_template%cell] = [v*1000 for v in self.results[res_template%cell]]
        



if __name__ == '__main__':
    
    sim_time = 500
    dt = 0.05
    
    if len(sys.argv) == 2 and sys.argv[1] == '-phar':
        
        sim = C302Simulation('TestPhar', 'C', 'Pharyngeal', sim_time, dt, 'jNeuroML', 'temp')
        sim.go()
        sim.show()

    elif len(sys.argv) == 2 and sys.argv[1] == '-pharN':
        
        sim = C302Simulation('TestPhar', 'C', 'Pharyngeal', sim_time, dt, 'jNeuroML_NEURON', 'temp')
        sim.go()
        sim.show()
        
    elif len(sys.argv) == 2 and sys.argv[1] == '-musc':
        
        sim = C302Simulation('TestMuscles', 'B', 'Muscles', sim_time, dt)
        sim.go()
        sim.show()
        
    elif len(sys.argv) == 2 and sys.argv[1] == '-muscN':
        
        sim = C302Simulation('TestMuscles', 'B', 'Muscles', sim_time, dt, 'jNeuroML_NEURON')
        sim.go()
        sim.show()
        
    elif len(sys.argv) == 2 and sys.argv[1] == '-osc':
        
        sim = C302Simulation('TestOsc', 'C', 'Oscillator', sim_time, dt, 'jNeuroML', 'temp')
        sim.go()
        sim.show()
        
    elif len(sys.argv) == 2 and sys.argv[1] == '-oscC1':
        
        sim = C302Simulation('TestOsc', 'C1', 'Oscillator', sim_time, dt, 'jNeuroML', 'temp')
        sim.go()
        sim.show()
        
    elif len(sys.argv) == 2 and sys.argv[1] == '-oscN':
        
        sim = C302Simulation('TestOsc', 'C', 'Oscillator', sim_time, dt, 'jNeuroML_NEURON', 'temp')
        sim.go()
        sim.show()
        
    else:

        sim = C302Simulation('TestIClamp', 'C', 'IClamp', sim_time, dt)
        sim.go()
        sim.show()


