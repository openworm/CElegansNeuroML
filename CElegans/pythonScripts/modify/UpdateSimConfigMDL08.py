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
    print("Note: this file should be run using ..\\nC.bat -python XXX.py' or './nC.sh -python XXX.py'")
    print("See http://www.neuroconstruct.org/docs/python.html for more details")
    quit()

from ucl.physiol.neuroconstruct.project import ProjectManager
from ucl.physiol.neuroconstruct.project import SimConfig
from ucl.physiol.neuroconstruct.project import SynapticProperties
from ucl.physiol.neuroconstruct.project import SearchPattern
from ucl.physiol.neuroconstruct.project import MaxMinLength
from ucl.physiol.neuroconstruct.project import ConnectivityConditions
from ucl.physiol.neuroconstruct.utils import NumberGenerator

from math import *
from random import *

# Load an existing neuroConstruct project
projFile = File("../../CElegans.ncx")
print(("Loading project from file: " + projFile.getAbsolutePath()+", exists: "+ str(projFile.exists())))

pm = ProjectManager()
project = pm.loadProject(projFile)
print(("Loaded project: " + project.getProjectName()))


##########################

newSimConfig = "MDL08Connections"

cells = ["AS1", "AS2", "DA1", "DA2", "DB1", "DD1", "SMDDL", "SMDDR"]
conns = [ 3,     2,     8,     1,     1,     4,     1,       1]



##########################

simConfig = project.simConfigInfo.getSimConfig(newSimConfig)

print((simConfig.toLongString()))
##for cell in cells:
#    simConfig.addCellGroup(cell)


netConnInfo = project.morphNetworkConnectionsInfo  # Simple/morph based net conns only

print(("Currently there are %i morph based net conns"%netConnInfo.getNumSimpleNetConns()))


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

prefix = "NCM_"
target = "MDL08"


for cell in cells:

        source = cell
        netConnName = prefix+source+"_"+target

        searchPattern = SearchPattern.getRandomSearchPattern()
        #searchPattern = SearchPattern.getClosestSearchPattern() # will be better, but slower!
        maxMinLength = MaxMinLength()

        connectivityConditions = ConnectivityConditions()
        connectivityConditions.setGenerationDirection(ConnectivityConditions.SOURCE_TO_TARGET)

        num = conns[cells.index(cell)]
        connectivityConditions.setNumConnsInitiatingCellGroup(NumberGenerator(num))

        print(("Set NumConnsInitiatingCellGroup to %i"%num))

        '''
        if "axon" in postGroup:
            connectivityConditions.getPrePostAllowedLoc().setAxonsAllowedPost(1)
            connectivityConditions.getPrePostAllowedLoc().setDendritesAllowedPost(0)
            connectivityConditions.getPrePostAllowedLoc().setSomaAllowedPost(0)
        '''
        print(("Set connectivityConditions: " + str(connectivityConditions)))

        connectivityConditions.setAllowAutapses(0)

        synList = Vector()
        cellMechNames = project.cellMechanismInfo.getAllCellMechanismNames()

        syn = "Acetylcholine"
        if cell is "DD1":
            syn = "GABA"

        default_syn_delay=0
        synProp = SynapticProperties(syn)
        synProp.setThreshold(0)
        synProp.setFixedDelay(default_syn_delay)
        synList.add(synProp)


        netConnInfo.deleteNetConn(netConnName)

        netConnInfo.addNetConn(netConnName,
                               source,
                               target,
                               synList,
                               searchPattern,
                               maxMinLength,
                               connectivityConditions,
                               Float.MAX_VALUE)

        print((netConnInfo.getSummary(netConnName)))

        simConfig.addNetConn(netConnName)


print((simConfig.toLongString()))



# Save project & exit
print("Saving project!!")
project.markProjectAsEdited()
project.saveProject()


System.exit(0)