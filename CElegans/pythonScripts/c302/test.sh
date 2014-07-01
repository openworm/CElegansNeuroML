set -e

##   (Re)generate NeuroML 2 & LEMS files from the python scripts

python c302_A.py
python c302_A_Pharyngeal.py
python c302_A_Syns.py


## Validate generated NeuroML 2

jnml -validate c302_A.nml
jnml -validate c302_A_Pharyngeal.nml
jnml -validate c302_A_Syns.nml


## Try running these in jNeuroML with no GUI

#jnml LEMS_c302_A.xml -nogui    #  Takes 2 mins to run!
jnml LEMS_c302_A_Pharyngeal.xml -nogui
jnml LEMS_c302_A_Syns.xml -nogui


## Try regenerating using command line options

python c302.py c302_A_Syns parameters_A -cells ["ADAL","AIBL","RIVR","RMEV"] -cellstostimulate ["ADAL","RIVR"] -duration 500 -dt 0.1 -vmin -72 -vmax -48

python c302.py c302_A_Weights parameters_A -cells ["ADAL","AIBL","I1L","I3","DB5","PVCR"] -cellstostimulate ["ADAL","I1L","PVCR"] -connnumberoverride=["I1L-I3":2.5] -connnumberscaling=["PVCR-DB5":5] -duration 500 -dt 0.1 -vmin -72 -vmax -48


## Try converting it to NEURON

jnml LEMS_c302_A.xml -neuron
jnml LEMS_c302_A_Pharyngeal.xml -neuron
jnml LEMS_c302_A_Syns.xml -neuron
nrnivmodl