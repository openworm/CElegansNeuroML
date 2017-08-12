# -*- coding: utf-8 -*-
#
#   Author: Padraig Gleeson
#
#   This file has been developed as part of the neuroConstruct project
#   This work has been funded by the Medical Research Council and the
#   Wellcome Trust
#
#

try:
	from java.io import File
	from java.lang import System
except ImportError:
	print("Note: this file should be run using ..\\nC.bat -python XXX.py' or './nC.sh -python XXX.py'")
	print("See http://www.neuroconstruct.org/docs/python.html for more details")
	quit()

from ucl.physiol.neuroconstruct.project import ProjectManager
from ucl.physiol.neuroconstruct.cell import ChannelMechanism

from math import *
from random import *

# Load an existing neuroConstruct project
projFile = File("../CElegans.ncx")
print(("Loading project from file: " + projFile.getAbsolutePath()+", exists: "+ str(projFile.exists())))

pm = ProjectManager()
project = pm.loadProject(projFile)
print(("Loaded project: " + project.getProjectName()))


channelDensities = {}
channelDensities["LeakConductance"] = ["all", 2.5e-10] # mS μm-2, Typical value for mammalian central neurons...



cells = project.cellManager.getAllCells()

for cell in cells:

    for chan in channelDensities.keys():
        group = channelDensities[chan][0]
        dens = float(channelDensities[chan][1])

        cm = ChannelMechanism(chan, dens)

        print(("Looking at adding %s to cell %s..."%(str(cm), cell)))
        cell.associateGroupWithChanMech(group, cm)


# Save project & exit
project.markProjectAsEdited()
project.saveProject()


##System.exit(0)

