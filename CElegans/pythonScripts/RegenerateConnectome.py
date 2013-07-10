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

class ConnectionInfo:

    def __init__(self,
                 pre_cell,
                 post_cell,
                 number,
                 syntype,
                 synclass):

        self.pre_cell = pre_cell
        self.post_cell = post_cell
        self.number = number
        self.syntype = syntype
        self.synclass = synclass


    def __str__(self):
        return "Connection from %s to %s (%i times, type: %s, neurotransmitter: %s)"%(self.pre_cell, self.post_cell, self.number, self.syntype, self.synclass)



if __name__ == "__main__":

    cells, conns = SpreadsheetDataReader.readDataFromSpreadsheet()

    net_id = "CElegansConnectome"
    proj_template = "NCXLS_%s_%s"

    nml_network_doc = NeuroMLDocument(id=net_id)
    nml_network_doc = NeuroMLDocument(id=net_id)


    net = Network(id=net_id)
    nml_network_doc.networks.append(net)

    
    for cell in cells:
        pop0 = Population(id=cell, component=cell, size=1)
        inst = Instance(id="0")
        inst.location = Location(x="0.0", y="0.0", z="0.0")
        pop0.instances.append(inst)
        net.populations.append(pop0)

    for conn in conns:
        
        proj0 = Projection(id=proj_template%(conn.pre_cell, conn.post_cell), presynaptic_population=conn.pre_cell, postsynaptic_population=conn.post_cell, synapse=conn.synclass)
        
        conn0 = Connection(id="0", pre_cell_id="../%s/0/%s"%(conn.pre_cell, conn.pre_cell), post_cell_id="../%s/0/%s"%(conn.post_cell, conn.post_cell))
        
        proj0.connections.append(conn0)
        net.projections.append(proj0)
    

    fn = net_id+'.nml'
    writers.NeuroMLWriter.write(nml_network_doc, fn)

    print("Written network file to: "+fn)




