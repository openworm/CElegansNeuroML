from NeuroMLUtilities import ConnectionInfo
import PyOpenWorm as P

############################################################

#   A simple script to read the values in PyOpenWorm
#   Originally written by Mark Watts (github.com/mwatts15)

############################################################


class OpenWormReader:
    def __init__(self):
        P.connect()
        self.net = P.Worm().get_neuron_network()
        self.all_connections = self.net.synapses()

    def read(self):
        conns = []
        cells = []
        for s in self.all_connections:
            pre = str(s.pre_cell())
            post = str(s.post_cell())
            syntype = str(s.syntype())
            num = int(s.number())
            synclass = str(s.synclass())

            conns.append(ConnectionInfo(pre, post, num, syntype, synclass))

            if pre not in cells:
                cells.append(pre)
            if post not in cells:
                cells.append(post)

        print("Total cells read " + str(len(cells)))
        print("Total connections read " + str(len(conns)))
        P.disconnect()
        return cells, conns
