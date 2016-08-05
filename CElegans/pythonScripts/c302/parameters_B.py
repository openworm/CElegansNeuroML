
from neuroml import ExpTwoSynapse
from neuroml import GapJunction
from neuroml import PulseGenerator

from bioparameters import c302ModelPrototype

'''

    We are very aware that:
    
        C elegans neurons do NOT behave like Integrate & Fire neurons
        Their synapses are NOT like double exponential, conductance based synapses
        Electrical synapses are very different from event triggered, conductance based synapses
        
    The values below are a FIRST APPROXIMATION of neurons for use in a network to 
    investigate the synaptic connectivity of C elegans
    
    We plan more detailed parameter sets (parameters_B based on more detailed neurons & including 
    electrical connections; parameters_C based on conductance based neurons) which use this 
    framework.

'''

class ParameterisedModel(c302ModelPrototype):

    def __init__(self):
        self.level = "B"
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

        self.add_bioparameter("chem_exc_syn_gbase", "0.01nS", "BlindGuess", "0.1")
        self.add_bioparameter("chem_exc_syn_erev", "0mV", "BlindGuess", "0.1")
        self.add_bioparameter("chem_exc_syn_rise", "3ms", "BlindGuess", "0.1")
        self.add_bioparameter("chem_exc_syn_decay", "10ms", "BlindGuess", "0.1")
        

        self.add_bioparameter("chem_inh_syn_gbase", "0.01nS", "BlindGuess", "0.1")
        self.add_bioparameter("chem_inh_syn_erev", "-80mV", "BlindGuess", "0.1")
        self.add_bioparameter("chem_inh_syn_rise", "3ms", "BlindGuess", "0.1")
        self.add_bioparameter("chem_inh_syn_decay", "10ms", "BlindGuess", "0.1")

        self.add_bioparameter("elec_syn_gbase", "0.1 nS", "BlindGuess", "0.1")


        self.add_bioparameter("unphysiological_offset_current", "3pA", "KnownError", "0")
        self.add_bioparameter("unphysiological_offset_current_del", "0ms", "KnownError", "0")
        self.add_bioparameter("unphysiological_offset_current_dur", "2000ms", "KnownError", "0")
        
    def cerate_generic_muscle_cell(self):
        self.generic_muscle_cell = IafActivityCell(id="generic_muscle_iaf_cell", 
                                C =                 self.get_bioparameter("muscle_iaf_C").value,
                                thresh =            self.get_bioparameter("muscle_iaf_thresh").value,
                                reset =             self.get_bioparameter("muscle_iaf_reset").value,
                                leak_conductance =  self.get_bioparameter("muscle_iaf_conductance").value,
                                leak_reversal =     self.get_bioparameter("muscle_iaf_leak_reversal").value,
                                tau1 =              self.get_bioparameter("muscle_iaf_tau1").value)   
   
    def cerate_generic_neuron_cell(self):
        self.generic_neuron_cell = IafActivityCell(id="generic_neuron_iaf_cell", 
                                C =                 self.get_bioparameter("neuron_iaf_C").value,
                                thresh =            self.get_bioparameter("neuron_iaf_thresh").value,
                                reset =             self.get_bioparameter("neuron_iaf_reset").value,
                                leak_conductance =  self.get_bioparameter("neuron_iaf_conductance").value,
                                leak_reversal =     self.get_bioparameter("neuron_iaf_leak_reversal").value,
                                tau1 =              self.get_bioparameter("neuron_iaf_tau1").value)  

    def create_syn_and_offset(self):        

        self.exc_syn = ExpTwoSynapse(id="exc_syn",
                                gbase =         self.get_bioparameter("chem_exc_syn_gbase").value,
                                erev =          self.get_bioparameter("chem_exc_syn_erev").value,
                                tau_decay =     self.get_bioparameter("chem_exc_syn_decay").value,
                                tau_rise =      self.get_bioparameter("chem_exc_syn_rise").value)


        self.inh_syn = ExpTwoSynapse(id="inh_syn",
                                gbase =         self.get_bioparameter("chem_inh_syn_gbase").value,
                                erev =          self.get_bioparameter("chem_inh_syn_erev").value,
                                tau_decay =     self.get_bioparameter("chem_inh_syn_decay").value,
                                tau_rise =      self.get_bioparameter("chem_inh_syn_rise").value)
                      
                                
        self.elec_syn = GapJunction(id="elec_syn",
                                conductance =    self.get_bioparameter("elec_syn_gbase").value)


        self.offset_current = PulseGenerator(id="offset_current",
                                delay= self.get_bioparameter("unphysiological_offset_current_del").value,
                                duration= self.get_bioparameter("unphysiological_offset_current_dur").value,
                                amplitude= self.get_bioparameter("unphysiological_offset_current").value)

    def create_models(self):
        self.cerate_generic_muscle_cell()
        self.cerate_generic_neuron_cell()
        self.create_syn_and_offset()
                        

class IafActivityCell():
    
    def __init__(self, id, C, thresh, reset, leak_conductance, leak_reversal, tau1):
        self.id = id
        self.C = C
        self.thresh = thresh
        self.reset = reset
        self.leak_conductance = leak_conductance
        self.leak_reversal = leak_reversal
        self.tau1 = tau1
        
        
    
    def export(self, outfile, level, namespace, name_, pretty_print=True):
        outfile.write('    '*level + '<iafCell type="iafActivityCell" id="%s" C="%s" thresh="%s" reset="%s" leakConductance="%s" leakReversal="%s" tau1="%s"/>\n'%(self.id, self.C, self.thresh, self.reset, self.leak_conductance, self.leak_reversal, self.tau1))

