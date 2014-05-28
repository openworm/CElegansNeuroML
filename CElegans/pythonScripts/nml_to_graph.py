#!/usr/bin/env python
from glob import glob
import rdflib as R
import httplib as H
import numbers
from numbers import Number
import neuroml.loaders as loaders
import lxml
from lxml import etree as ET

# open the morphology (NML2) file

ns = R.Namespace("http://www.neuroml.org/schema/neuroml2/")
ns1 = R.Namespace("http://www.markw.com/coolURL#")
namespaces = {"ns" :"http://www.neuroml.org/schema/neuroml2/"}
def triples_from_morphology(f):
    c = ET.parse(f).getroot()
    c = c.xpath("*")[1]
    for i in z(c,R.BNode()):
        yield i

def z(m, node):
    for k in m:
        if isinstance(k,type(m)):
            c = R.BNode()
            n = ET.QName(k.tag).localname
            yield (node, ns[n], c)
            for i in z(k,c):
                yield i
    t = m.text
    if t != None and len(t.strip()) > 0:
        yield (node, ns["text"], R.Literal(m.text))
    for (k,v) in m.items():
        yield (node, ns[k], R.Literal(v))


def is_valid_datatype(v):
    types = [basestring, Number]
    for t in types:
        if isinstance(v, t):
            return True
    return False

def put_in_sesame(graph):
    s = graph.serialize(format="n3")
    con = H.HTTPConnection("107.170.133.175:8080")
    con.request("PUT", "/openrdf-sesame/repositories/test/statements", s, {"Content-Type": "application/x-turtle;charset=UTF-8"})
    r = con.getresponse()
    print "sesame response is %d " % r.status

if __name__ == "__main__":
    graph = R.Graph()
    for x in iglob("../generatedNeuroML2/*.nml"):
        try:
            for p in triples_from_morphology(x):
                graph.add(p)
        except Exception, e:
            print 'failed on file %s' % x
            print 'error : ' + str(e)
            pass
    put_in_sesame(graph)
