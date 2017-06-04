'''

    Parameters C2 for c302 still under developemnt!!
    
    
    C2 adds analogue synapses... Might be merged into C or bumped up to D
    
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

    The values below are a FIRST APPROXIMATION of conductance based neurons for use in a network to 
    investigate the synaptic connectivity of C elegans
        
'''

class ParameterisedModel(ParameterisedModel_C):

    def __init__(self):
        super(ParameterisedModel, self).__init__()
        self.level = "C2"
        self.custom_component_types_definitions = ['cell_C.xml', 'custom_muscle_components.xml']
        
        self.set_default_bioparameters()
        print("Set default parameters for %s"%self.level)


    def set_default_bioparameters(self):

        self.add_bioparameter("cell_diameter", "5", "BlindGuess", "0.1")
        self.add_bioparameter("muscle_length", "20", "BlindGuess", "0.1")

        self.add_bioparameter("initial_memb_pot", "-60 mV", "BlindGuess", "0.1")
        self.add_bioparameter("muscle_initial_memb_pot", "-28 mV", "BlindGuess", "0.1")

        self.add_bioparameter("specific_capacitance", "1 uF_per_cm2", "BlindGuess", "0.1")
        self.add_bioparameter("muscle_specific_capacitance", "1 uF_per_cm2", "BlindGuess", "0.1")

        self.add_bioparameter("neuron_spike_thresh", "-55 mV", "BlindGuess", "0.1")
        self.add_bioparameter("muscle_spike_thresh", "-10 mV", "BlindGuess", "0.1")

        self.add_bioparameter("muscle_leak_cond_density", "0.0172 mS_per_cm2", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_leak_cond_density", "0.002 mS_per_cm2", "BlindGuess", "0.1")

        self.add_bioparameter("leak_erev", "-60 mV", "BlindGuess", "0.1")
        self.add_bioparameter("muscle_leak_erev", "-13 mV", "BlindGuess", "0.1")

        self.add_bioparameter("muscle_k_slow_cond_density", "0.564 mS_per_cm2", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_k_slow_cond_density", "0.45833751019872582 mS_per_cm2", "BlindGuess", "0.1")
        self.add_bioparameter("k_slow_erev", "-60 mV", "BlindGuess", "0.1")
        self.add_bioparameter("muscle_k_slow_erev", "-70 mV", "BlindGuess", "0.1")

        #self.add_bioparameter("muscle_k_fast_cond_density", "1.015 mS_per_cm2", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_k_fast_cond_density", "0.042711643917483308 mS_per_cm2", "BlindGuess", "0.1")
        self.add_bioparameter("k_fast_erev", "-70 mV", "BlindGuess", "0.1")
        #self.add_bioparameter("muscle_k_fast_erev", "-50 mV", "BlindGuess", "0.1")

        self.add_bioparameter("muscle_ca_boyle_cond_density", "0.284 mS_per_cm2", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_ca_boyle_cond_density", "1.812775772264702 mS_per_cm2", "BlindGuess", "0.1")

        self.add_bioparameter("ca_boyle_erev", "10 mV", "BlindGuess", "0.1")
        self.add_bioparameter("muscle_ca_boyle_erev", "46 mV", "BlindGuess", "0.1")
        
        self.add_bioparameter("ca_conc_decay_time", "13.811870945509265 ms", "BlindGuess", "0.1")
        self.add_bioparameter("ca_conc_rho", "0.000238919 mol_per_m_per_A_per_s", "BlindGuess", "0.1")

        self.add_bioparameter("neuron_to_neuron_exc_syn_conductance", "0.49 nS", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_to_muscle_exc_syn_conductance", "3.46 nS", "BlindGuess", "0.1")
        
        self.add_bioparameter("exc_syn_delta", "5 mV", "BlindGuess", "0.1")
        self.add_bioparameter("exc_syn_vth", "00 mV", "BlindGuess", "0.1")
        self.add_bioparameter("exc_syn_erev", "-10 mV", "BlindGuess", "0.1")
        self.add_bioparameter("exc_syn_k", "0.5per_ms", "BlindGuess", "0.1")

        self.add_bioparameter("neuron_to_muscle_exc_syn_delta", "5 mV", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_to_muscle_exc_syn_vth", "00 mV", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_to_muscle_exc_syn_erev", "00 mV", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_to_muscle_exc_syn_k", "0.025per_ms", "BlindGuess", "0.1")

        self.add_bioparameter("neuron_to_neuron_inh_syn_conductance", "0.29 nS", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_to_muscle_inh_syn_conductance", "1.29 nS", "BlindGuess", "0.1")
        
        self.add_bioparameter("inh_syn_delta", "5 mV", "BlindGuess", "0.1")
        self.add_bioparameter("inh_syn_vth", "0 mV", "BlindGuess", "0.1")
        self.add_bioparameter("inh_syn_erev", "-70 mV", "BlindGuess", "0.1")
        self.add_bioparameter("inh_syn_k", "0.015per_ms", "BlindGuess", "0.1")

        self.add_bioparameter("neuron_to_muscle_inh_syn_delta", "5 mV", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_to_muscle_inh_syn_vth", "0 mV", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_to_muscle_inh_syn_erev", "-50 mV", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_to_muscle_inh_syn_k", "0.025per_ms", "BlindGuess", "0.1")
        
        self.add_bioparameter("neuron_to_neuron_elec_syn_gbase", "0.01252 nS", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_to_muscle_elec_syn_gbase", "0.00152 nS", "BlindGuess", "0.1")
        self.add_bioparameter("muscle_to_muscle_elec_syn_gbase", "0.0052 nS", "BlindGuess", "0.1")

        self.add_bioparameter("unphysiological_offset_current", "5.135697186048022 pA", "KnownError", "0")
        self.add_bioparameter("unphysiological_offset_current_del", "0 ms", "KnownError", "0")
        self.add_bioparameter("unphysiological_offset_current_dur", "2000 ms", "KnownError", "0")



    def create_models(self):
        self.create_generic_muscle_cell()
        self.create_generic_neuron_cell()
        self.create_offsetcurrent_concentrationmodel()
        self.create_neuron_to_neuron_syn()
        self.create_neuron_to_muscle_syn()
        self.create_muscle_to_muscle_syn()


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

        mp.init_memb_potentials.append(InitMembPotential(value=self.get_bioparameter("muscle_initial_memb_pot").value))

        mp.specific_capacitances.append(SpecificCapacitance(value=self.get_bioparameter("muscle_specific_capacitance").value))

        mp.spike_threshes.append(SpikeThresh(value=self.get_bioparameter("muscle_spike_thresh").value))

        mp.channel_densities.append(ChannelDensity(cond_density=self.get_bioparameter("muscle_leak_cond_density").value, 
                                                   id="Leak_all", 
                                                   ion_channel="Leak", 
                                                   erev=self.get_bioparameter("muscle_leak_erev").value,
                                                   ion="non_specific"))

        mp.channel_densities.append(ChannelDensity(cond_density=self.get_bioparameter("muscle_k_slow_cond_density").value, 
                                                   id="k_slow_all", 
                                                   ion_channel="k_muscle", 
                                                   erev=self.get_bioparameter("muscle_k_slow_erev").value,
                                                   ion="k"))

        #mp.channel_densities.append(ChannelDensity(cond_density=self.get_bioparameter("muscle_k_fast_cond_density").value, 
        #                                           id="k_fast_all", 
        #                                           ion_channel="k_fast", 
        #                                           erev=self.get_bioparameter("muscle_k_fast_erev").value,
        #                                           ion="k"))

        mp.channel_densities.append(ChannelDensity(cond_density=self.get_bioparameter("muscle_ca_boyle_cond_density").value, 
                                                   id="ca_boyle_all", 
                                                   ion_channel="ca_muscle", 
                                                   erev=self.get_bioparameter("muscle_ca_boyle_erev").value,
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
                                delta =              self.get_bioparameter("neuron_to_muscle_exc_syn_delta").value,
                                Vth =                self.get_bioparameter("neuron_to_muscle_exc_syn_vth").value,
                                erev =               self.get_bioparameter("neuron_to_muscle_exc_syn_erev").value,
                                k =                  self.get_bioparameter("neuron_to_muscle_exc_syn_k").value)


        self.neuron_to_muscle_inh_syn = GradedSynapse(id="neuron_to_muscle_inh_syn",
                                conductance =        self.get_bioparameter("neuron_to_muscle_inh_syn_conductance").value,
                                delta =              self.get_bioparameter("neuron_to_muscle_inh_syn_delta").value,
                                Vth =                self.get_bioparameter("neuron_to_muscle_inh_syn_vth").value,
                                erev =               self.get_bioparameter("neuron_to_muscle_inh_syn_erev").value,
                                k =                  self.get_bioparameter("neuron_to_muscle_inh_syn_k").value)

        self.neuron_to_muscle_elec_syn = GapJunction(id="neuron_to_muscle_elec_syn",
                               conductance =    self.get_bioparameter("neuron_to_muscle_elec_syn_gbase").value)


    def create_muscle_to_muscle_syn(self):
        self.muscle_to_muscle_elec_syn = GapJunction(id="muscle_to_muscle_elec_syn",
                               conductance =    self.get_bioparameter("muscle_to_muscle_elec_syn_gbase").value)





class SwitchedGapJunction():
    def __init__(self, id, conductance, delay):
        self.id = id
        self.conductance = conductance
        self.delay = delay

    def export(self, outfile, level, namespace, name_, pretty_print=True):
        outfile.write(
            '    ' * level + '<switchedGapJunction id="%s" conductance="%s" delay="%s" />\n' % (
            self.id, self.conductance, self.delay))


class DelayedGapJunction():
    def __init__(self, id, weight, conductance, sigma, mu):
        self.id = id
        self.weight = weight
        self.conductance = conductance
        self.sigma = sigma
        self.mu = mu

    def export(self, outfile, level, namespace, name_, pretty_print=True):
        outfile.write(
            '    ' * level + '<delayedGapJunction id="%s" weight="%s" conductance="%s" sigma="%s" mu="%s" />\n'
            % (self.id, self.weight, self.conductance, self.sigma, self.mu))

    def __repr__(self):
        return "DelayedGapJunction(id=%s, weight=%s, conductance=%s, sigma=%s, mu=%s)" % (self.id, self.weight, self.conductance, self.sigma, self.mu)

class DelayedGradedSynapse():
    def __init__(self, id=None, weight=1, conductance=None, delta=None, vth=None, k=None, erev=None, sigma=None, mu=None):
        self.id = id
        self.weight = weight
        self.conductance = conductance
        self.delta = delta
        self.vth = vth
        self.k = k
        self.erev = erev
        self.sigma = sigma
        self.mu = mu

    def export(self, outfile, level, namespace, name_, pretty_print=True):
        outfile.write(
            '    ' * level + '<delayedGradedSynapse id="%s" weight="%s" conductance="%s" delta="%s" Vth="%s" k="%s" erev="%s" sigma="%s" mu="%s" />\n'
            % (self.id, self.weight, self.conductance, self.delta, self.vth, self.k, self.erev, self.sigma, self.mu))

    def __repr__(self):
        return "DelayedGradedSynapse(id=%s, weight=%s, conductance=%s, delta=%s, vth=%s, k=%s, erev=%s, sigma=%s, mu=%s)" \
               % (self.id, self.weight, self.conductance, self.delta, self.vth, self.k, self.erev, self.sigma, self.mu)
