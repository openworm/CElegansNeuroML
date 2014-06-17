# -*- coding: utf-8 -*-

############################################################

#    A simple script to regenerate the CElegans connectome in NeuroML2
#    Currently uses SpreadsheetDataReader to load connection info
#    from the CElegansNeuronTables.xls spreadsheet

############################################################

from PyOpenWorm import Network as PNetwork
from PyOpenWorm import Neuron as PNeuron
from PyOpenWorm import NeuroML as PNml
from PyOpenWorm import Data
from itertools import imap

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
    pyopenworm_conf = Data.open("morph.conf")

    pyopenworm_net = PNetwork(conf=pyopenworm_conf)
    cell_names, conns = (pyopenworm_net.neurons(), pyopenworm_net.synapses())


    net_id = "CElegansConnectome"

    nml_network_doc = NeuroMLDocument(id=net_id)

    # Create a NeuroML Network data structure to hold on to all the connection info.
    net = Network(id=net_id)
    nml_network_doc.networks.append(net)

    def morphology(cell_name):
    	# build a Population data structure out of the cell name
        pop0 = Population(id=cell_name, component=cell_name, size=1)
        inst = Instance(id="0")
        # Each of these cells is at (0,0,0), i.e. segment 3D info in each cell is absolute
        inst.location = Location(x="0.0", y="0.0", z="0.0")
        pop0.instances.append(inst)

        # put that Population into the Network data structure from above
        net.populations.append(pop0)

        neur = pyopenworm_net.aneuron(cell_name)
        doc = PNml.generate(neur)

        return cell_name, doc.cells[0]
        #print("Loaded morphology file from: %s, with id: %s"%(cell_file, all_cells[cell].id))

    # To hold all Cell NeuroML objects vs. names
    all_cells = { x[0] : x[1] for x in imap(morphology, cell_names) }

    dists = []
    start_time = time.time()
    def get_random_synapse_location(c):
        idx = randint(0,  len(c.morphology.segments)-1)
        seg_id = getSegmentIds(c)[idx]
        fraction = random()
        return (idx,seg_id,fraction)
    def getDist(p1,p2):
        return math.sqrt(math.pow(p1[0]-p2[0],2)+math.pow(p1[1]-p2[1],2)+math.pow(p1[2] - p2[2],2))
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

        debug = True
        if debug: print "Projection between %s and %s has %i conns"%(conn.pre_cell,conn.post_cell,conn.number)

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
                    (pre_segment_index,pre_segment_id,pre_fraction_along) = get_random_synapse_location(pre_cell)
                    (post_segment_index,post_segment_id,post_fraction_along) = get_random_synapse_location(post_cell)

                    pre_pos = get3DPosition(pre_cell, pre_segment_index, pre_fraction_along)
                    post_pos = get3DPosition(post_cell, post_segment_index, post_fraction_along)

                    dist = getDist(pre_pos,post_pos)
                    print dist

                    if dist < best_dist:
                        best_dist = dist
                        if debug: print "Shortest length of connection: %f um"%best_dist
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

    print ("Connections generated in %f seconds, mean length: %f um"%((time.time() - start_time), sum(dists)/len(dists)))
    nml_file = net_id+'.nml'
    writers.NeuroMLWriter.write(nml_network_doc, nml_file)

    print("Written network file to: "+nml_file)

    ###### Validate the NeuroML ######

    validateNeuroML2(nml_file)



