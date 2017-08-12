# from LEMS_c302_C1_Syns_nrn import NeuronSimulation
from LEMS_c302_C1_Full_nrn import NeuronSimulation

import neuron

h = neuron.h

class C302NRNSimualtion():
    
    max_ca = 1.7e-11
    max_ca_found = -1
    
    def __init__(self, tstop=1e-6, dt=0.1,activity_file=None):
        
        # super(C302NRNSimualtion, self).__init__(tstop, dt)
        self.ns = NeuronSimulation(tstop, dt)
        
    def step(self):
        
        print(("> Current NEURON time: %s"%h.t))
        
        h.fadvance()
        
        print(("< Current NEURON time: %s"%h.t))
                  
        values = [self._scale(h.a_MDR01[0].soma.cai,print_it=True), \
                 self._scale(h.a_MVR01[0].soma.cai), \
                 self._scale(h.a_MVL01[0].soma.cai), \
                 self._scale(h.a_MDL01[0].soma.cai), \
                 self._scale(h.a_MDR02[0].soma.cai), \
                 self._scale(h.a_MVR02[0].soma.cai), \
                 self._scale(h.a_MVL02[0].soma.cai), \
                 self._scale(h.a_MDL02[0].soma.cai), \
                 self._scale(h.a_MDR03[0].soma.cai), \
                 self._scale(h.a_MVR03[0].soma.cai), \
                 self._scale(h.a_MVL03[0].soma.cai), \
                 self._scale(h.a_MDL03[0].soma.cai), \
                 self._scale(h.a_MDR04[0].soma.cai), \
                 self._scale(h.a_MVR04[0].soma.cai), \
                 self._scale(h.a_MVL04[0].soma.cai), \
                 self._scale(h.a_MDL04[0].soma.cai), \
                 self._scale(h.a_MDR05[0].soma.cai), \
                 self._scale(h.a_MVR05[0].soma.cai), \
                 self._scale(h.a_MVL05[0].soma.cai), \
                 self._scale(h.a_MDL05[0].soma.cai), \
                 self._scale(h.a_MDR06[0].soma.cai), \
                 self._scale(h.a_MVR06[0].soma.cai), \
                 self._scale(h.a_MVL06[0].soma.cai), \
                 self._scale(h.a_MDL06[0].soma.cai), \
                 self._scale(h.a_MDR07[0].soma.cai), \
                 self._scale(h.a_MVR07[0].soma.cai), \
                 self._scale(h.a_MVL07[0].soma.cai), \
                 self._scale(h.a_MDL07[0].soma.cai), \
                 self._scale(h.a_MDR08[0].soma.cai), \
                 self._scale(h.a_MVR08[0].soma.cai), \
                 self._scale(h.a_MVL08[0].soma.cai), \
                 self._scale(h.a_MDL08[0].soma.cai), \
                 self._scale(h.a_MDR09[0].soma.cai), \
                 self._scale(h.a_MVR09[0].soma.cai), \
                 self._scale(h.a_MVL09[0].soma.cai), \
                 self._scale(h.a_MDL09[0].soma.cai), \
                 self._scale(h.a_MDR10[0].soma.cai), \
                 self._scale(h.a_MVR10[0].soma.cai), \
                 self._scale(h.a_MVL10[0].soma.cai), \
                 self._scale(h.a_MDL10[0].soma.cai), \
                 self._scale(h.a_MDR11[0].soma.cai), \
                 self._scale(h.a_MVR11[0].soma.cai), \
                 self._scale(h.a_MVL11[0].soma.cai), \
                 self._scale(h.a_MDL11[0].soma.cai), \
                 self._scale(h.a_MDR12[0].soma.cai), \
                 self._scale(h.a_MVR12[0].soma.cai), \
                 self._scale(h.a_MVL12[0].soma.cai), \
                 self._scale(h.a_MDL12[0].soma.cai), \
                 self._scale(h.a_MDR13[0].soma.cai), \
                 self._scale(h.a_MVR13[0].soma.cai), \
                 self._scale(h.a_MVL13[0].soma.cai), \
                 self._scale(h.a_MDL13[0].soma.cai), \
                 self._scale(h.a_MDR14[0].soma.cai), \
                 self._scale(h.a_MVR14[0].soma.cai), \
                 self._scale(h.a_MVL14[0].soma.cai), \
                 self._scale(h.a_MDL14[0].soma.cai), \
                 self._scale(h.a_MDR15[0].soma.cai), \
                 self._scale(h.a_MVR15[0].soma.cai), \
                 self._scale(h.a_MVL15[0].soma.cai), \
                 self._scale(h.a_MDL15[0].soma.cai), \
                 self._scale(h.a_MDR16[0].soma.cai), \
                 self._scale(h.a_MVR16[0].soma.cai), \
                 self._scale(h.a_MVL16[0].soma.cai), \
                 self._scale(h.a_MDL16[0].soma.cai), \
                 self._scale(h.a_MDR17[0].soma.cai), \
                 self._scale(h.a_MVR17[0].soma.cai), \
                 self._scale(h.a_MVL17[0].soma.cai), \
                 self._scale(h.a_MDL17[0].soma.cai), \
                 self._scale(h.a_MDR18[0].soma.cai), \
                 self._scale(h.a_MVR18[0].soma.cai), \
                 self._scale(h.a_MVL18[0].soma.cai), \
                 self._scale(h.a_MDL18[0].soma.cai), \
                 self._scale(h.a_MDR19[0].soma.cai), \
                 self._scale(h.a_MVR19[0].soma.cai), \
                 self._scale(h.a_MVL19[0].soma.cai), \
                 self._scale(h.a_MDL19[0].soma.cai), \
                 self._scale(h.a_MDR20[0].soma.cai), \
                 self._scale(h.a_MVR20[0].soma.cai), \
                 self._scale(h.a_MVL20[0].soma.cai), \
                 self._scale(h.a_MDL20[0].soma.cai), \
                 self._scale(h.a_MDR21[0].soma.cai), \
                 self._scale(h.a_MVR21[0].soma.cai), \
                 self._scale(h.a_MVL21[0].soma.cai), \
                 self._scale(h.a_MDL21[0].soma.cai), \
                 self._scale(h.a_MDR22[0].soma.cai), \
                 self._scale(h.a_MVR22[0].soma.cai), \
                 self._scale(h.a_MVL22[0].soma.cai), \
                 self._scale(h.a_MDL22[0].soma.cai), \
                 self._scale(h.a_MDR23[0].soma.cai), \
                 self._scale(h.a_MVR23[0].soma.cai), \
                 self._scale(h.a_MVL23[0].soma.cai), \
                 self._scale(h.a_MDL23[0].soma.cai), \
                 self._scale(h.a_MDR24[0].soma.cai), \
                 self._scale(0), \
                 self._scale(h.a_MVL24[0].soma.cai), \
                 self._scale(h.a_MDL24[0].soma.cai)]
                 
        print(("Returning %s"%values))
        return values
        
    
    def _scale(self,ca,print_it=False):
        
        self.max_ca_found = max(ca,self.max_ca_found)
        scaled = min(1,(ca/self.max_ca))
        if print_it: 
            print(("- Scaling %s to %s (max found: %s)"%(ca,scaled,self.max_ca_found)))
        return scaled
    

if __name__ == '__main__':
    
    dt = 0.1
    maxt = 360
    
    ns = C302NRNSimualtion(tstop=maxt, dt=dt)

    steps = int(maxt/dt)
    
    for step in range(steps):
        print(("======= Step %i ==============="%step))
        ns.step()