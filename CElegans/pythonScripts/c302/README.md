c302: simple NeuroML based network models of C elegans
------------------------------------------------------

*NOTE: Still a work in progress!!* 

This is an experimental set of files for generating network models in NeuroML 2 based on C elegans connectivity data.

It uses information on the synaptic connectivity of the network (from 
[here](https://github.com/openworm/CElegansNeuroML/blob/master/CElegansNeuronTables.xls)) and uses 
[libNeuroML](https://github.com/NeuralEnsemble/libNeuroML) to generate 
a network in valid NeuroML, which can be run in [jNeuroML](https://github.com/NeuroML/jNeuroML).


![c302 structure](https://raw.githubusercontent.com/openworm/CElegansNeuroML/master/CElegans/pythonScripts/c302/images/c302.png)

### Multiple versions of the network

There will be multiple version of this network, based on increasingly complex cell models, e.g.

**[Parameters_A](https://github.com/openworm/CElegansNeuroML/blob/master/CElegans/pythonScripts/c302/parameters_A.py)** Integrate & fire cells (not very physiological) connected by chemical (event triggered, conductance based) synapses

**[Parameters_B](https://github.com/openworm/CElegansNeuroML/blob/master/CElegans/pythonScripts/c302/parameters_B.py)** Updated I&F cells, with gap junction connections plus an "activity" measure (varies 0->1 depending on depolarisation of cell), which should be a better approximation for the relative activity of cells

**[Parameters_C](https://github.com/openworm/CElegansNeuroML/blob/master/CElegans/pythonScripts/c302/parameters_C.py)** Single compartment, conductance based neurons (will be initially based on [muscle cell model](https://github.com/openworm/muscle_model))

**Parameters_D** Multicompartmental, conductance based cells 

Parameters A, B and C are the only parameter sets tested so far, but the aim is to make all of the associated tools below for running, visualising, analysing, etc. *independent of the parameter set used*, so they can be ready for more detailed networks from c302 in the future. 

### To install & test

The full set of dependencies for c302 can be installed with the following (see also the [Travis-CI script](https://github.com/openworm/CElegansNeuroML/blob/master/.travis.yml)):

    git clone https://github.com/openworm/CElegansNeuroML.git
    svn checkout svn://svn.code.sf.net/p/neuroml/code/jNeuroMLJar
    pip install lxml
    pip install xlrd
    pip install xlwt
    git clone https://github.com/purcell/airspeed.git
    cd airspeed
    python setup.py install
    cd ..
    git clone git://github.com/NeuralEnsemble/libNeuroML.git
    cd libNeuroML
    git checkout development
    python setup.py install
    cd ..
    cd CElegans/pythonScripts/c302
    export JNML_HOME=../../../jNeuroMLJar

To regenerate a set of NeuroML & LEMS files for one instance of the model and execute it:

    python c302_Full.py                           # To regenerate the NeuroML & LEMS files
    ../jNeuroMLJar/jnml LEMS_c302_A_Full.xml      # Run a simulation with jNeuroML
    
This will produce the following (6 cells visualised with the jNeuroML GUI):

![Simulation in jNeuroML](https://raw.githubusercontent.com/openworm/CElegansNeuroML/master/CElegans/pythonScripts/c302/images/LEMS.png)

This saves traces from all neurons in a file c302_A.dat. To plot the membrane potential of all 302 neurons:

    python analyse.py c302_A_Full.dat
    
![Analysis](https://raw.githubusercontent.com/openworm/CElegansNeuroML/master/CElegans/pythonScripts/c302/images/analyse.png)
    
    
Traces are slightly offset from one another for clarity.

To test all of the working features of the framework run [test.sh](https://raw.githubusercontent.com/openworm/CElegansNeuroML/master/CElegans/pythonScripts/c302/test.sh):

    ./test.sh
    
### Command line interface

This package can be used to generate customised networks of varying size, with different cells stimulated, of varying duration from the command line:

    ./c302.py MyNetwork parameters_A -cells ["ADAL","AIBL","RIVR","RMEV"] -cellstostimulate ["ADAL","RIVR"] -duration 500
    
This will create a NeuroML 2 file and a LEMS file to execute it, containing 4 cells, stimulating 2 of them, and with a duration of 500 ms

More options can be found with 

    ./c302.py -h
    
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

- Implement & correctly tune **Parameters_B** (started), **Parameters_C**

- Modify to use [PyOpenWorm](https://github.com/openworm/PyOpenWorm) as source of connection data

- Move all of this to its own repository

- ~~Add to Geppetto for simulation of networks in browser~~ (done, see live.geppetto.org)

- Add muscle cells & connect output to muscle cell activity in [Sibernetic](http://openworm.github.io/Smoothed-Particle-Hydrodynamics/)

- Link to [bionet](https://github.com/portegys/bionet) to tune weights of network to physiological behaviour


