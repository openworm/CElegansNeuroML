
from neuroml import NeuroMLDocument
from neuroml import IafCell
from neuroml import Network
from neuroml import ExpTwoSynapse
from neuroml import Population
from neuroml import PulseGenerator
from neuroml import ExplicitInput
from neuroml import SynapticConnection
import neuroml.writers as writers

import parameters as params

nml_doc = NeuroMLDocument(id="c3o2")

generic_iaf_cell = IafCell(id="generic_iaf_cell", 
                            C =                 params.iaf_C.value,
                            thresh =            params.iaf_thresh.value,
                            reset =             params.iaf_reset.value,
                            leak_conductance =  params.iaf_conductance.value,
                            leak_reversal =     params.iaf_leak_reversal.value)

nml_doc.iaf_cells.append(generic_iaf_cell)


exc_syn = ExpTwoSynapse(id="exc_syn",
                        gbase =         params.chem_exc_syn_gbase.value,
                        erev =          params.chem_exc_syn_erev.value,
                        tau_decay =     params.chem_exc_syn_decay.value,
                        tau_rise =      params.chem_exc_syn_rise.value)

nml_doc.exp_two_synapses.append(exc_syn)

inh_syn = ExpTwoSynapse(id="inh_syn",
                        gbase =         params.chem_inh_syn_gbase.value,
                        erev =          params.chem_inh_syn_erev.value,
                        tau_decay =     params.chem_inh_syn_decay.value,
                        tau_rise =      params.chem_inh_syn_rise.value)

nml_doc.exp_two_synapses.append(inh_syn)

'''
net = Network(id="IafNet")

nml_doc.networks.append(net)

size0 = 5
pop0 = Population(id="IafPop0",
                  component=IafCell0.id,
                  size=size0)

net.populations.append(pop0)

size1 = 5
pop1 = Population(id="IafPop1",
                  component=IafCell0.id,
                  size=size1)

net.populations.append(pop1)'''



#######   Write to file  ######    

nml_file = 'c3o2.nml'
writers.NeuroMLWriter.write(nml_doc, nml_file)

print("Written network file to: "+nml_file)


###### Validate the NeuroML ######    

from neuroml.utils import validate_neuroml2

validate_neuroml2(nml_file)
