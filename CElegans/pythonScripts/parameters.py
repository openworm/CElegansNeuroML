


class BioParameter():

	def __init__(self, name, value, source, certainty):
		self.name = name
		self.value = value
		self.source = source
		self.certainty = certainty


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

