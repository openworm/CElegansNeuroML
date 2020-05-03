'''

    Still under developemnt!!
    
    Subject to change without notice!!
    
'''

import sys
import os.path
import time

from pyneuroml import pynml

import neuroml.writers as writers


if not os.path.isfile('c302.py'):
    c302.print_('This script should be run from dir: CElegansNeuroML/CElegans/pythonScripts/c302')
    exit()
        
sys.path.append(".")
import c302

class C302Simulation(object):

    def __init__(self, reference, parameter_set, config, config_package=None, data_reader="SpreadsheetDataReader", sim_time=1000, dt=0.05, simulator='jNeuroML', generate_dir = './', input_list=None, conns_to_include=[], conns_to_exclude=[]):

        self.target_cell = 'ADAL' # TODO: obsolete?

        self.sim_time = sim_time
        self.dt = dt
        self.simulator = simulator
        self.already_run = False
        self.generate_dir = generate_dir if generate_dir.endswith('/') else generate_dir+'/'

        if config_package:
            exec ('from %s.c302_%s import setup' % (config_package, config))
        else:
            exec('from c302_%s import setup'%config)

        self.data_reader = data_reader

        self.input_list = input_list
        
        self.cells, self.cells_to_stimulate, self.params, self.muscles_to_include, nml_doc = setup(parameter_set)
        
        self.reference = reference

        self.conns_to_include = conns_to_include
        self.conns_to_exclude = conns_to_exclude
        


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
            c302.print_("""First you have to `go()` the simulation.""")
        plt.show()
        
    
    def go(self):
        """
        Start the simulation once it's been intialized
        """

        nml_doc = c302.generate(self.reference, 
                                self.params, 
                                cells=self.cells, 
                                cells_to_stimulate=self.cells_to_stimulate, 
                                muscles_to_include = self.muscles_to_include,
                                duration=self.sim_time, 
                                dt=self.dt, 
                                verbose=False,
                                target_directory = self.generate_dir,
                                data_reader=self.data_reader,
                                conns_to_include=self.conns_to_include,
                                conns_to_exclude=self.conns_to_exclude)

        if self.input_list:
            for input_tuple in self.input_list:
                cell, start, duration, amplitude = input_tuple
                c302.add_new_input(nml_doc, cell, start, duration, amplitude, self.params)
            nml_file = self.generate_dir + '/' + self.reference + '.nml'
            writers.NeuroMLWriter.write(nml_doc, nml_file)

        self.lems_file ="LEMS_%s.xml"%(self.reference)
        
        c302.print_("Running a simulation of %s ms with timestep %s ms: %s"%(self.sim_time, self.dt, self.lems_file))
        
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
            c302.print_('Unsupported simulator: %s'%self.simulator)
            exit()


        # pynml.run_lems_with...() can return False!
        """if self.results is False:
            print
            print
            print
            print "SIMULATION RETURNED NO RESULT"
            print
            print
            print
            exit()"""
            
        secs = time.time()-start
    
        c302.print_("Ran simulation in %s in %f seconds (%f mins)\n\n"%(self.simulator, secs, secs/60.0))
        
        self.t = [t*1000 for t in self.results['t']]
        res_template_n = '%s/0/generic_neuron_iaf_cell/v'
        if self.params.level.startswith('C') or self.params.level.startswith('D'):
            res_template_n = '%s/0/GenericNeuronCell/v'
            res_template_m = '%s/0/GenericMuscleCell/v'
        self.volts = {}
        
        if self.cells is None:
            self.cells = []
            for pop in nml_doc.networks[0].populations:
                self.cells.append(pop.id)
            
        for cell in self.cells:
            self.volts[res_template_n%cell] = [v*1000 for v in self.results[res_template_n%cell]]

        res_template = '%s/0/GenericMuscleCell/v'
        muscles = []
        if self.muscles_to_include is None or self.muscles_to_include is True:
            # muscles_to_include = True or None -> ALL muscles
            muscles = c302.get_muscle_names()
        elif isinstance(self.muscles_to_include, list) and self.muscles_to_include:
            # len(muscles_to_include) > 0
            muscles = self.muscles_to_include

        for muscle in muscles:
            self.volts[res_template % muscle] = [v * 1000 for v in self.results[res_template % muscle]]


if __name__ == '__main__':
    
    sim_time = 500
    dt = 0.05
    
    if len(sys.argv) == 2 and sys.argv[1] == '-phar':
        
        sim = C302Simulation('TestPhar', 'C', 'Pharyngeal', sim_time=sim_time, dt=dt, simulator='jNeuroML', generate_dir='temp')
        sim.go()
        sim.show()

    elif len(sys.argv) == 2 and sys.argv[1] == '-pharN':
        
        sim = C302Simulation('TestPhar', 'C0', 'Pharyngeal', sim_time=sim_time, dt=dt, simulator='jNeuroML_NEURON', generate_dir='temp')
        sim.go()
        sim.show()
        
    elif len(sys.argv) == 2 and sys.argv[1] == '-musc':
        
        sim = C302Simulation('TestMuscles', 'B', 'Muscles', sim_time=sim_time, dt=dt)
        sim.go()
        sim.show()
        
    elif len(sys.argv) == 2 and sys.argv[1] == '-muscC0':
        
        sim = C302Simulation('TestMuscles', 'C0', 'Muscles', sim_time=sim_time, dt=dt)
        sim.go()
        sim.show()
        
    elif len(sys.argv) == 2 and sys.argv[1] == '-muscN':
        
        sim = C302Simulation('TestMuscles', 'B', 'Muscles', sim_time=sim_time, dt=dt, simulator='jNeuroML_NEURON', generate_dir='temp')
        sim.go()
        sim.show()
        
    elif len(sys.argv) == 2 and sys.argv[1] == '-osc':
        
        sim = C302Simulation('TestOsc', 'C', 'Oscillator', sim_time=sim_time, dt=dt, simulator='jNeuroML', generate_dir='temp')
        sim.go()
        sim.show()
        
    elif len(sys.argv) == 2 and sys.argv[1] == '-oscC1':
        
        sim = C302Simulation('TestOsc', 'C1', 'Oscillator', sim_time=sim_time, dt=dt, simulator='jNeuroML', generate_dir='temp')
        sim.go()
        sim.show()
        
    elif len(sys.argv) == 2 and sys.argv[1] == '-oscN':
        
        sim = C302Simulation('TestOsc', 'C', 'Oscillator', sim_time=sim_time, dt=dt, simulator='jNeuroML', generate_dir='temp')
        sim.go()
        sim.show()
        
        
    elif len(sys.argv) == 2 and sys.argv[1] == '-imC0':

        sim = C302Simulation('TestIClampMuscle', 'C0', 'IClampMuscle', sim_time=sim_time, dt=dt, simulator='jNeuroML', generate_dir='temp')
        sim.go()
        sim.show()
        
    else:

        sim = C302Simulation('TestIClamp', 'C', 'IClamp', dt=dt, sim_time=6000)
        sim.go()
        sim.show()


