from LEMS_c302_C1_Syns_nrn import NeuronSimulation

ns = NeuronSimulation(tstop=1200.0, dt=0.1)

ns.run()