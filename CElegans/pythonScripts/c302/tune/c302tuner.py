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


    def __init__(self, reference, parameter_set, sim_time=1000, dt=0.05):

        self.sim_time = sim_time
        self.dt = dt
        self.go_already = False
        
        cells = ['ADAL']
        
        exec('from parameters_%s import ParameterisedModel'%parameter_set)
        params = ParameterisedModel()
        
        generate(reference, 
             params, 
             cells=cells, 
             cells_to_stimulate=cells, 
             duration=sim_time, 
             dt=dt, 
             vmin=-72 if parameter_set=='A' else -52, 
             vmax=-48 if parameter_set=='A' else -28,
             validate=(parameter_set!='B'))
             
        self.lems_file = "LEMS_%s.xml"%(reference)



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

        print("Running a simulation of %s ms with timestep %s ms"%(self.sim_time, self.dt))
        
        self.go_already = True


        pynml.run_lems_with_jneuroml(self.lems_file, nogui=True)
        
        self.rec_t = [0,1,2,3,4,5]
        self.rec_v = [0,.1,.2,.3,.4,.5]
        

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

        #make compartments and connect them
        soma=h.Section()
        axon=h.Section()
        soma.connect(axon)
    
        axon.insert('na')
        axon.insert('kv')
        axon.insert('kv_3')
        soma.insert('na')
        soma.insert('kv')
        soma.insert('kv_3')
    
        soma.diam=10
        soma.L=10
        axon.diam=2
        axon.L=100
    
        #soma.insert('canrgc')
        #soma.insert('cad2')
    
        self.set_section_mechanism(axon,'na','gbar',sim_var['axon_gbar_na'])
        self.set_section_mechanism(axon,'kv','gbar',sim_var['axon_gbar_kv'])
        self.set_section_mechanism(axon,'kv_3','gbar',sim_var['axon_gbar_kv3'])
        self.set_section_mechanism(soma,'na','gbar',sim_var['soma_gbar_na'])
        self.set_section_mechanism(soma,'kv','gbar',sim_var['soma_gbar_kv'])
        self.set_section_mechanism(soma,'kv_3','gbar',sim_var['soma_gbar_kv3'])
    
        for sec in h.allsec():
            sec.insert('pas')
            sec.Ra=300
            sec.cm=0.75
            self.set_section_mechanism(sec,'pas','g',1.0/30000)
            self.set_section_mechanism(sec,'pas','e',-70)
    
        h.vshift_na=-5.0
        sim=Simulation(soma,sim_time=1000,v_init=-70.0)
        sim.set_IClamp(150, 0.1, 750)
        sim.go()

        if show:
            sim.show()
    
        return np.array(sim.rec_t), np.array(sim.rec_v)


if __name__ == '__main__':

    if len(sys.argv) == 2:
        if sys.argv[1] == '-sim':
            sim = C302Simulation('SimpleTest', 'C')
            sim.go()
            sim.show()