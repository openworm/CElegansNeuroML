c302: simple NeuroML based network models of C elegans
------------------------------------------------------

*NOTE: Work in progress!!* 

This is an experimental set of files for generating network models in NeuroML 
based on C elegans connectivity data.

It uses information on the synaptic connectivity of the network and uses 
[libNeuroML](https://github.com/NeuralEnsemble/libNeuroML) to generate 
a network in valid NeuroML, which can be run in [jNeuroML](https://github.com/NeuroML/jNeuroML).

**Multiple versions**

There will be multiple version of this network, based on increasingly complex cell models, e.g.

**[Parameters_A](https://github.com/openworm/CElegansNeuroML/blob/master/CElegans/pythonScripts/c302/parameters_A.py))** Integrate & fire cells (not very physiological)

**Parameters_B)** Izhikevich cells or perhaps AdEx cells (slightly more physiological)

**Parameters_C)** Single compartment, conductance based neurons (could be based on known ion channel types, etc.)


**To install & test**

Install [libNeuroML](https://github.com/NeuralEnsemble/libNeuroML) & [jNeuroML](https://github.com/NeuroML/jNeuroML)

    python c302_A.py          # To regenerate the NeuroML & LEMS files
    jnml LEMS_c302_A.xml      # Run a simulation with jNeuroML
    
This will produce the following (6 cells visualised with the jNeuromL GUI)

To plot all of the activity

    python analyse.py c302_A.dat
    
Or, test all of the working features:

    ./test.sh

**Planned work**

Future plans include:

- Implement & tune Parameters_B, Parameters_c

- Modify to use [PyOpenWorm](https://github.com/openworm/PyOpenWorm)

- Move all of this to its own repository

- Add to Geppetto for simulation of networks in browser

- Connect output of motorneurons in networks to [Sibernetic](http://openworm.github.io/Smoothed-Particle-Hydrodynamics/)

- Link to [bionet](https://github.com/portegys/bionet) to tune weights of network to physiological behaviour


