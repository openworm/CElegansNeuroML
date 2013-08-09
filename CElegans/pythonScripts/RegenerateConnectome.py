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
from NeuroMLUtilities import get3DPosition

import math


def get_projection_id(pre, post, syntype):

    proj_id = "NCXLS_%s_%s"%(pre, post)
    
    if "GapJunction" in syntype:
       proj_id += '_GJ'

    return proj_id


if __name__ == "__main__":

	# Use the spreadsheet reader to give a list of all cells and a list of all connections
    cell_names, conns = SpreadsheetDataReader.readDataFromSpreadsheet()

    net_id = "CElegansConnectome"

    nml_network_doc = NeuroMLDocument(id=net_id)
    nml_network_doc = NeuroMLDocument(id=net_id) # are we doing this twice on purpose?

	# Create a NeuroML Network data structure to hold on to all the connection info.
    net = Network(id=net_id)
    nml_network_doc.networks.append(net)

    all_cells = {}
    
    for cell in cell_names:
    	# build a Population data structure out of the cell name
        pop0 = Population(id=cell, component=cell, size=1)
        inst = Instance(id="0")
        inst.location = Location(x="0.0", y="0.0", z="0.0")
        pop0.instances.append(inst)
        
        # put that Population into the Network data structure from above
        net.populations.append(pop0)
        
        # also use the cell name to grab the morphology file, as a NeuroML data structure
        #  into the 'all_cells' dict
        cell_file = '../generatedNeuroML2/%s.nml'%cell
        doc = loaders.NeuroMLLoader.load(cell_file)
        all_cells[cell] = doc.cells[0]
        print("Loaded morphology file from: %s, with id: %s"%(cell_file, all_cells[cell].id))

	
    for conn in conns:
		# take information about each connection and package it into a 
		#  neuroML Projection data structure
        proj_id = get_projection_id(conn.pre_cell, conn.post_cell, conn.syntype)
        proj0 = Projection(id=proj_id, \
        		     	   presynaptic_population=conn.pre_cell, 
        		      	   postsynaptic_population=conn.post_cell, 
        		       	   synapse=conn.synclass)

        pre_cell = all_cells[conn.pre_cell]
        post_cell = all_cells[conn.post_cell]

        pre_segs = getSegmentIds(pre_cell)
        post_segs = getSegmentIds(post_cell)
        print "Projection between %s and %s has %i conns"%(conn.pre_cell,conn.post_cell,conn.number)

        for conn_id in range(0,conn.number):

            #print "--- Conn %i"%conn_id
            best_dist = 1e6
            num_to_try = len(pre_segs)*len(post_segs)
            
            for i in range(num_to_try):
                pre_segment_index = randint(0,  len(pre_cell.morphology.segments)-1)
                pre_segment_id = pre_segs[pre_segment_index]
                pre_fraction_along = random()
                post_segment_index = randint(0,  len(post_cell.morphology.segments)-1)
                post_segment_id = post_segs[post_segment_index]
                post_fraction_along = random()
    
                pre_x, pre_y,pre_z = get3DPosition(pre_cell, pre_segment_index, pre_fraction_along)
                post_x, post_y,post_z = get3DPosition(post_cell, post_segment_index, post_fraction_along)

                dist = math.sqrt(math.pow(pre_x-post_x,2)+math.pow(pre_y-post_y,2)+math.pow(pre_z-post_z,2))
                #print dist
            
                if dist < best_dist:
                    best_dist = dist
                    #print "Best: %f"%best_dist
                    best_pre_seg = pre_segment_id
                    best_pre_fract = pre_fraction_along
                    best_post_seg = post_segment_id
                    best_post_fract = post_fraction_along
                    

            
        
            conn0 = Connection(id=conn_id, \

                           pre_cell_id="../%s/0/%s"%(conn.pre_cell, conn.pre_cell),
                           pre_segment_id = best_pre_seg,
                           pre_fraction_along = best_pre_fract,
                           post_cell_id="../%s/0/%s"%(conn.post_cell, conn.post_cell),
                           post_segment_id = best_post_seg,
                           post_fraction_along = best_post_fract)
        
            proj0.connections.append(conn0)

        net.projections.append(proj0)
    

    nml_file = net_id+'.nml'
    writers.NeuroMLWriter.write(nml_network_doc, nml_file)

    print("Written network file to: "+nml_file)

    ###### Validate the NeuroML ######    

    validateNeuroML2(nml_file)



