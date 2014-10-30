from neuroml import IafCell
from neuroml import ExpTwoSynapse
from neuroml import GapJunction
from neuroml import PulseGenerator

from bioparameters import BioParameter

'''

    We are very aware that:
    
        C elegans neurons do NOT behave like Integrate & Fire neurons
        Their synapses are NOT like double exponential, conductance based synapses
        Electrical synapses are very different from event triggered, conductance based synapses
        
    The values below are a FIRST APPROXIMATION of neurons for use in a network to 
    investigate the synaptic connectivity of C elegans
    
    We plan more detailed parameter sets (parameters_B based on Izhikevich or Adaptive
    Exponential I&F; parameters_C based on conductance based neurons) which use this 
    framework.

'''



iaf_leak_reversal =     BioParameter("iaf_leak_reversal", "-70mV", "BlindGuess", "0.1")
iaf_reset =             BioParameter("iaf_reset", "-70mV", "BlindGuess", "0.1")
iaf_thresh =            BioParameter("iaf_thresh", "-50mV", "BlindGuess", "0.1")
iaf_C =                 BioParameter("iaf_C", "0.2nF", "BlindGuess", "0.1")
iaf_conductance =       BioParameter("iaf_conductance", "0.01uS", "BlindGuess", "0.1")
iaf_tau1 =              BioParameter("iaf_tau1", "50ms", "BlindGuess", "0.1")


chem_exc_syn_gbase =       BioParameter("chem_exc_syn_gbase", "0.6nS", "BlindGuess", "0.1")
chem_exc_syn_erev =        BioParameter("chem_exc_syn_erev", "0mV", "BlindGuess", "0.1")
chem_exc_syn_rise =        BioParameter("chem_exc_syn_rise", "3ms", "BlindGuess", "0.1")
chem_exc_syn_decay =       BioParameter("chem_exc_syn_decay", "10ms", "BlindGuess", "0.1")

chem_inh_syn_gbase =       BioParameter("chem_inh_syn_gbase", "2nS", "BlindGuess", "0.1")
chem_inh_syn_erev =        BioParameter("chem_inh_syn_erev", "-80mV", "BlindGuess", "0.1")
chem_inh_syn_rise =        BioParameter("chem_inh_syn_rise", "6ms", "BlindGuess", "0.1")
chem_inh_syn_decay =       BioParameter("chem_inh_syn_decay", "20ms", "BlindGuess", "0.1")

elec_syn_gbase =       BioParameter("elec_syn_gbase", "0.2nS", "BlindGuess", "0.1")


unphysiological_offset_current = BioParameter("unphysiological_offset_current", "0.3nA", "KnownError", "0")
unphysiological_offset_current_dur = BioParameter("unphysiological_offset_current_dur", "2000ms", "KnownError", "0")

class IafActivityCell():
    
    def __init__(self, id, C, thresh, reset, leak_conductance, leak_reversal, tau1):
        self.id = id
        self.C = C
        self.thresh = thresh
        self.reset = reset
        self.leak_conductance = leak_conductance
        self.leak_reversal = leak_reversal
        self.tau1 = tau1
        
        self.custom_component_type_definition = 'cell_B.xml'
        
    
    def export(self, outfile, level, namespace, name_, pretty_print=True):
        outfile.write('    '*level + '<iafCell type="iafActivityCell" id="%s" C="%s" thresh="%s" reset="%s" leakConductance="%s" leakReversal="%s" tau1="%s"/>\n'%(self.id, self.C, self.thresh, self.reset, self.leak_conductance, self.leak_reversal, self.tau1))

generic_cell = IafActivityCell(id = "generic_iaf_cell",
                            C =                 iaf_C.value,
                            thresh =            iaf_thresh.value,
                            reset =             iaf_reset.value,
                            leak_conductance =  iaf_conductance.value,
                            leak_reversal =     iaf_leak_reversal.value,
                            tau1 =              iaf_tau1.value)


exc_syn = ExpTwoSynapse(id="exc_syn",
                        gbase =         chem_exc_syn_gbase.value,
                        erev =          chem_exc_syn_erev.value,
                        tau_decay =     chem_exc_syn_decay.value,
                        tau_rise =      chem_exc_syn_rise.value)
    

inh_syn = ExpTwoSynapse(id="inh_syn",
                        gbase =         chem_inh_syn_gbase.value,
                        erev =          chem_inh_syn_erev.value,
                        tau_decay =     chem_inh_syn_decay.value,
                        tau_rise =      chem_inh_syn_rise.value)

elec_syn = GapJunction(id="elec_syn",
                       conductance =    elec_syn_gbase.value)


offset_current = PulseGenerator(id="offset_current",
                        delay="0ms",
                        duration=unphysiological_offset_current_dur.value,
                        amplitude=unphysiological_offset_current.value)
