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
        
        cells = [self.target_cell]
        

        self.params.set_bioparameter("unphysiological_offset_current", "0.25nA", "Testing IClamp", "0")
        self.params.set_bioparameter("unphysiological_offset_current_del", "0 ms", "Testing IClamp", "0")
        self.params.set_bioparameter("unphysiological_offset_current_dur", "%f ms"%self.sim_time, "Testing IClamp", "0")
        
        c302.generate(self.reference, 
             self.params, 
             cells=cells, 
             cells_to_stimulate=cells, 
             duration=self.sim_time, 
             dt=self.dt, 
             vmin=-72 if self.params.level=='A' else -52, 
             vmax=-48 if self.params.level=='A' else -28,
             validate=(self.params.level!='B'),
             verbose=False)
             
        self.lems_file = "LEMS_%s.xml"%(self.reference)
        
        print("Running a simulation of %s ms with timestep %s ms"%(self.sim_time, self.dt))
        
        self.go_already = True
        results = pynml.run_lems_with_jneuroml(self.lems_file, nogui=True, load_saved_data=True, plot=False, verbose=False)
        #results = pynml.run_lems_with_jneuroml_neuron(self.lems_file, nogui=True, load_saved_data=True, plot=False)
        
        self.t = [t*1000 for t in results['t']]
        res_template = '%s/0/generic_iaf_cell/v'
        if self.params.level == 'C' or self.params.level == 'D':
            res_template = '%s[0]/v'
        self.volts = {}
        for cell in cells:
            self.volts[res_template%cell] = [v*1000 for v in results[res_template%cell]]
        



if __name__ == '__main__':
    
    sim_time = 1000
    dt = 0.05
    
    sim = C302Simulation('SimpleTest', 'C', sim_time, dt)
    sim.go()
    sim.show()


