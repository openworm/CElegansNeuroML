'''

    Parameters C for c302 still under developemnt!!
    
    Subject to hange without notice!!
    
'''
from neuroml import Cell
from neuroml import ExpTwoSynapse
from neuroml import GapJunction
from neuroml import PulseGenerator

from bioparameters import BioParameter

'''

    The values below are a FIRST APPROXIMATION of conductance based neurons for use in a network to 
    investigate the synaptic connectivity of C elegans
        

'''

level = "C"

leak_cond_density =        BioParameter("leak_cond_density", "0.0193181 mS_per_cm2", "BlindGuess", "0.1")


chem_exc_syn_gbase =       BioParameter("chem_exc_syn_gbase", "0.4nS", "BlindGuess", "0.1")
chem_exc_syn_erev =        BioParameter("chem_exc_syn_erev", "0mV", "BlindGuess", "0.1")
chem_exc_syn_rise =        BioParameter("chem_exc_syn_rise", "1ms", "BlindGuess", "0.1")
chem_exc_syn_decay =       BioParameter("chem_exc_syn_decay", "10ms", "BlindGuess", "0.1")

chem_inh_syn_gbase =       BioParameter("chem_inh_syn_gbase", "1nS", "BlindGuess", "0.1")
chem_inh_syn_erev =        BioParameter("chem_inh_syn_erev", "-55mV", "BlindGuess", "0.1")
chem_inh_syn_rise =        BioParameter("chem_inh_syn_rise", "2ms", "BlindGuess", "0.1")
chem_inh_syn_decay =       BioParameter("chem_inh_syn_decay", "40ms", "BlindGuess", "0.1")

elec_syn_gbase =       BioParameter("elec_syn_gbase", "0.3nS", "BlindGuess", "0.1")

unphysiological_offset_current = BioParameter("unphysiological_offset_current", "0.35nA", "KnownError", "0")
unphysiological_offset_current_dur = BioParameter("unphysiological_offset_current_dur", "2000ms", "KnownError", "0")



generic_cell = Cell(id = "SingleCompMuscleCell")


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
