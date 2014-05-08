# -*- coding: utf-8 -*-
from NeuroMLUtilities import ConnectionInfo
from PyOpenWorm import Configure,Data,Network

############################################################

#    A simple script to read the values in CElegansNeuronTables.xls.

############################################################


class OpenWormReader:
    def __init__(self):
        c = Data()
        c['connectomecsv'] = 'https://raw.github.com/openworm/data-viz/master/HivePlots/connectome.csv'
        c['neuronscsv'] = 'https://raw.github.com/openworm/data-viz/master/HivePlots/neurons.csv'
        c['sqldb'] = '/home/markw/work/openworm/PyOpenWorm/db/celegans.db'
        self.config = c
        self.net = Network(c)
    def read(self):
        conns = []
        cells = []
        for s in self.net.synapses():
            pre = str(s[0])
            post = str(s[1])
            syntype = str(s[2][0])
            num = int(s[2][2])
            synclass = str(s[2][2])

            conns.append(ConnectionInfo(pre, post, num, syntype, synclass))
            if pre not in cells:
                cells.append(pre)
            if post not in cells:
                cells.append(post)

        return cells, conns


