'''

    Still under developemnt!!
    
    Subject to change without notice!!
    
'''

import sys
import os.path
import time

from pyneuroml import pynml

from pyneuroml.lems import generate_lems_file_for_neuroml


class NeuroMLSimulation(object):

    target_cell = 'ADAL'
    params = None

    def __init__(self, reference, neuroml_file, target, sim_time=1000, dt=0.05, simulator='jNeuroML', generate_dir = './'):

        self.sim_time = sim_time
        self.dt = dt
        self.simulator = simulator
        self.generate_dir = generate_dir if generate_dir.endswith('/') else generate_dir+'/'
        
        self.reference = reference
        self.target = target
        self.neuroml_file = neuroml_file
        
        self.already_run = False
        


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
        
        lems_file_name = 'LEMS_%s.xml'%self.reference
        
        generate_lems_file_for_neuroml(self.reference, 
                                       self.neuroml_file, 
                                       self.target, 
                                       self.sim_time, 
                                       self.dt, 
                                       lems_file_name = lems_file_name)
        
        print("Running a simulation of %s ms with timestep %s ms: %s"%(self.sim_time, self.dt, lems_file_name))
        
        self.already_run = True
        
        start = time.time()
        if self.simulator == 'jNeuroML':
            results = pynml.run_lems_with_jneuroml(lems_file_name, 
                                                   nogui=True, 
                                                   load_saved_data=True, 
                                                   plot=False, 
                                                   exec_in_dir = self.generate_dir,
                                                   verbose=False)
        elif self.simulator == 'jNeuroML_NEURON':
            results = pynml.run_lems_with_jneuroml_neuron(lems_file_name, 
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
        
        '''
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
            self.volts[res_template%cell] = [v*1000 for v in results[res_template%cell]]'''
        



if __name__ == '__main__':
    
    sim_time = 500
    dt = 0.05
    
    if len(sys.argv) == 2 and sys.argv[1] == '-hh':
        
        sim = NeuroMLSimulation('TestHH', 
                                'tune/test_data/HHCellNetwork.net.nml',
                                'HHCellNetwork',
                                sim_time, 
                                dt, 
                                'jNeuroML', 
                                'temp')
        sim.go()
        sim.show()




