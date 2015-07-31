"""

Example to build a full spiking IaF network
throught libNeuroML, save it as XML and validate it

"""


#########################################################

import neuroml

import random
random.seed(12345)

nml_doc = neuroml.NeuroMLDocument(id="simplenet")

# Define integrate & fire cell 
iaf0 = neuroml.IafCell(id="iaf0", C="1.0 nF",
                           thresh = "-50mV",
                           reset="-65mV",
                           leak_conductance="10 nS",
                           leak_reversal="-65mV")
nml_doc.iaf_cells.append(iaf0)

# Define synapse
syn0 = neuroml.ExpTwoSynapse(id="syn0", gbase="10nS",
                             erev="0mV",
                             tau_rise="0.5ms",
                             tau_decay="10ms")
nml_doc.exp_two_synapses.append(syn0)

# Create network
net = neuroml.Network(id="simplenet")
nml_doc.networks.append(net)

# Create 2 populations
size0 = 5
size1 = 5
pop0 = neuroml.Population(id="Pop0", size = size0,
                          component=iaf0.id)
pop1 = neuroml.Population(id="Pop1", size = size1,
                          component=iaf0.id)
net.populations.append(pop0)
net.populations.append(pop1)

# Create a projection between them
proj1 = neuroml.Projection(id="Proj0", synapse=syn0.id,
                        presynaptic_population=pop0.id, 
                        postsynaptic_population=pop1.id)
net.projections.append(proj1)

conn_count = 0
for pre in range(0,size0):

    # Create a number of random amplitude current pulses 
    pg = neuroml.PulseGenerator(id="input%i"%pre,
                                delay="0ms",
                                duration="500ms",
                                amplitude="%fnA"%(0.5+random.random()))
    nml_doc.pulse_generators.append(pg)

    # Add these to cells
    input_list = neuroml.InputList(id="il%i"%pre,
                             component=pg.id,
                             populations=pop0.id)
    input = neuroml.Input(id=pre, 
                          target="../%s[%i]"%(pop0.id, pre), 
                          destination="synapses")  
    input_list.input.append(input)
    net.input_lists.append(input_list)
    
    # Connect cells with defined probability
    prob_connection = 0.5
    for post in range(0,size1):
      if random.random() <= prob_connection:
        conn = \
          neuroml.Connection(id=conn_count, \
                   pre_cell_id="../%s[%i]"%(pop0.id,pre),
                   post_cell_id="../%s[%i]"%(pop1.id,post))
        proj1.connections.append(conn)
        conn_count+=1
        
            
#########################################################


import neuroml.writers as writers

nml_file = 'simplenet.nml'
writers.NeuroMLWriter.write(nml_doc, nml_file)


print("Written network file to: "+nml_file)


###### Validate the NeuroML ######    

from neuroml.utils import validate_neuroml2

validate_neuroml2(nml_file)
