This is a neuroConstruct project (http://neuroconstruct.org) containing the latest version of the c. elegans connectome.

* cellMechanisms/ - Contains a series of directories that contain ChannelML files, which provide an XML data structures for representing channel models based on Hodgkin-Huxley style kinetics and as kinetic schemes
* dataSets/ - Intended for storing data sets related to the project
* generatedMorphML/ - MorphML files, one per neuron in the C. elegans, named for the neuron name.  [MorphML](http://homes.mpimf-heidelberg.mpg.de/~mhelmsta/pdf/2007%20Crook%20Gleeson%20Howell%20Svitak%20Silver%20Neuroinformatics.pdf) captures the structural shape of the neuron only, and is a simpler description of the neurons that leaves out dynamics.
* generatedNeuroML/ - NeuroML files, one per neuron in the C. elegans.  In addition to neuron structural shape, NeuroML adds the ability to describe biophysical parameters and connectivity to each neuron.  The relationship of what is in MorphML vs. NeuroML is captured in [the NeuroML introduction documentation](http://www.neuroml.org/introduction.php)
* generatedNeuroML2/ - NeuroML2 files, one per neuron in the C. elegans.  NeuroML2 improves upon NeuroML in many ways.  [Read more about this online](http://www.neuroml.org/neuroml2.php).
* images/ - PNG files generated from screenshots of neuroConstruct with the loaded connectome, for reference of what it should look like when it is loaded
* morphologies/ - internal neuroConstruct representation of all the morphologies of the C. elegans neurons.  Only useful to neuroConstruct.
* pythonScripts/ - Some scripts to interact with, test, and update the C. elegans project
* CElegans.ncx - a neuroConstruct project file -- load this into neuroConstruct to see the connectome.
* README.txt - this file

Open Worm Project, 2013
http://openworm.org
