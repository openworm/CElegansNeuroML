# -*- coding: utf-8 -*-
#
# Author: Padraig Gleeson
#
# This file has been developed as part of the neuroConstruct project
# This work has been funded by the Medical Research Council and the
# Wellcome Trust
#
#

try:
    from java.io import *
    from java.lang import *
    from java.util import *
except ImportError:
    print "Note: this file should be run using ..\\nC.bat -python XXX.py' or './nC.sh -python XXX.py'"
    print "See http://www.neuroconstruct.org/docs/python.html for more details"
    quit()

from ucl.physiol.neuroconstruct.project import ProjectManager
from ucl.physiol.neuroconstruct.project import SimConfig

from math import *
from random import *

# Load an existing neuroConstruct project
projFile = File("../../CElegans.ncx")
print "Loading project from file: " + projFile.getAbsolutePath()+", exists: "+ str(projFile.exists())

pm = ProjectManager()
project = pm.loadProject(projFile)
print "Loaded project: " + project.getProjectName()


##########################

newSimConfig = "MDL08Connections"
newSimConfigDesc = "Generates a subset of the CElegans neural system consisting of the MDL08 muscle and motor neurons which connect to it. See https://github.com/openworm/OpenWorm/issues/53"
cells = ["AS1", "AS2", "DA1", "DA2", "DB1", "DD1", "SMDDL", "SMDDR", "MDL08"]


##########################

simConfig = SimConfig(newSimConfig, newSimConfigDesc)

for cell in cells:
    simConfig.addCellGroup(cell)

'''
prefix = "NCXLS_"

allNetConnNames = project.morphNetworkConnectionsInfo.getAllSimpleNetConnNames()
for name in allNetConnNames:
    if prefix in name:
        for cell in cells:
            if cell in name:
                if not name in simConfig.getNetConns():
                    simConfig.addNetConn(name)
'''


simPlots = project.simPlotInfo.getAllSimPlots()

for sp in simPlots:
    for cell in cells:
        if cell in sp.getPlotReference():
            simConfig.addPlot(sp.getPlotReference())

print simConfig.toLongString()

project.simConfigInfo.add(simConfig)

# Save project & exit
print "Saving project!!"
project.markProjectAsEdited()
project.saveProject()


System.exit(0)