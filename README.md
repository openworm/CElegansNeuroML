This repository contains a neuroConstruct (http://www.neuroConstruct.org) project containing a model of the c. elegans nervous system.

The NeuroML files are available under the directories CElegans/generatedMorphML, CElegans/generatedNeuroML, and CElegans/generatedNeuroML2

This is being developed as part of the OpenWorm project (http://www.openworm.org).

The C. elegans 3D model this was derived from was produced by Dr. Christian Grove and Dr. Paul Sternberg at the VirtualWorm project (WormBase, CalTech) and released into the public domain. You can visit the VirtualWorm home page at http://caltech.wormbase.org/virtualworm/

We have converted all 302 neurons described in the [WormBase Virtual Worm Blender files](https://github.com/openworm/OpenWorm/wiki/Virtual-Worm-Blender-Files).  We have represented them as [multi-compartmental neuronal models](http://en.wikipedia.org/wiki/Biological_neuron_models#Expanded_neuron_models).  This captures the positions of the cells in context with each other and gives us a place to start building descriptions of the [synaptic junctions](http://en.wikipedia.org/wiki/Synapse) and the [ion channels for each cell](http://en.wikipedia.org/wiki/Ion_channel).  In addition, we have added [details of connectivity between neurons](https://docs.google.com/spreadsheet/ccc?key=0Avt3mQaA-HaMdHZuZnFuZmI5Q1VRU0VMekZ5d1QyZVE&hl=en_US#gid=0) into the neuroConstruct project.

Limitations:

* An accurate representation of the ion channels and their distributions in each neuron has not yet been attempted -- currently they are just "stub" collections of ion channels.
* An accurate representation of the synapses between the neurons has not yet been attempted.  They are simplistic synapses only for the moment.

For full details on running this neuroConstruct project see: 
https://github.com/openworm/OpenWorm/wiki/Running-the-C.-elegans-model-in-neuroConstruct.



