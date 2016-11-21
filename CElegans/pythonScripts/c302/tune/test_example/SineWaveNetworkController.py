
import math

import numpy as np


class SineWaveNetworkController():
    
    
    def __init__(self, population_id, pop_num):
        self.population_id = population_id
        self.pop_num = pop_num
        
    
    def run_individual(self, sim_var, gen_plot=False, show_plot=True, prefix=''):
        """
        Run an individual simulation.

        The candidate data has been flattened into the sim_var dict. The
        sim_var dict contains parameter:value key value pairs, which are
        applied to the model before it is simulated.

        """
        print(">> Running individual: %s"%(sim_var))
        sim_time = 1000
        dt = 0.1
        t = 0
        times = []
        volts = {}
            
        for i in range(self.pop_num):
            volts['%s_%i'%(self.population_id, i)] = []
        
        while t <= sim_time:
            for i in range(self.pop_num):
                period = max(sim_var['period']+i*sim_var['period_increment'], 1)
                v = sim_var['offset'] + ( (sim_var['amp']+i*sim_var['amp_increment']) * (math.sin( 2*math.pi * t/period)))
             
                volts['%s_%i'%(self.population_id, i)].append(v)
                
            times.append(t)    
            t += dt
            
        if gen_plot:
            
            from matplotlib import pyplot as plt
            info = "Variables: "
            for key in sim_var.keys():
                info+="%s=%s "%(key, sim_var[key])
            
            #fig = plt.figure()
            #fig.canvas.set_window_title(info)
            
            for i in range(self.pop_num):
                ref = '%s_%i'%(self.population_id, i)
                plt.plot(times, volts[ref], label=prefix+ref)
            
            plt.legend()
            
            if show_plot:
                plt.show()
            
        return times, volts
        
    
    def run(self,candidates,parameters):
        """
        Run simulation for each candidate
        
        This run method will loop through each candidate and run the simulation
        corresponding to its parameter values. It will populate an array called
        traces with the resulting voltage traces for the simulation and return it.
        """

        traces = []
        for candidate in candidates:
            sim_var = dict(zip(parameters,candidate))
            t,v = self.run_individual(sim_var)
            traces.append([t,v])

        return traces
    
    
if __name__ == '__main__':

    sim_vars = {'amp':     5,
               'amp_increment':     20,
               'period':  1250,
               'period_increment':  -300,
               'offset':  -10}
               
    
    swc = SineWaveNetworkController('wave', 5)
        
  
    times, volts = swc.run_individual(sim_vars, True, True)
    
    