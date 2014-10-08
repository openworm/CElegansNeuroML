
# Model of a decision making circuit

# See https://github.com/openworm/OpenWorm/issues/212

# To run:
#          python c302_Social.py A   (uses parameters_A, requires jNeuroML to run)
# or
#          python c302_Social.py B   (uses parameters_B, requires jNeuroML built from the 
#                                     experimental branches to run: 'python getNeuroML experimental'
#                                     see https://github.com/NeuroML/jNeuroML)

from c302 import generate

from neuroml import PulseGenerator
from neuroml import ExplicitInput
from neuroml import GapJunction
import neuroml.writers as writers

import sys

def add_new_input(nml_doc, cell, delay, duration, amplitude):
    
    stim = PulseGenerator(id="stim_"+cell, delay=delay, duration=duration, amplitude=amplitude)
    
    nml_doc.pulse_generators.append(stim)
    
    populations_without_location = isinstance(params.elec_syn, GapJunction)
    
    target ="%s/0/%s"%(cell, params.generic_cell.id)
    if populations_without_location:
        target ="%s[0]"%(cell)
    exp_input = ExplicitInput(target=target, input=stim.id)

    nml_doc.networks[0].explicit_inputs.append(exp_input)

if __name__ == '__main__':
    
    parameter_set = sys.argv[1] if len(sys.argv)==2 else 'A'
    
    exec('import parameters_%s as params'%parameter_set)
    
    cells = ["RMGR","ASHR","ASKR","AWBR","IL2R","RMHR","URXR"]
    cells_to_stimulate      = []
    
    reference = "c302_%s_Social"%parameter_set
    
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