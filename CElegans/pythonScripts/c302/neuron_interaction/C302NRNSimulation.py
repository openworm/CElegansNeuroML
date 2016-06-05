from LEMS_c302_C1_Syns_nrn import NeuronSimulation

import neuron

h = neuron.h

class C302NRNSimualtion():
    
    max_ca = 7e-13
    max_ca_found = -1
    
    def __init__(self, tstop, dt):
        
        # super(C302NRNSimualtion, self).__init__(tstop, dt)
        self.ns = NeuronSimulation(tstop, dt)
        
    def step(self):
        
        print("> Current NEURON time: %s"%h.t)
        
        h.fadvance()
        
        print("< Current NEURON time: %s"%h.t)
        
        return (self.scale(h.a_SMDDR[0].soma.cai))
        
    
    def scale(self,ca):
        
        self.max_ca_found = max(ca,self.max_ca_found)
        scaled = min(1,(ca/self.max_ca))
        print("- Scaling %s to %s (max found: %s)"%(ca,scaled,self.max_ca_found))
        return scaled
    

if __name__ == '__main__':
    
    dt = 0.1
    maxt = 36
    
    ns = C302NRNSimualtion(tstop=maxt, dt=dt)

    steps = int(maxt/dt)
    
    for step in range(steps):
        print("======= Step %i ==============="%step)
        ns.step()