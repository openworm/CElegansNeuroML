c302: simple NeuroML based network models of C elegans
------------------------------------------------------

*NOTE: Still a work in progress!!* 

This is an experimental set of files for generating network models in NeuroML 
based on C elegans connectivity data.

It uses information on the synaptic connectivity of the network and uses 
[libNeuroML](https://github.com/NeuralEnsemble/libNeuroML) to generate 
a network in valid NeuroML, which can be run in [jNeuroML](https://github.com/NeuroML/jNeuroML).

### Multiple versions of the network

There will be multiple version of this network, based on increasingly complex cell models, e.g.

**[Parameters_A](https://github.com/openworm/CElegansNeuroML/blob/master/CElegans/pythonScripts/c302/parameters_A.py)** Integrate & fire cells (not very physiological; only parameter set so far)

**Parameters_B** Izhikevich cells or perhaps AdEx cells (slightly more physiological)

**Parameters_C** Single compartment, conductance based neurons (could be based on known ion channel types, etc.)


### To install & test

Install [libNeuroML](https://github.com/NeuralEnsemble/libNeuroML) & [jNeuroML](https://github.com/NeuroML/jNeuroML)

    python c302_A.py          # To regenerate the NeuroML & LEMS files
    jnml LEMS_c302_A.xml      # Run a simulation with jNeuroML
    
This will produce the following (6 cells visualised with the jNeuroML GUI):

![Simulation in jNeuroML](https://raw.githubusercontent.com/openworm/CElegansNeuroML/master/CElegans/pythonScripts/c302/images/LEMS.png)

This saves traces from all neurons in a file c302_A.dat. To plot the activity of all 302 neurons:

    python analyse.py c302_A.dat
    
![Analysis](https://raw.githubusercontent.com/openworm/CElegansNeuroML/master/CElegans/pythonScripts/c302/images/analyse.png)
    
    
To test all of the working features:

    ./test.sh
    
### Command line interface

This package can be used to generate customised networks of varying size, with different cells stimulated, of varying duration from the command line:

    c302.py MyNetwork parameters_A -cells ["ADAL","AIBL","RIVR","RMEV"] -cellstostimulate ["ADAL","RIVR"] -duration 500
    
This will create a NeuroML 2 file and a LEMS file to execute it, containing 4 cells, stimulating 2 of them, and with a duration of 500 ms

More options can be found with 

    c302.py -h
    
### Mapping to NEURON

Due to the fact that the cells are in pure NeuroML2, they can be mapped to other formats using the export feature of jNeuroML. [Install NEURON](http://www.neuron.yale.edu/neuron/download) and map the network to this format using:

    jnml LEMS_c302_A_Pharyngeal.xml -neuron
    nrnivmodl
    nrngui -python LEMS_c302_A_Pharyngeal_nrn.py
    
This will run the example network containing [just the 20 cells from the pharynx](https://github.com/openworm/CElegansNeuroML/blob/master/CElegans/pythonScripts/c302/c302_A_Pharyngeal.py). 

![Run in NEURON](https://raw.githubusercontent.com/openworm/CElegansNeuroML/master/CElegans/pythonScripts/c302/images/Neuron.png)

Image above shows the network run in NEURON (top) and a comparison of the activity of the 20 cells when run on jNeuroML 
(bottom left) and NEURON (bottom right). Bottom graphs generated with [analyse.py](https://github.com/openworm/CElegansNeuroML/blob/master/CElegans/pythonScripts/c302/analyse.py) and each of the traces are offset by a few mV for clarity.

### Planned work

Future plans include:

- Implement & correctly tune **Parameters_B**, **Parameters_C**

- Modify to use [PyOpenWorm](https://github.com/openworm/PyOpenWorm) as source of connection data

- Move all of this to its own repository

- Add to Geppetto for simulation of networks in browser

- Connect output of motorneurons in networks to [Sibernetic](http://openworm.github.io/Smoothed-Particle-Hydrodynamics/)

- Link to [bionet](https://github.com/portegys/bionet) to tune weights of network to physiological behaviour


