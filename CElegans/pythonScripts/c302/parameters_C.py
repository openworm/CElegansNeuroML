'''

    Parameters C for c302 still under developemnt!!
    
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
from neuroml import FixedFactorConcentrationModel

from neuroml import ExpTwoSynapse
from neuroml import GapJunction
from neuroml import PulseGenerator

from bioparameters import c302ModelPrototype

'''

    The values below are a FIRST APPROXIMATION of conductance based neurons for use in a network to 
    investigate the synaptic connectivity of C elegans
        

'''

class ParameterisedModel(c302ModelPrototype):

    def __init__(self):
        self.level = "C"
        self.custom_component_types_definitions = 'cell_C.xml'
        
        self.set_default_bioparameters()

    def set_default_bioparameters(self):

        self.add_bioparameter("cell_diameter", "5", "BlindGuess", "0.1")

        self.add_bioparameter("initial_memb_pot", "-45 mV", "BlindGuess", "0.1")

        self.add_bioparameter("specific_capacitance", "1 uF_per_cm2", "BlindGuess", "0.1")

        self.add_bioparameter("spike_thresh", "-20 mV", "BlindGuess", "0.1")

        self.add_bioparameter("leak_cond_density", "0.005 mS_per_cm2", "BlindGuess", "0.1")
        self.add_bioparameter("leak_erev", "-50 mV", "BlindGuess", "0.1")

        self.add_bioparameter("k_slow_cond_density", "1.8333751019872582 mS_per_cm2", "BlindGuess", "0.1")
        self.add_bioparameter("k_slow_erev", "-60 mV", "BlindGuess", "0.1")

        self.add_bioparameter("k_fast_cond_density", "0.0711643917483308 mS_per_cm2", "BlindGuess", "0.1")
        self.add_bioparameter("k_fast_erev", "-60 mV", "BlindGuess", "0.1")

        self.add_bioparameter("ca_boyle_cond_density", "1.6862775772264702 mS_per_cm2", "BlindGuess", "0.1")
        self.add_bioparameter("ca_boyle_erev", "40 mV", "BlindGuess", "0.1")
        
        self.add_bioparameter("ca_conc_decay_time", "11.5943 ms", "BlindGuess", "0.1")
        self.add_bioparameter("ca_conc_rho", "0.000238919 mol_per_m_per_A_per_s", "BlindGuess", "0.1")


        self.add_bioparameter("chem_exc_syn_gbase", ".1 nS", "BlindGuess", "0.1")
        self.add_bioparameter("chem_exc_syn_erev", "0 mV", "BlindGuess", "0.1")
        self.add_bioparameter("chem_exc_syn_rise", "1 ms", "Bli ndGuess", "0.1")
        self.add_bioparameter("chem_exc_syn_decay", "5 ms", "BlindGuess", "0.1")

        self.add_bioparameter("chem_inh_syn_gbase", ".1 nS", "BlindGuess", "0.1")
        self.add_bioparameter("chem_inh_syn_erev", "-60 mV", "BlindGuess", "0.1")
        self.add_bioparameter("chem_inh_syn_rise", "2 ms", "BlindGuess", "0.1")
        self.add_bioparameter("chem_inh_syn_decay", "40 ms", "BlindGuess", "0.1")

        self.add_bioparameter("elec_syn_gbase", "0.0005 nS", "BlindGuess", "0.1")

        self.add_bioparameter("unphysiological_offset_current", "6.076428433117039 pA", "KnownError", "0")
        self.add_bioparameter("unphysiological_offset_current_del", "0 ms", "KnownError", "0")
        self.add_bioparameter("unphysiological_offset_current_dur", "2000 ms", "KnownError", "0")



    def create_models(self):

        self.generic_cell = Cell(id = "GenericCell")

        morphology = Morphology()
        morphology.id = "morphology_"+self.generic_cell.id

        self.generic_cell.morphology = morphology

        prox_point = Point3DWithDiam(x="0", y="0", z="0", diameter=self.get_bioparameter("cell_diameter").value)
        dist_point = Point3DWithDiam(x="0", y="0", z="0", diameter=self.get_bioparameter("cell_diameter").value)

        segment = Segment(id="0",
                          name="soma",
                          proximal = prox_point, 
                          distal = dist_point)

        morphology.segments.append(segment)

        self.generic_cell.biophysical_properties = BiophysicalProperties(id="biophys_"+self.generic_cell.id)

        mp = MembraneProperties()
        self.generic_cell.biophysical_properties.membrane_properties = mp

        mp.init_memb_potentials.append(InitMembPotential(value=self.get_bioparameter("initial_memb_pot").value))

        mp.specific_capacitances.append(SpecificCapacitance(value=self.get_bioparameter("specific_capacitance").value))

        mp.spike_threshes.append(SpikeThresh(value=self.get_bioparameter("spike_thresh").value))

        mp.channel_densities.append(ChannelDensity(cond_density=self.get_bioparameter("leak_cond_density").value, 
                                                   id="Leak_all", 
                                                   ion_channel="Leak", 
                                                   erev=self.get_bioparameter("leak_erev").value,
                                                   ion="non_specific"))

        mp.channel_densities.append(ChannelDensity(cond_density=self.get_bioparameter("k_slow_cond_density").value, 
                                                   id="k_slow_all", 
                                                   ion_channel="k_slow", 
                                                   erev=self.get_bioparameter("k_slow_erev").value,
                                                   ion="k"))

        mp.channel_densities.append(ChannelDensity(cond_density=self.get_bioparameter("k_fast_cond_density").value, 
                                                   id="k_fast_all", 
                                                   ion_channel="k_fast", 
                                                   erev=self.get_bioparameter("k_fast_erev").value,
                                                   ion="k"))

        mp.channel_densities.append(ChannelDensity(cond_density=self.get_bioparameter("ca_boyle_cond_density").value, 
                                                   id="ca_boyle_all", 
                                                   ion_channel="ca_boyle", 
                                                   erev=self.get_bioparameter("ca_boyle_erev").value,
                                                   ion="ca"))

        ip = IntracellularProperties()
        self.generic_cell.biophysical_properties.intracellular_properties = ip

        # NOTE: resistivity/axial resistance not used for single compartment cell models, so value irrelevant!
        ip.resistivities.append(Resistivity(value="0.1 kohm_cm"))


        # NOTE: Ca reversal potential not calculated by Nernst, so initial_ext_concentration value irrelevant!
        species = Species(id="ca", 
                          ion="ca",
                          concentration_model="CaPool",
                          initial_concentration="0 mM",
                          initial_ext_concentration="2E-6 mol_per_cm3")

        ip.species.append(species)


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
                                delay=self.get_bioparameter("unphysiological_offset_current_del").value,
                                duration=self.get_bioparameter("unphysiological_offset_current_dur").value,
                                amplitude=self.get_bioparameter("unphysiological_offset_current").value)

    
        self.concentration_model = FixedFactorConcentrationModel(id="CaPool",
                                            ion="ca",
                                            resting_conc="0 mM",
                                            decay_constant=self.get_bioparameter("ca_conc_decay_time").value,
                                            rho=self.get_bioparameter("ca_conc_rho").value)
