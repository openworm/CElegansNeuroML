from neuroml import IafCell
from neuroml import ExpTwoSynapse
from neuroml import PulseGenerator

from bioparameters import BioParameter


iaf_leak_reversal =     BioParameter("iaf_leak_reversal", "-70mV", "BlindGuess", "0.1")
iaf_reset =             BioParameter("iaf_reset", "-70mV", "BlindGuess", "0.1")
iaf_thresh =            BioParameter("iaf_thresh", "-50mV", "BlindGuess", "0.1")
iaf_C =                 BioParameter("iaf_C", "0.2nF", "BlindGuess", "0.1")
iaf_conductance =       BioParameter("iaf_conductance", "0.01uS", "BlindGuess", "0.1")


chem_exc_syn_gbase =       BioParameter("chem_exc_syn_gbase", "0.06nS", "BlindGuess", "0.1")
chem_exc_syn_erev =        BioParameter("chem_exc_syn_erev", "0mV", "BlindGuess", "0.1")
chem_exc_syn_rise =        BioParameter("chem_exc_syn_rise", "3ms", "BlindGuess", "0.1")
chem_exc_syn_decay =       BioParameter("chem_exc_syn_decay", "10ms", "BlindGuess", "0.1")

chem_inh_syn_gbase =       BioParameter("chem_inh_syn_gbase", "0.06nS", "BlindGuess", "0.1")
chem_inh_syn_erev =        BioParameter("chem_inh_syn_erev", "-80mV", "BlindGuess", "0.1")
chem_inh_syn_rise =        BioParameter("chem_inh_syn_rise", "3ms", "BlindGuess", "0.1")
chem_inh_syn_decay =       BioParameter("chem_inh_syn_decay", "10ms", "BlindGuess", "0.1")


unphysiological_offset_current = BioParameter("unphysiological_offset_current", "0.25nA", "KnownError", "0")
unphysiological_offset_current_dur = BioParameter("unphysiological_offset_current_dur", "200ms", "KnownError", "0")


generic_cell = IafCell(id="generic_iaf_cell", 
                            C =                 iaf_C.value,
                            thresh =            iaf_thresh.value,
                            reset =             iaf_reset.value,
                            leak_conductance =  iaf_conductance.value,
                            leak_reversal =     iaf_leak_reversal.value)


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


offset_current = PulseGenerator(id="offset_current",
                        delay="0ms",
                        duration=unphysiological_offset_current_dur.value,
                        amplitude=unphysiological_offset_current.value)
