'''

    Parameters C for c302 still under developemnt!!
    
    Subject to hange without notice!!
    
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

from neuroml import ExpTwoSynapse
from neuroml import GapJunction
from neuroml import PulseGenerator

from bioparameters import BioParameter

'''

    The values below are a FIRST APPROXIMATION of conductance based neurons for use in a network to 
    investigate the synaptic connectivity of C elegans
        

'''

level = "C"

cell_length =              BioParameter("cell_length", "230.3459", "BlindGuess", "0.1")
cell_diameter =            BioParameter("cell_diameter", "10", "BlindGuess", "0.1")

initial_memb_pot =         BioParameter("initial_memb_pot", "-75 mV", "BlindGuess", "0.1")

specific_capacitance =     BioParameter("specific_capacitance", "1 uF_per_cm2", "BlindGuess", "0.1")

spike_thresh =             BioParameter("spike_thresh", "0 mV", "BlindGuess", "0.1")

leak_cond_density =        BioParameter("leak_cond_density", "0.0193181 mS_per_cm2", "BlindGuess", "0.1")
leak_erev =                BioParameter("leak_erev", "10 mV", "BlindGuess", "0.1")

k_slow_cond_density =      BioParameter("k_slow_cond_density", "0.43584 mS_per_cm2", "BlindGuess", "0.1")
k_slow_erev =              BioParameter("k_slow_erev", "-64.3461 mV", "BlindGuess", "0.1")

k_fast_cond_density =      BioParameter("k_fast_cond_density", "0.399994 mS_per_cm2", "BlindGuess", "0.1")
k_fast_erev =              BioParameter("k_fast_erev", "-54.9998 mV", "BlindGuess", "0.1")

ca_boyle_cond_density =    BioParameter("ca_boyle_cond_density", "0.220209 mS_per_cm2", "BlindGuess", "0.1")
ca_boyle_erev =            BioParameter("ca_boyle_erev", "49.11 mV", "BlindGuess", "0.1")


chem_exc_syn_gbase =       BioParameter("chem_exc_syn_gbase", "0.4nS", "BlindGuess", "0.1")
chem_exc_syn_erev =        BioParameter("chem_exc_syn_erev", "0mV", "BlindGuess", "0.1")
chem_exc_syn_rise =        BioParameter("chem_exc_syn_rise", "1ms", "BlindGuess", "0.1")
chem_exc_syn_decay =       BioParameter("chem_exc_syn_decay", "10ms", "BlindGuess", "0.1")

chem_inh_syn_gbase =       BioParameter("chem_inh_syn_gbase", "1nS", "BlindGuess", "0.1")
chem_inh_syn_erev =        BioParameter("chem_inh_syn_erev", "-55mV", "BlindGuess", "0.1")
chem_inh_syn_rise =        BioParameter("chem_inh_syn_rise", "2ms", "BlindGuess", "0.1")
chem_inh_syn_decay =       BioParameter("chem_inh_syn_decay", "40ms", "BlindGuess", "0.1")

elec_syn_gbase =           BioParameter("elec_syn_gbase", "0.3nS", "BlindGuess", "0.1")

unphysiological_offset_current = BioParameter("unphysiological_offset_current", "0.035nA", "KnownError", "0")
unphysiological_offset_current_dur = BioParameter("unphysiological_offset_current_dur", "20ms", "KnownError", "0")



generic_cell = Cell(id = "GenericCell")

morphology = Morphology()
morphology.id = "morphology_"+generic_cell.id

generic_cell.morphology = morphology

prox_point = Point3DWithDiam(x="0", y="0", z="0", diameter=cell_diameter.value)
dist_point = Point3DWithDiam(x="0", y="0", z=cell_length.value, diameter=cell_diameter.value)

segment = Segment(id="0",
                  name="soma",
                  proximal = prox_point, 
                  distal = dist_point)
  
morphology.segments.append(segment)

generic_cell.biophysical_properties = BiophysicalProperties(id="biophys_"+generic_cell.id)

mp = MembraneProperties()
generic_cell.biophysical_properties.membrane_properties = mp

mp.init_memb_potentials.append(InitMembPotential(value=initial_memb_pot.value))

mp.specific_capacitances.append(SpecificCapacitance(value=specific_capacitance.value))

mp.spike_threshes.append(SpikeThresh(value=spike_thresh.value))

mp.channel_densities.append(ChannelDensity(cond_density=leak_cond_density.value, 
                                           id="Leak_all", 
                                           ion_channel="Leak", 
                                           erev=leak_erev.value,
                                           ion="non_specific"))

mp.channel_densities.append(ChannelDensity(cond_density=k_slow_cond_density.value, 
                                           id="k_slow_all", 
                                           ion_channel="k_slow", 
                                           erev=k_slow_erev.value,
                                           ion="k"))

mp.channel_densities.append(ChannelDensity(cond_density=k_fast_cond_density.value, 
                                           id="k_fast_all", 
                                           ion_channel="k_fast", 
                                           erev=k_fast_erev.value,
                                           ion="k"))

mp.channel_densities.append(ChannelDensity(cond_density=ca_boyle_cond_density.value, 
                                           id="ca_boyle_all", 
                                           ion_channel="ca_boyle", 
                                           erev=ca_boyle_erev.value,
                                           ion="ca"))

ip = IntracellularProperties()
generic_cell.biophysical_properties.intracellular_properties = ip

# NOTE: resistivity/axial resistance not used for single compartment cell models, so value irrelevant!
ip.resistivities.append(Resistivity(value="0.1 kohm_cm"))


# NOTE: Ca reversal potential not calculated by Nernst, so initial_ext_concentration value irrelevant!
species = Species(id="ca", 
                  ion="ca",
                  concentration_model="CaPool",
                  initial_concentration="0 mM",
                  initial_ext_concentration="2E-6 mol_per_cm3")
                  
ip.species.append(species)


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
