"""Model class for muscle_model projects"""

# Built-in libs
import os
from importlib import import_module

# Common libs
import numpy as np
import quantities as pq
from neo.core import AnalogSignal

# Testing libs
from neuronunit.models import LEMSModel
from neuronunit import capabilities as cap
import neuronunit.capabilities.spike_functions as sf

# OpenWorm libs
import c302

class MuscleModel(LEMSModel,
                  cap.ProducesActionPotentials):
    """A C. elegans muscle cell model"""

    def __init__(self, 
                 config, 
                 parameter_set, 
                 duration, 
                 dt, 
                 data_reader="UpdatedSpreadsheetDataReader",
                 verbose=False,
                 param_overrides={},
                 config_package="",
                 config_param_overrides={},
                 name=None, 
                 backend='jNeuroML', 
                 attrs=None):
        
        if config_package:
            c302_config = import_module('c302.%s.c302_%s' % (config_package, config))
        else:
            c302_config = import_module('c302.c302_%s' % config)
        
        root = c302.__path__[0]
        cells, cells_to_stimulate, params, muscles = c302_config.setup(
                                parameter_set, 
                                data_reader=data_reader,
                                generate=True,
                                duration=duration, 
                                dt=dt,
                                target_directory=os.path.join(root,'examples'),
                                verbose=verbose,
                                param_overrides=param_overrides,
                                config_param_overrides=config_param_overrides)
    
        LEMS_file_path = os.path.join(root,'examples','LEMS_c302_%s_%s.xml'%(parameter_set,config))
        super().__init__(LEMS_file_path,name=name,backend=backend,attrs=attrs)

    def get_membrane_potential(self, cell='GenericMuscleCell', **run_params):
        """Gets membrane potential of either the neuron or the muscle cell"""
        self.run(**run_params)
        for rkey in self.results.keys():
            if '%s/v'%cell in rkey:
                v = np.array(self.results[rkey])
        t = np.array(self.results['t'])
        dt = (t[1]-t[0])*pq.s # Time per sample in seconds.
        vm = AnalogSignal(v,units=pq.V,sampling_rate=1.0/dt).rescale('mV')
        return vm 
        
    def get_membrane_potential_neuron(self, **run_params):
        """Gets membrane potential of the neuron"""
        return self.get_membrane_potential(cell='GenericNeuronCell',**run_params)
    
    def get_membrane_potential_muscle(self, **run_params):
        """Gets membrane potential of the muscle cell"""
        return self.get_membrane_potential(cell='GenericMuscleCell',**run_params)
    
    def get_APs(self, rerun=False, **run_params):
        vm = self.get_membrane_potential(rerun=rerun, **run_params)
        waveforms = sf.get_spike_waveforms(vm)
        return waveforms

    def get_spike_train(self, rerun=False, **run_params):
        vm = self.get_membrane_potential(rerun=rerun, **run_params)
        spike_train = sf.get_spike_train(vm)
        return spike_train