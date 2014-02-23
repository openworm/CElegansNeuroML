from neuroml import NeuroMLDocument
from neuroml import IafCell
from neuroml import Network
from neuroml import ExpTwoSynapse
from neuroml import Population
from neuroml import Instance
from neuroml import Location
from neuroml import PulseGenerator
from neuroml import ExplicitInput
from neuroml import Projection
from neuroml import Connection
import neuroml.writers as writers
import neuroml.loaders as loaders


import SpreadsheetDataReader

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


net = Network(id="c3o2")

nml_doc.networks.append(net)


offset_current = PulseGenerator(id="offset_current",
                        delay="0ms",
                        duration="1000s",
                        amplitude=params.unphysiological_offset_current.value)

nml_doc.pulse_generators.append(offset_current)

# Use the spreadsheet reader to give a list of all cells and a list of all connections
# This could be replaced with a call to "DatabaseReader" or "OpenWormNeuroLexReader" in future...
cell_names, conns = SpreadsheetDataReader.readDataFromSpreadsheet()

# cell_names = ['ADAL']
cell_names.sort()

# To hold all Cell NeuroML objects vs. names
all_cells = {}

lems_file = ""

for cell in cell_names:
    # build a Population data structure out of the cell name
    pop0 = Population(id=cell, 
                      component=generic_iaf_cell.id,
                      type="populationList")
                      
    inst = Instance(id="0")
    pop0.instances.append(inst)

    # put that Population into the Network data structure from above
    net.populations.append(pop0)

    # also use the cell name to grab the morphology file, as a NeuroML data structure
    #  into the 'all_cells' dict
    cell_file = '../generatedNeuroML2/%s.nml'%cell
    doc = loaders.NeuroMLLoader.load(cell_file)
    all_cells[cell] = doc.cells[0]
    location = doc.cells[0].morphology.segments[0].proximal
    print("Loaded morphology file from: %s, with id: %s, location: (%s, %s, %s)"%(cell_file, all_cells[cell].id, location.x, location.y, location.z))
    
    inst.location = Location(float(location.x), float(location.y), float(location.z))
    
    exp_input = ExplicitInput(target="%s/0/%s"%(pop0.id,generic_iaf_cell.id),
                                             input=offset_current.id)

    if 'P' in cell:
        net.explicit_inputs.append(exp_input)
        
    lems_file = lems_file + '    <OutputColumn id="%s_v" quantity="%s/0/%s/v" />\n'%(cell, cell, generic_iaf_cell.id)

# Get the standard name for a network connection
def get_projection_id(pre, post, synclass, syntype):

    proj_id = "NC_%s_%s_%s"%(pre, post, synclass)
    '''
    if "GapJunction" in syntype:
       proj_id += '_GJ' '''

    return proj_id

for conn in conns:

    # take information about each connection and package it into a 
    # NeuroML Projection data structure
    proj_id = get_projection_id(conn.pre_cell, conn.post_cell, conn.synclass, conn.syntype)
    
    syn = exc_syn.id
    if 'GABA' in conn.synclass:
        syn = inh_syn.id
    
    proj0 = Projection(id=proj_id, \
                       presynaptic_population=conn.pre_cell, 
                       postsynaptic_population=conn.post_cell, 
                       synapse=syn)

    # Get the corresponding Cell for each 
    pre_cell = all_cells[conn.pre_cell]
    post_cell = all_cells[conn.post_cell]

    net.projections.append(proj0)
    
    for conn_id in range(0,conn.number):

        # Add a Connection with the closest locations
        conn0 = Connection(id=conn_id, \
                   pre_cell_id="../%s/0/%s"%(conn.pre_cell, generic_iaf_cell.id),
                   post_cell_id="../%s/0/%s"%(conn.post_cell, generic_iaf_cell.id))

        proj0.connections.append(conn0)



#######   Write to file  ######    

nml_file = 'c3o2.nml'
writers.NeuroMLWriter.write(nml_doc, nml_file)

print("Written network file to: "+nml_file)

lems_file_name = 'LEMS_c3o2.xml.tmp'
lems = open(lems_file_name, 'w')
lems.write(lems_file)

print("Written LEMS file to: "+lems_file_name)


###### Validate the NeuroML ######    

from neuroml.utils import validate_neuroml2

validate_neuroml2(nml_file)
