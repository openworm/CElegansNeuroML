cd ../examples
rm *.hoc *.mod *nrn.py
# jnml LEMS_c302_C_Muscles.xml -neuron -nogui
# jnml LEMS_c302_C1_Syns.xml -neuron -nogui
jnml LEMS_c302_C1_Full.xml -neuron -nogui
cp *.hoc *.mod *nrn.py ../neuron_interaction
cd -
rm -rf x86_64
nrnivmodl