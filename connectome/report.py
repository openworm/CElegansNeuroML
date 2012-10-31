# This file uses https://github.com/NeuralEnsemble/libNeuroML to read in the C elegans connectome information in NeuroML
import os

# Uses code from https://github.com/NeuralEnsemble/libNeuroML/tree/dev/ideas/padraig/generatedFromV2Schema
from neuroml2 import *

reader = NeuroMLReader()

source_dir = "../CElegans/generatedNeuroML2/"

files=os.listdir(source_dir)

cell_count = 0
segment_count = 0

for fname in files:
    if fname.endswith(".nml"):
        print("---   Reading in %s"%fname)
        doc=reader.read_neuroml(source_dir+fname)

        for cell in doc.cell:
            cell_count +=1
            morph = cell.morphology
            print("Found a cell: %s with %i segments"% (cell.id, len(morph.segment)))
            segment_count += len(morph.segment)


print ("Total cells: %i"%cell_count)
print ("Total segments: %i"%segment_count)
            

        




