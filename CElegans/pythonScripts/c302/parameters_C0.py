'''

    Parameters C0 for c302 still under developemnt!!
    
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


from parameters_C import ParameterisedModel as ParameterisedModel_C

'''

    Simplified conductance based cell model (Morris Lecar like)
    
    No fast K channel. No inactivation on Ca channel. No [Ca2+] dependence 
        

'''

class ParameterisedModel(ParameterisedModel_C):

    def __init__(self):
        self.level = "C0"
        self.custom_component_types_definitions = 'cell_C.xml'
        
        self.set_default_bioparameters()
        print("Set default parameters for %s"%self.level)

    def set_default_bioparameters(self):

        self.add_bioparameter("cell_diameter", "5", "BlindGuess", "0.1")
        self.add_bioparameter("muscle_length", "20", "BlindGuess", "0.1")

        self.add_bioparameter("initial_memb_pot", "-45 mV", "BlindGuess", "0.1")

        self.add_bioparameter("specific_capacitance", "1 uF_per_cm2", "BlindGuess", "0.1")

        self.add_bioparameter("muscle_spike_thresh", "-20 mV", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_spike_thresh", "-20 mV", "BlindGuess", "0.1")

        self.add_bioparameter("muscle_leak_cond_density", "0.005 mS_per_cm2", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_leak_cond_density", "0.005 mS_per_cm2", "BlindGuess", "0.1")
        self.add_bioparameter("leak_erev", "-50 mV", "BlindGuess", "0.1")

        self.add_bioparameter("muscle_k_slow_cond_density", "1.7 mS_per_cm2", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_k_slow_cond_density", "1.0 mS_per_cm2", "BlindGuess", "0.1")
        self.add_bioparameter("k_slow_erev", "-60 mV", "BlindGuess", "0.1")

        self.add_bioparameter("muscle_ca_simple_cond_density", "1.2 mS_per_cm2", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_ca_simple_cond_density", "0.1 mS_per_cm2", "BlindGuess", "0.1")
        self.add_bioparameter("ca_simple_erev", "40 mV", "BlindGuess", "0.1")
        
        self.add_bioparameter("ca_conc_decay_time", "200 ms", "BlindGuess", "0.1")
        self.add_bioparameter("ca_conc_rho", "0.0002 mol_per_m_per_A_per_s", "BlindGuess", "0.1")


        self.add_bioparameter("neuron_to_neuron_exc_syn_conductance", "0.09 nS", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_to_muscle_exc_syn_conductance", "0.09 nS", "BlindGuess", "0.1")
        
        self.add_bioparameter("exc_syn_delta", "5 mV", "BlindGuess", "0.1")
        self.add_bioparameter("exc_syn_vth", "0 mV", "BlindGuess", "0.1")
        self.add_bioparameter("exc_syn_erev", "0 mV", "BlindGuess", "0.1")
        self.add_bioparameter("exc_syn_k", "0.025per_ms", "BlindGuess", "0.1")

        self.add_bioparameter("neuron_to_neuron_inh_syn_conductance", "0.2 nS", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_to_muscle_inh_syn_conductance", "0.2 nS", "BlindGuess", "0.1")
        
        self.add_bioparameter("inh_syn_delta", "5 mV", "BlindGuess", "0.1")
        self.add_bioparameter("inh_syn_vth", "-30 mV", "BlindGuess", "0.1")
        self.add_bioparameter("inh_syn_erev", "-70 mV", "BlindGuess", "0.1")
        self.add_bioparameter("inh_syn_k", "0.025per_ms", "BlindGuess", "0.1")
        

        self.add_bioparameter("neuron_to_neuron_elec_syn_gbase", "0.0001 nS", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_to_muscle_elec_syn_gbase", "0.0001 nS", "BlindGuess", "0.1")

        self.add_bioparameter("unphysiological_offset_current", "6.076428433117039 pA", "KnownError", "0")
        self.add_bioparameter("unphysiological_offset_current_del", "0 ms", "KnownError", "0")
        self.add_bioparameter("unphysiological_offset_current_dur", "2000 ms", "KnownError", "0")



    def create_models(self):
        self.create_generic_muscle_cell()
        self.create_generic_neuron_cell()
        self.create_offsetcurrent_concentrationmodel()
        self.create_neuron_to_neuron_syn()
        self.create_neuron_to_muscle_syn()


    def create_generic_muscle_cell(self):

        self.generic_muscle_cell = Cell(id = "GenericMuscleCell")

        morphology = Morphology()
        morphology.id = "morphology_"+self.generic_muscle_cell.id

        self.generic_muscle_cell.morphology = morphology

        prox_point = Point3DWithDiam(x="0", y="0", z="0", diameter=self.get_bioparameter("cell_diameter").value)
        dist_point = Point3DWithDiam(x="0", y=self.get_bioparameter("muscle_length").value, z="0", diameter=self.get_bioparameter("cell_diameter").value)

        segment = Segment(id="0",
                          name="soma",
                          proximal = prox_point, 
                          distal = dist_point)

        morphology.segments.append(segment)

        self.generic_muscle_cell.biophysical_properties = BiophysicalProperties(id="biophys_"+self.generic_muscle_cell.id)

        mp = MembraneProperties()
        self.generic_muscle_cell.biophysical_properties.membrane_properties = mp

        mp.init_memb_potentials.append(InitMembPotential(value=self.get_bioparameter("initial_memb_pot").value))

        mp.specific_capacitances.append(SpecificCapacitance(value=self.get_bioparameter("specific_capacitance").value))

        mp.spike_threshes.append(SpikeThresh(value=self.get_bioparameter("muscle_spike_thresh").value))

        mp.channel_densities.append(ChannelDensity(cond_density=self.get_bioparameter("muscle_leak_cond_density").value, 
                                                   id="Leak_all", 
                                                   ion_channel="Leak", 
                                                   erev=self.get_bioparameter("leak_erev").value,
                                                   ion="non_specific"))

        mp.channel_densities.append(ChannelDensity(cond_density=self.get_bioparameter("muscle_k_slow_cond_density").value, 
                                                   id="k_slow_all", 
                                                   ion_channel="k_slow", 
                                                   erev=self.get_bioparameter("k_slow_erev").value,
                                                   ion="k"))
        '''
        mp.channel_densities.append(ChannelDensity(cond_density=self.get_bioparameter("muscle_k_fast_cond_density").value, 
                                                   id="k_fast_all", 
                                                   ion_channel="k_fast", 
                                                   erev=self.get_bioparameter("k_fast_erev").value,
                                                   ion="k"))'''

        mp.channel_densities.append(ChannelDensity(cond_density=self.get_bioparameter("muscle_ca_simple_cond_density").value, 
                                                   id="ca_simple_all", 
                                                   ion_channel="ca_simple", 
                                                   erev=self.get_bioparameter("ca_simple_erev").value,
                                                   ion="ca"))

        ip = IntracellularProperties()
        self.generic_muscle_cell.biophysical_properties.intracellular_properties = ip

        # NOTE: resistivity/axial resistance not used for single compartment cell models, so value irrelevant!
        ip.resistivities.append(Resistivity(value="0.1 kohm_cm"))


        # NOTE: Ca reversal potential not calculated by Nernst, so initial_ext_concentration value irrelevant!
        species = Species(id="ca", 
                          ion="ca",
                          concentration_model="CaPool",
                          initial_concentration="0 mM",
                          initial_ext_concentration="2E-6 mol_per_cm3")

        ip.species.append(species)  


    def create_generic_neuron_cell(self):

        self.generic_neuron_cell = Cell(id = "GenericNeuronCell")

        morphology = Morphology()
        morphology.id = "morphology_"+self.generic_neuron_cell.id

        self.generic_neuron_cell.morphology = morphology

        prox_point = Point3DWithDiam(x="0", y="0", z="0", diameter=self.get_bioparameter("cell_diameter").value)
        dist_point = Point3DWithDiam(x="0", y="0", z="0", diameter=self.get_bioparameter("cell_diameter").value)

        segment = Segment(id="0",
                          name="soma",
                          proximal = prox_point, 
                          distal = dist_point)

        morphology.segments.append(segment)

        self.generic_neuron_cell.biophysical_properties = BiophysicalProperties(id="biophys_"+self.generic_neuron_cell.id)

        mp = MembraneProperties()
        self.generic_neuron_cell.biophysical_properties.membrane_properties = mp

        mp.init_memb_potentials.append(InitMembPotential(value=self.get_bioparameter("initial_memb_pot").value))

        mp.specific_capacitances.append(SpecificCapacitance(value=self.get_bioparameter("specific_capacitance").value))

        mp.spike_threshes.append(SpikeThresh(value=self.get_bioparameter("neuron_spike_thresh").value))

        mp.channel_densities.append(ChannelDensity(cond_density=self.get_bioparameter("neuron_leak_cond_density").value, 
                                                   id="Leak_all", 
                                                   ion_channel="Leak", 
                                                   erev=self.get_bioparameter("leak_erev").value,
                                                   ion="non_specific"))

        mp.channel_densities.append(ChannelDensity(cond_density=self.get_bioparameter("neuron_k_slow_cond_density").value, 
                                                   id="k_slow_all", 
                                                   ion_channel="k_slow", 
                                                   erev=self.get_bioparameter("k_slow_erev").value,
                                                   ion="k"))
        '''
        mp.channel_densities.append(ChannelDensity(cond_density=self.get_bioparameter("neuron_k_fast_cond_density").value, 
                                                   id="k_fast_all", 
                                                   ion_channel="k_fast", 
                                                   erev=self.get_bioparameter("k_fast_erev").value,
                                                   ion="k"))'''

        mp.channel_densities.append(ChannelDensity(cond_density=self.get_bioparameter("neuron_ca_simple_cond_density").value, 
                                                   id="ca_simple_all", 
                                                   ion_channel="ca_simple", 
                                                   erev=self.get_bioparameter("ca_simple_erev").value,
                                                   ion="ca"))

        ip = IntracellularProperties()
        self.generic_neuron_cell.biophysical_properties.intracellular_properties = ip

        # NOTE: resistivity/axial resistance not used for single compartment cell models, so value irrelevant!
        ip.resistivities.append(Resistivity(value="0.1 kohm_cm"))


        # NOTE: Ca reversal potential not calculated by Nernst, so initial_ext_concentration value irrelevant!
        species = Species(id="ca", 
                          ion="ca",
                          concentration_model="CaPool",
                          initial_concentration="0 mM",
                          initial_ext_concentration="2E-6 mol_per_cm3")

        ip.species.append(species)




    def create_neuron_to_neuron_syn(self):
        self.neuron_to_neuron_exc_syn = GradedSynapse(id="neuron_to_neuron_exc_syn",
                                conductance =        self.get_bioparameter("neuron_to_neuron_exc_syn_conductance").value,
                                delta =              self.get_bioparameter("exc_syn_delta").value,
                                Vth =                self.get_bioparameter("exc_syn_vth").value,
                                erev =               self.get_bioparameter("exc_syn_erev").value,
                                k =                  self.get_bioparameter("exc_syn_k").value)


        self.neuron_to_neuron_inh_syn = GradedSynapse(id="neuron_to_neuron_inh_syn",
                                conductance =        self.get_bioparameter("neuron_to_neuron_inh_syn_conductance").value,
                                delta =              self.get_bioparameter("inh_syn_delta").value,
                                Vth =                self.get_bioparameter("inh_syn_vth").value,
                                erev =               self.get_bioparameter("inh_syn_erev").value,
                                k =                  self.get_bioparameter("inh_syn_k").value)

        self.neuron_to_neuron_elec_syn = GapJunction(id="neuron_to_neuron_elec_syn",
                               conductance =    self.get_bioparameter("neuron_to_neuron_elec_syn_gbase").value)



    def create_neuron_to_muscle_syn(self):
        self.neuron_to_muscle_exc_syn = GradedSynapse(id="neuron_to_muscle_exc_syn",
                                conductance =        self.get_bioparameter("neuron_to_muscle_exc_syn_conductance").value,
                                delta =              self.get_bioparameter("exc_syn_delta").value,
                                Vth =                self.get_bioparameter("exc_syn_vth").value,
                                erev =               self.get_bioparameter("exc_syn_erev").value,
                                k =                  self.get_bioparameter("exc_syn_k").value)


        self.neuron_to_muscle_inh_syn = GradedSynapse(id="neuron_to_muscle_inh_syn",
                                conductance =        self.get_bioparameter("neuron_to_muscle_inh_syn_conductance").value,
                                delta =              self.get_bioparameter("inh_syn_delta").value,
                                Vth =                self.get_bioparameter("inh_syn_vth").value,
                                erev =               self.get_bioparameter("inh_syn_erev").value,
                                k =                  self.get_bioparameter("inh_syn_k").value)

        self.neuron_to_muscle_elec_syn = GapJunction(id="neuron_to_muscle_elec_syn",
                               conductance =    self.get_bioparameter("neuron_to_muscle_elec_syn_gbase").value)


