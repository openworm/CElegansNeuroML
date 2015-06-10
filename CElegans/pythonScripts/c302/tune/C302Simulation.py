'''

    Still under developemnt!!
    
    Subject to change without notice!!
    
'''

import sys
import os.path

from pyneuroml import pynml


if not os.path.isfile('c302.py'):
    print('This script should be run from dir: CElegansNeuroML/CElegans/pythonScripts/c302')
    exit()
        
sys.path.append(".")
import c302

class C302Simulation(object):

    target_cell = 'ADAL'
    params = None

    def __init__(self, reference, parameter_set, config, sim_time=1000, dt=0.05):

        self.sim_time = sim_time
        self.dt = dt
        self.go_already = False
        
        exec('from c302_%s import setup'%config)
        
        self.cells, self.cells_to_stimulate, self.params = setup(parameter_set)
        
        self.reference = reference
        


    def show(self):
        """
        Plot the result of the simulation once it's been intialized
        """

        from matplotlib import pyplot as plt

        if self.go_already:
            
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
                                duration=self.sim_time, 
                                dt=self.dt, 
                                validate=(self.params.level!='B'),
                                verbose=False)
             
        self.lems_file = "LEMS_%s.xml"%(self.reference)
        
        print("Running a simulation of %s ms with timestep %s ms"%(self.sim_time, self.dt))
        
        self.go_already = True
        results = pynml.run_lems_with_jneuroml(self.lems_file, nogui=True, load_saved_data=True, plot=False, verbose=False)
        #results = pynml.run_lems_with_jneuroml_neuron(self.lems_file, nogui=True, load_saved_data=True, plot=False)
        
        self.t = [t*1000 for t in results['t']]
        res_template = '%s/0/generic_iaf_cell/v'
        if self.params.level == 'B' or self.params.level == 'C' or self.params.level == 'D':
            res_template = '%s[0]/v'
        self.volts = {}
        
        if self.cells is None:
            self.cells = []
            for pop in nml_doc.networks[0].populations:
                self.cells.append(pop.id)
            
                
        for cell in self.cells:
            self.volts[res_template%cell] = [v*1000 for v in results[res_template%cell]]
        



if __name__ == '__main__':
    
    sim_time = 1000
    dt = 0.05
    
    if len(sys.argv) == 2 and sys.argv[1] == '-phar':
        
        sim = C302Simulation('TestPhar', 'B', 'Pharyngeal', sim_time, dt)
        sim.go()
        sim.show()
        
    elif len(sys.argv) == 2 and sys.argv[1] == '-musc':
        
        sim = C302Simulation('TestMuscles', 'B', 'Muscles', sim_time, dt)
        sim.go()
        sim.show()
        
    else:

        sim = C302Simulation('TestIClamp', 'C', 'IClamp', sim_time, dt)
        sim.go()
        sim.show()


