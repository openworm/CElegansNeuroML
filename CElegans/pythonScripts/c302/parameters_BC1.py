'''

    Parameters BC1 for c302 still under developemnt!!
    
    
    Uses IaF cells from B & analogue synapses from C1 .. 
    
    Subject to change without notice!!
    
'''
from neuroml import Cell
from neuroml import Morphology
from neuroml import Point3DWithDiam
from neuroml import Segment
from neuroml import BiophysicalProperties
from neuroml import IntracellularProperties
from neuroml import Resistivity
from neuroml import Species
from neuroml import MembraneProperties
from neuroml import InitMembPotential
from neuroml import SpecificCapacitance
from neuroml import ChannelDensity
from neuroml import SpikeThresh

from neuroml import GradedSynapse
from neuroml import GapJunction
from neuroml import PulseGenerator

from bioparameters import c302ModelPrototype

from parameters_B import IafActivityCell

'''

    The values below are a FIRST APPROXIMATION of conductance based neurons for use in a network to 
    investigate the synaptic connectivity of C elegans
        

'''

class ParameterisedModel(c302ModelPrototype):

    def __init__(self):
        self.level = "BC1"
        self.custom_component_types_definitions = 'cell_B.xml'
        
        self.set_default_bioparameters()

    def set_default_bioparameters(self):

        self.add_bioparameter("muscle_iaf_leak_reversal", "-50mV", "BlindGuess", "0.1")
        self.add_bioparameter("muscle_iaf_reset", "-50mV", "BlindGuess", "0.1")
        self.add_bioparameter("muscle_iaf_thresh", "-30mV", "BlindGuess", "0.1")
        self.add_bioparameter("muscle_iaf_C", "3pF", "BlindGuess", "0.1")
        self.add_bioparameter("muscle_iaf_conductance", "0.1nS", "BlindGuess", "0.1")
        self.add_bioparameter("muscle_iaf_tau1", "50ms", "BlindGuess", "0.1")

        self.add_bioparameter("neuron_iaf_leak_reversal", "-50mV", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_iaf_reset", "-50mV", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_iaf_thresh", "-30mV", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_iaf_C", "3pF", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_iaf_conductance", "0.1nS", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_iaf_tau1", "50ms", "BlindGuess", "0.1")


        self.add_bioparameter("exc_syn_conductance", "8 nS", "BlindGuess", "0.1")
        self.add_bioparameter("exc_syn_delta", "5 mV", "BlindGuess", "0.1")
        self.add_bioparameter("exc_syn_vth", "0 mV", "BlindGuess", "0.1")
        self.add_bioparameter("exc_syn_erev", "0 mV", "BlindGuess", "0.1")
        self.add_bioparameter("exc_syn_k", "0.025per_ms", "BlindGuess", "0.1")

        self.add_bioparameter("inh_syn_conductance", "8 nS", "BlindGuess", "0.1")
        self.add_bioparameter("inh_syn_delta", "5 mV", "BlindGuess", "0.1")
        self.add_bioparameter("inh_syn_vth", "0 mV", "BlindGuess", "0.1")
        self.add_bioparameter("inh_syn_erev", "-70 mV", "BlindGuess", "0.1")
        self.add_bioparameter("inh_syn_k", "0.025per_ms", "BlindGuess", "0.1")
        

        self.add_bioparameter("elec_syn_gbase", "0.3 nS", "BlindGuess", "0.1")

        self.add_bioparameter("unphysiological_offset_current", "0.35 nA", "KnownError", "0")
        self.add_bioparameter("unphysiological_offset_current_del", "0 ms", "KnownError", "0")
        self.add_bioparameter("unphysiological_offset_current_dur", "2000 ms", "KnownError", "0")

    def cerate_generic_muscle_cell(self):
        self.generic_muscle_cell = IafActivityCell(id="generic_muscle_iaf_cell", 
                                C =                 self.get_bioparameter("muscle_iaf_C").value,
                                thresh =            self.get_bioparameter("muscle_iaf_thresh").value,
                                reset =             self.get_bioparameter("muscle_iaf_reset").value,
                                leak_conductance =  self.get_bioparameter("muscle_iaf_conductance").value,
                                leak_reversal =     self.get_bioparameter("muscle_iaf_leak_reversal").value)   
   
    def cerate_generic_neuron_cell(self):
        self.generic_neuron_cell = IafActivityCell(id="generic_neuron_iaf_cell", 
                                C =                 self.get_bioparameter("neuron_iaf_C").value,
                                thresh =            self.get_bioparameter("neuron_iaf_thresh").value,
                                reset =             self.get_bioparameter("neuron_iaf_reset").value,
                                leak_conductance =  self.get_bioparameter("neuron_iaf_conductance").value,
                                leak_reversal =     self.get_bioparameter("neuron_iaf_leak_reversal").value)  

    def create_syn_and_offset(self):
        self.exc_syn = GradedSynapse(id="exc_syn",
                                conductance =        self.get_bioparameter("exc_syn_conductance").value,
                                delta =              self.get_bioparameter("exc_syn_delta").value,
                                Vth =                self.get_bioparameter("exc_syn_vth").value,
                                erev =               self.get_bioparameter("exc_syn_erev").value,
                                k =                  self.get_bioparameter("exc_syn_k").value)


        self.inh_syn = GradedSynapse(id="inh_syn",
                                conductance =        self.get_bioparameter("inh_syn_conductance").value,
                                delta =              self.get_bioparameter("inh_syn_delta").value,
                                Vth =                self.get_bioparameter("inh_syn_vth").value,
                                erev =               self.get_bioparameter("inh_syn_erev").value,
                                k =                  self.get_bioparameter("inh_syn_k").value)

        self.elec_syn = GapJunction(id="elec_syn",
                               conductance =    self.get_bioparameter("elec_syn_gbase").value)


        self.offset_current = PulseGenerator(id="offset_current",
                                delay=self.get_bioparameter("unphysiological_offset_current_del").value,
                                duration=self.get_bioparameter("unphysiological_offset_current_dur").value,
                                amplitude=self.get_bioparameter("unphysiological_offset_current").value)

    def create_models(self):
        self.cerate_generic_muscle_cell()
        self.cerate_generic_neuron_cell()
        self.create_syn_and_offset()

    # def create_models(self):
        

    #     self.generic_cell = IafActivityCell(id="generic_iaf_cell", 
    #                                 C =                 self.get_bioparameter("iaf_C").value,
    #                                 thresh =            self.get_bioparameter("iaf_thresh").value,
    #                                 reset =             self.get_bioparameter("iaf_reset").value,
    #                                 leak_conductance =  self.get_bioparameter("iaf_conductance").value,
    #                                 leak_reversal =     self.get_bioparameter("iaf_leak_reversal").value,
    #                                 tau1 =              self.get_bioparameter("iaf_tau1").value)


    #     self.exc_syn = GradedSynapse(id="exc_syn",
    #                             conductance =        self.get_bioparameter("exc_syn_conductance").value,
    #                             delta =              self.get_bioparameter("exc_syn_delta").value,
    #                             Vth =                self.get_bioparameter("exc_syn_vth").value,
    #                             erev =               self.get_bioparameter("exc_syn_erev").value,
    #                             k =                  self.get_bioparameter("exc_syn_k").value)


    #     self.inh_syn = GradedSynapse(id="inh_syn",
    #                             conductance =        self.get_bioparameter("inh_syn_conductance").value,
    #                             delta =              self.get_bioparameter("inh_syn_delta").value,
    #                             Vth =                self.get_bioparameter("inh_syn_vth").value,
    #                             erev =               self.get_bioparameter("inh_syn_erev").value,
    #                             k =                  self.get_bioparameter("inh_syn_k").value)

    #     self.elec_syn = GapJunction(id="elec_syn",
    #                            conductance =    self.get_bioparameter("elec_syn_gbase").value)


    #     self.offset_current = PulseGenerator(id="offset_current",
    #                             delay=self.get_bioparameter("unphysiological_offset_current_del").value,
    #                             duration=self.get_bioparameter("unphysiological_offset_current_dur").value,
                                # amplitude=self.get_bioparameter("unphysiological_offset_current").value)
