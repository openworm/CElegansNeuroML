*C. elegans* models in NeuroML and neuroConstruct
==============================================

This repository contains a neuroConstruct (http://www.neuroConstruct.org) project containing a model of the *C. elegans* nervous system, see [here](https://github.com/openworm/CElegansNeuroML/tree/master/CElegans).

The NeuroML files are available under the directories [generatedNeuroML](https://github.com/openworm/CElegansNeuroML/tree/master/CElegans/generatedNeuroML), and [generatedNeuroML2](https://github.com/openworm/CElegansNeuroML/tree/master/CElegans/generatedNeuroML).

This is being developed as part of the [OpenWorm project](http://www.openworm.org).

**There is also a new initiative which uses Python scripts to generate network models in NeuroML2 at multiple levels of detail: c302. This has recently been moved to [its own repository](https://github.com/openworm/c302).** 

### Installation

  python setup.py install

### Data on which this model is based

The *C. elegans* 3D model this was derived from was produced by Dr. Christian Grove and Dr. Paul Sternberg at the VirtualWorm project (WormBase, CalTech) and released into the public domain. You can visit the VirtualWorm home page at http://caltech.wormbase.org/virtualworm/

We have converted all 302 neurons described in the [WormBase Virtual Worm Blender files](https://github.com/openworm/OpenWorm/wiki/Virtual-Worm-Blender-Files).  We have represented them as [multi-compartmental neuronal models](http://en.wikipedia.org/wiki/Biological_neuron_models#Expanded_neuron_models).  This captures the positions of the cells in context with each other and gives us a place to start building descriptions of the [synaptic junctions](http://en.wikipedia.org/wiki/Synapse) and the [ion channels for each cell](http://en.wikipedia.org/wiki/Ion_channel).  In addition, we have added [details of connectivity between neurons](https://docs.google.com/spreadsheet/ccc?key=0Avt3mQaA-HaMdHZuZnFuZmI5Q1VRU0VMekZ5d1QyZVE&hl=en_US#gid=0) into the neuroConstruct project.

### Important Limitations

Please note:

* An accurate representation of the ion channels and their distributions in each neuron has not yet been attempted. Work on a cell model from *C. elegans* with ion channels can be found [here](https://github.com/openworm/muscle_model/tree/master/NeuroML2)
* An accurate representation of the synapses between the neurons has not yet been attempted.  They are simplistic synapses only for the moment.

More accurate models of conductance based neurons and more realistic synapses will be incorporated into [c302](https://github.com/openworm/CElegansNeuroML/tree/master/CElegans/pythonScripts/c302) first, and then the neuroConstruct model will be updated.

### Running the neuroConstruct model

For full details on running this neuroConstruct project see:
https://github.com/openworm/OpenWorm/wiki/Running-the-C.-elegans-model-in-neuroConstruct.

[![Build Status](https://travis-ci.org/openworm/CElegansNeuroML.svg?branch=master)](https://travis-ci.org/openworm/CElegansNeuroML)
