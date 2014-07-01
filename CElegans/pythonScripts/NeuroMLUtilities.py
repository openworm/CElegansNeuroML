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

#cachedSegIds = {}

def getSegmentIds(cell):
    seg_ids = []
    for segment in cell.morphology.segments:
        seg_ids.append(segment.id)

    return seg_ids

def get3DPosition(cell, segment_index, fraction_along):
    seg = cell.morphology.segments[segment_index]

    end = seg.distal

    start = seg.proximal
    if start is None:
        segs = getSegmentIds(cell)
        seg_index_parent = segs.index(seg.parent.segments)
        start = cell.morphology.segments[seg_index_parent].distal

    fx = fract(start.x, end.x, fraction_along)
    fy = fract(start.y, end.y, fraction_along)
    fz = fract(start.z, end.z, fraction_along)

    #print "(%f, %f, %f) is %f between (%f, %f, %f) and (%f, %f, %f)"%(fx,fy,fz,fraction_along,start.x,start.y,start.z,end.x,end.y,end.z)

    return fx, fy, fz

def fract(a, b, f):
    return a+(b-a)*f
