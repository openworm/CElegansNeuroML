# -*- coding: utf-8 -*-

############################################################

#    A simple script to regenerate the CElegans connectome in NeuroML2
#    Currently uses SpreadsheetDataReader to load connection info 
#    from the CElegansNeuronTables.xls spreadsheet

############################################################

import SpreadsheetDataReader

from neuroml import NeuroMLDocument
from neuroml import Network
from neuroml import Population
from neuroml import Instance
from neuroml import Location
from neuroml import Projection
from neuroml import Connection
import neuroml.writers as writers
import neuroml.loaders as loaders

from random import random
from random import randint

from NeuroMLUtilities import validateNeuroML2
from NeuroMLUtilities import getSegmentIds


def get_projection_id(pre, post, syntype):

    proj_id = "NCXLS_%s_%s"%(pre, post)
    
    if "GapJunction" in syntype:
       proj_id += '_GJ'

    return proj_id


if __name__ == "__main__":

    cell_names, conns = SpreadsheetDataReader.readDataFromSpreadsheet()

    net_id = "CElegansConnectome"

    nml_network_doc = NeuroMLDocument(id=net_id)
    nml_network_doc = NeuroMLDocument(id=net_id)


    net = Network(id=net_id)
    nml_network_doc.networks.append(net)

    all_cells = {}
    
    for cell in cell_names:
        pop0 = Population(id=cell, component=cell, size=1)
        inst = Instance(id="0")
        inst.location = Location(x="0.0", y="0.0", z="0.0")
        pop0.instances.append(inst)
        net.populations.append(pop0)
        cell_file = '../generatedNeuroML2/%s.nml'%cell
        doc = loaders.NeuroMLLoader.load(cell_file)
        all_cells[cell] = doc.cells[0]
        print("Loaded morphology file from: %s, with id: %s"%(cell_file, all_cells[cell].id))

    for conn in conns:

        proj_id = get_projection_id(conn.pre_cell, conn.post_cell, conn.syntype)
        
        proj0 = Projection(id=proj_id, presynaptic_population=conn.pre_cell, postsynaptic_population=conn.post_cell, synapse=conn.synclass)

        pre_cell = all_cells[conn.pre_cell]
        post_cell = all_cells[conn.post_cell]

        pre_segs = getSegmentIds(pre_cell)
        post_segs = getSegmentIds(post_cell)

        for conn_id in range(0,conn.number):

            pre_segment_id = pre_segs[randint(0,  len(pre_cell.morphology.segments)-1)]
            pre_fraction_along = random()
            post_segment_id = post_segs[randint(0,  len(post_cell.morphology.segments)-1)]
            post_fraction_along = random()
    
        
            conn0 = Connection(id=conn_id, \
                           pre_cell_id="../%s/0/%s"%(conn.pre_cell, conn.pre_cell),
                           pre_segment_id = pre_segment_id,
                           pre_fraction_along = pre_fraction_along,
                           post_cell_id="../%s/0/%s"%(conn.post_cell, conn.post_cell),
                           post_segment_id = post_segment_id,
                           post_fraction_along = post_fraction_along)
        
            proj0.connections.append(conn0)

        net.projections.append(proj0)
    

    nml_file = net_id+'.nml'
    writers.NeuroMLWriter.write(nml_network_doc, nml_file)

    print("Written network file to: "+nml_file)



    ###### Validate the NeuroML ######    

    validateNeuroML2(nml_file)



