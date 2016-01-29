# -*- coding: utf-8 -*-

############################################################

#    A simple script to regenerate the CElegans connectome in NeuroML2
#    Currently uses SpreadsheetDataReader to load connection info 
#    from the CElegansNeuronTables.xls spreadsheet

############################################################

from __future__ import print_function

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

from neuroml.utils import validate_neuroml2

from random import random
from random import randint

from NeuroMLUtilities import getSegmentIds
from NeuroMLUtilities import get3DPosition


import math
import time

# Get the standard name for a network connection as used in the neuroConstruct project
def get_projection_id(pre, post, syntype):

    proj_id = "NCXLS_%s_%s"%(pre, post)
    
    if "GapJunction" in syntype:
       proj_id += '_GJ'

    return proj_id


if __name__ == "__main__":

    # Use the spreadsheet reader to give a list of all cells and a list of all connections
    # This could be replaced with a call to "DatabaseReader" or "OpenWormNeuroLexReader" in future...
    cell_names, conns = SpreadsheetDataReader.readDataFromSpreadsheet()

    net_id = "CElegansConnectome"

    nml_network_doc = NeuroMLDocument(id=net_id)

    # Create a NeuroML Network data structure to hold on to all the connection info.
    net = Network(id=net_id)
    nml_network_doc.networks.append(net)

    # To hold all Cell NeuroML objects vs. names
    all_cells = {}
    
    for cell in cell_names:
    	# build a Population data structure out of the cell name
        pop0 = Population(id=cell, component=cell, size=1)
        inst = Instance(id="0")
        # Each of these cells is at (0,0,0), i.e. segment 3D info in each cell is absolute
        inst.location = Location(x="0.0", y="0.0", z="0.0")
        pop0.instances.append(inst)
        
        # put that Population into the Network data structure from above
        net.populations.append(pop0)
        
        # also use the cell name to grab the morphology file, as a NeuroML data structure
        #  into the 'all_cells' dict
        cell_file = '../generatedNeuroML2/%s.cell.nml'%cell
        doc = loaders.NeuroMLLoader.load(cell_file)
        all_cells[cell] = doc.cells[0]
        print("Loaded morphology file from: %s, with id: %s"%(cell_file, all_cells[cell].id))

    dists = []
    start_time = time.time()
    for conn in conns:
		
        # take information about each connection and package it into a 
        # NeuroML Projection data structure
        proj_id = get_projection_id(conn.pre_cell, conn.post_cell, conn.syntype)
        proj0 = Projection(id=proj_id, \
        		     	   presynaptic_population=conn.pre_cell, 
        		      	   postsynaptic_population=conn.post_cell, 
        		       	   synapse=conn.synclass)

        # Get the corresponding Cell for each 
        pre_cell = all_cells[conn.pre_cell]
        post_cell = all_cells[conn.post_cell]

        # Get lists of the valid segment ids
        pre_segs = getSegmentIds(pre_cell)
        post_segs = getSegmentIds(post_cell)

        debug = False
        #if "VC5" in conn.pre_cell: debug = True
        debug = True
        if debug: print("Projection between %s and %s has %i conns"%(conn.pre_cell,conn.post_cell,conn.number))

        for conn_id in range(0,conn.number):

            use_substitute_connections = False

            if use_substitute_connections:

                print("Substituting a connection...")
                ###########################################

                # This can be where alternate connections (e.g. extracted fromn Steve Cook's data) are added

                ###########################################

            else:

                #print "--- Conn %i"%conn_id
                best_dist = 1e6
                num_to_try = min(5000,int(0.5*len(pre_segs)*len(post_segs)))
                if debug: print("Trying %i possible random connections"%num_to_try)
            
                # Try a number of times to get the shortest connection between pre & post cells
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
                        if debug: print("Shortest length: %f um... "%best_dist, end="")
                        best_pre_seg = pre_segment_id
                        best_pre_fract = pre_fraction_along
                        best_post_seg = post_segment_id
                        best_post_fract = post_fraction_along

                dists.append(best_dist)
        
                # Add a Connection with the closest locations
                conn0 = Connection(id=conn_id, \
                    pre_cell_id="../%s/0/%s"%(conn.pre_cell, conn.pre_cell), 
                    pre_segment_id = best_pre_seg,
                    pre_fraction_along = best_pre_fract,
                    post_cell_id="../%s/0/%s"%(conn.post_cell, conn.post_cell), 
                    post_segment_id = best_post_seg,
                    post_fraction_along = best_post_fract)
        
                proj0.connections.append(conn0)

        net.projections.append(proj0)

    print("Connections generated in %f seconds, mean length: %f um"%((time.time() - start_time), sum(dists)/len(dists)))
    nml_file = net_id+'.nml'
    writers.NeuroMLWriter.write(nml_network_doc, nml_file)

    print("Written network file to: "+nml_file)

    ###### Validate the NeuroML ######    

    validate_neuroml2(nml_file)
    
    plotLengths = False
    
    if plotLengths:

        from pylab import *

        plot(dists, '.')

        xlabel('Connection number')
        ylabel('Length of connection (um)')
        title('Connection lengths')
        savefig("test.png")
        show()



