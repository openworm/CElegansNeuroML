# -*- coding: utf-8 -*-

############################################################

#    Utilities for reading/writing/parsing NeuroML 2 files

############################################################


from neuroml import NeuroMLDocument
from neuroml import Network
from neuroml import Population
from neuroml import Instance
from neuroml import Location
from neuroml import Projection
from neuroml import Connection

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



def validateNeuroML2(file_name):

    from lxml import etree
    from urllib import urlopen
    #schema_file = urlopen("https://raw.github.com/NeuroML/NeuroML2/master/Schemas/NeuroML2/NeuroML_v2beta.xsd")
    schema_file = urlopen("https://raw.github.com/NeuroML/NeuroML2/development/Schemas/NeuroML2/NeuroML_v2beta1.xsd")
    xmlschema = etree.XMLSchema(etree.parse(schema_file))
    print "Validating %s against %s" %(file_name, schema_file.geturl())
    xmlschema.assertValid(etree.parse(file_name))
    print "It's valid!"
