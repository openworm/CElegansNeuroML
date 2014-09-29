from c302 import generate

from neuroml import PulseGenerator
from neuroml import ExplicitInput
import neuroml.writers as writers

# See https://github.com/openworm/OpenWorm/issues/212

import parameters_A as params

def add_new_input(nml_doc, cell, delay, duration, amplitude):
    
    stim = PulseGenerator(id="stim_"+cell, delay=delay, duration=duration, amplitude=amplitude)
    
    nml_doc.pulse_generators.append(stim)
    
    exp_input = ExplicitInput(target="%s/0/%s"%(cell, params.generic_cell.id),
                                                     input=stim.id)

    nml_doc.networks[0].explicit_inputs.append(exp_input)

if __name__ == '__main__':
    
    cells = ["RMGR","ASHR","ASKR","AWBR","IL2R","RMHR","URXR"]
    cells_to_stimulate      = []
    
    reference = "c302_A_Social"
    
    nml_doc = generate(reference, params, cells=cells, cells_to_stimulate=cells_to_stimulate, \
             duration=2500, dt=0.1, vmin=-72, vmax=-48)
             
    stim_amplitude = "0.35nA"
    add_new_input(nml_doc, "RMGR", "100ms", "200ms", stim_amplitude)
    add_new_input(nml_doc, "ASHR", "400ms", "200ms", stim_amplitude)
    add_new_input(nml_doc, "ASKR", "700ms", "200ms", stim_amplitude)
    add_new_input(nml_doc, "AWBR", "1000ms", "200ms", stim_amplitude)
    add_new_input(nml_doc, "IL2R", "1300ms", "200ms", stim_amplitude)
    add_new_input(nml_doc, "RMHR", "1600ms", "200ms", stim_amplitude)
    add_new_input(nml_doc, "URXR", "1900ms", "200ms", stim_amplitude)
    
    
    nml_file = reference+'.nml'
    writers.NeuroMLWriter.write(nml_doc, nml_file) # Write over network file written above...
    
    print("(Re)written network file to: "+nml_file)