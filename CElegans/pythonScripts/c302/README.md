c302: simple NeuroML based network models of C elegans
------------------------------------------------------

*NOTE: Work in progress!!* 

This is an experimental set of files for generating network models in NeuroML 
based on C elegans connectivity data.

It used information on synaptic connectivity of the network and uses [libNeuroML](https://github.com/NeuralEnsemble/libNeuroML) to generate 
a network in valid NeuroML, which can be run in [jNeuroML](https://github.com/NeuroML/jNeuroML).

**Multiple versions**

There will be multiple version of the network, based on increasingly complex cell models, e.g.

Parameters A) Integrate & fire cells

Parameters B) Izhikevich cells (perhaps, or AdEx cells)

Parameters C) Single compartment, conductance based neurons


**To install & test**

Install [libNeuroML](https://github.com/NeuralEnsemble/libNeuroML) & [jNeuroML](https://github.com/NeuroML/jNeuroML)

    python c302_A.py
    ./jnml LEMS_c302_A.xml
    python analyse.py c302_A.dat

**Planned work**


Modify to use [PyOpenWorm](https://github.com/openworm/PyOpenWorm)

Move to its own repository

Connect to [Sibernetic](http://openworm.github.io/Smoothed-Particle-Hydrodynamics/)


