#!/usr/bin/env python
import rdflib as R
import numbers
from numbers import Number
import neuroml.loaders as loaders
import lxml
from lxml import etree as ET

# open the morphology (NML2) file

ns = R.Namespace("http://www.neuroml.org/schema/neuroml2/")
ns1 = R.Namespace("http://www.markw.com/coolURL#")
def k():
    doc = loaders.NeuroMLLoader.load("../generatedNeuroML2/ADAL.nml")
    c = doc.cells[0]
    for p in z(c.morphology):
        yield p
def k_xml():
    c = lxml.parse("../generatedNeuroML2/ADAL.nml")
    for p in z(c):
        yield p

def z(m):
    mNode = R.BNode()
    for k in m:
        d = getattr(m, k)
        if isinstance(d,list):
            n = R.BNode()
            yield (mNode, ns[k], n)
            for p in d:
                if isinstance(p, basestring):
                    yield (n, ns1["hasMember"], p)
                else:
                    for i in z(p):
                        yield(i)
        else:
            if is_valid_datatype(d):
                yield (mNode, ns[k], R.Literal(d))
            elif d != None:
                n = R.BNode()
                yield (n, R.RDFS['label'], R.Literal(k))
                for i in z(d):
                    yield(i)
                print (k,d)


def is_valid_datatype(v):
    types = [basestring, Number]
    for t in types:
        if isinstance(v, t):
            return True
    return False


if __name__ == "__main__":
    graph = R.Graph()
    for t in k():
        graph.add(t)
    graph.serialize("result.n3", "n3")

