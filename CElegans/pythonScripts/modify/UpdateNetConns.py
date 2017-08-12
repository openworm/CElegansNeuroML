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
from ucl.physiol.neuroconstruct.project import SearchPattern
from ucl.physiol.neuroconstruct.project import MaxMinLength

from math import *
from random import *

# Load an existing neuroConstruct project
projFile = File("../../CElegans.ncx")
print(("Loading project from file: " + projFile.getAbsolutePath()+", exists: "+ str(projFile.exists())))

pm = ProjectManager()
project = pm.loadProject(projFile)
print(("Loaded project: " + project.getProjectName()))

'''
prefix = "NCXLS_"

allNetConnNames = project.morphNetworkConnectionsInfo.getAllSimpleNetConnNames()
for name in allNetConnNames:
    if prefix in name:
        sp = SearchPattern.getRandomSearchPattern()
        src = project.morphNetworkConnectionsInfo.setSearchPattern(name,sp)
    print "%s: %s"%(name, project.morphNetworkConnectionsInfo.getSearchPattern(name))

    cc = project.morphNetworkConnectionsInfo.getConnectivityConditions(name)

    cc.getPrePostAllowedLoc().setAxonsAllowedPost(1)
    cc.getPrePostAllowedLoc().setDendritesAllowedPost(1)
    cc.getPrePostAllowedLoc().setSomaAllowedPost(1)

    cc.getPrePostAllowedLoc().setAxonsAllowedPre(1)
    cc.getPrePostAllowedLoc().setDendritesAllowedPre(1)
    cc.getPrePostAllowedLoc().setSomaAllowedPre(1)

    project.morphNetworkConnectionsInfo.setConnectivityConditions(name,cc)

    mml = MaxMinLength(50, 0, "r", 5000)
    project.morphNetworkConnectionsInfo.setMaxMinLength(name, mml)
'''

allCells = project.cellManager.getAllCells()
for cell in allCells:

    svg = cell.getSynapsesVsGroups()
    print(cell)
    print(svg)
    syns = ["Generic_GJ"]
    #syns.extend(svg.keySet())
    for syn in syns:
        cell.disassociateGroupFromSynapse("dendrite_group", syn)
        cell.disassociateGroupFromSynapse("axon_group", syn)
        cell.disassociateGroupFromSynapse("soma_group", syn)
        cell.associateGroupWithSynapse("all", syn)
    print((cell.getSynapsesVsGroups()))

# Save project & exit
project.markProjectAsEdited()
project.saveProject()


System.exit(0)
##

