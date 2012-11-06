# This file uses https://github.com/NeuralEnsemble/libNeuroML to read in the C elegans connectome information in NeuroML
import os

# Uses code from https://github.com/NeuralEnsemble/libNeuroML/tree/dev/ideas/padraig/generatedFromV2Schema
from neuroml2 import *

reader = NeuroMLReader()

source_dir = "../CElegans/generatedNeuroML2/"

files=os.listdir(source_dir)

cell_count = 0
segment_count = 0
pop_count = 0
instance_count = 0
conn_count = 0

for fname in files:
    if fname.endswith(".nml"):
        print("---   Reading in %s"%fname)
        doc=reader.read_neuroml(source_dir+fname)

        for cell in doc.cell:
            cell_count +=1
            morph = cell.morphology
            print("Found a cell: %s with %i segments"% (cell.id, len(morph.segment)))
            segment_count += len(morph.segment)

        for net in doc.network:
            for pop in net.population:
                pop_count += 1
                instance_count += pop.size

            for conn in net.synapticConnection:
                conn_count += 1



print
print("Total cell definitions : %i"%cell_count)
print("Total segments         : %i"%segment_count)
print("Total populations      : %i containing %i cells with %i connections"%(pop_count, instance_count, conn_count))
print
            

        




