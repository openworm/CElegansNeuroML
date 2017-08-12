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
	from java.io import *
	from java.lang import *
	from java.util import *
except ImportError:
	print("Note: this file should be run using ..\\nC.bat -python XXX.py' or './nC.sh -python XXX.py'")
	print("See http://www.neuroconstruct.org/docs/python.html for more details")
	quit()

from ucl.physiol.neuroconstruct.project import ProjectManager
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

simConfigForConnsName = "ConnectionsFromSpreadsheet"

simConfig = project.simConfigInfo.getSimConfig(simConfigForConnsName)


cgs = project.cellGroupsInfo.getAllCellGroupNames()

for cg in cgs:
    print(("Looking at cell group %s..."%(cg)))
    simConfig.addCellGroup(cg)


netConnInfo = project.morphNetworkConnectionsInfo  # Simple/morph based net conns only

print(("Currently there are %i morph based net conns"%netConnInfo.getNumSimpleNetConns()))


prefix = "NCXLS_"

deleteConnections = False

if deleteConnections:
    allNetConnNames = project.morphNetworkConnectionsInfo.getAllSimpleNetConnNames()
    for name in allNetConnNames:
        print(name)
        if name.startswith(prefix):
            print(("Deleting: "+name))
            project.morphNetworkConnectionsInfo.deleteNetConn(name)

    print(("Currently there are %i morph based net conns"%netConnInfo.getNumSimpleNetConns()))

else:

    from xlrd import open_workbook
    filename = "../../../CElegansNeuronTables.xls"
    rb = open_workbook(filename)

    print(("Opened Excel file: "+ filename))

    netConnInfo = project.morphNetworkConnectionsInfo  # Simple/morph based net conns only


    for row in range(1,rb.sheet_by_index(0).nrows):

        pre = str(rb.sheet_by_index(0).cell(row,0).value)
        post = str(rb.sheet_by_index(0).cell(row,1).value)
        syntype = str(rb.sheet_by_index(0).cell(row,2).value)
        num = int(rb.sheet_by_index(0).cell(row,3).value)
        synclass = str(rb.sheet_by_index(0).cell(row,4).value)


        print(("------------------------------------------\nConnection %i has %i from %s to %s (type: %s, synapse: %s)" %(row, num, pre, post, syntype, synclass)))

        source = pre
        target = post
        syns0 = synclass.strip(" ").split(",")
        syns = []

        for syn in syns0:
            syn = str(str(syn).strip())
            if len(syn)<2:
                syn ="Unknown"

            if "FRMFemide" in syn:
                syn = "FMRFamide"

            if "GapJunction" in syntype:
                if "_GJ" not in syn:
                    syn =  "%s_GJ"%syn
                print(("Electrical syn: "+syn))
            else:
                print(("Chemical syn: "+syn))
            syns.append(syn)


        preCell = project.cellManager.getCell(project.cellGroupsInfo.getCellType(source))
        postCell = project.cellManager.getCell(project.cellGroupsInfo.getCellType(target))

        numPre = int(num)
        default_syn_delay=0
        preGroup = "axon_group"
        postGroup = "dendrite_group"

        if not "dendrite_group" in postCell.getAllGroupNames():
            postGroup = "soma_group"

        netConnName = prefix+source+"_"+target

        if "GapJunction" in syntype:
            netConnName = netConnName + "_GJ"
            default_syn_delay = 0
            postGroup = preGroup

        print(("Creating a net conn: %s where points in %s of %g cells of %s contact each cell in %s with syns: %s on group %s" % (netConnName, preGroup, numPre, source, target, syns, postGroup)))

        synList = Vector()
        cellMechNames = project.cellMechanismInfo.getAllCellMechanismNames()



        for syn in syns:

            print(syn)
            if not syn in cellMechNames:
                print(("Synapse mechanism %s not found in project!"%syn))
                exit()

            synProp = SynapticProperties(syn)
            synProp.setThreshold(0)
            synProp.setFixedDelay(default_syn_delay)
            synList.add(synProp)


        searchPattern = SearchPattern.getRandomSearchPattern()
        #searchPattern = SearchPattern.getClosestSearchPattern() # will be better, but slower!
        maxMinLength = MaxMinLength()

        connectivityConditions = ConnectivityConditions()
        connectivityConditions.setGenerationDirection(ConnectivityConditions.SOURCE_TO_TARGET)

        connectivityConditions.setNumConnsInitiatingCellGroup(NumberGenerator(numPre))

        print(("Set NumConnsInitiatingCellGroup to %i"%numPre))
        
        
        if "axon" in postGroup:
            connectivityConditions.getPrePostAllowedLoc().setAxonsAllowedPost(1)
            connectivityConditions.getPrePostAllowedLoc().setDendritesAllowedPost(0)
            connectivityConditions.getPrePostAllowedLoc().setSomaAllowedPost(0)

        print(("Set connectivityConditions: " + str(connectivityConditions)))

        connectivityConditions.setAllowAutapses(0)

        if("Elect" in syns[0]):
            connectivityConditions.setNoRecurrent(1)


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


        #print "Syns vs groups: %s"%preCell.getSynapsesVsGroups()

        for syn in syns:

            if not preGroup in preCell.getAllGroupNames():
                print(("Group %s not found in PRE cell %s"%(preGroup, preCell)))
                exit()

            res = preCell.associateGroupWithSynapse(preGroup, syn)
            print(("Associated %s with PRE group %s: %s" % (preGroup, syn, res)))

            if not postGroup in postCell.getAllGroupNames():
                print(("Group %s not found in POST cell %s"%(postGroup, postCell)))
                exit()
            res = postCell.associateGroupWithSynapse(postGroup, syn)
            print(("Associated %s with POST group %s: %s" % (postGroup, syn, res)))

        simConfig.addNetConn(netConnName)


    simPlots = project.simPlotInfo.getAllSimPlots()

    for sp in simPlots:
        simConfig.addPlot(sp.getPlotReference())

    print((project.simConfigInfo.getSimConfig(simConfigForConnsName).toLongString()))


# Save project & exit
print("Saving project!!")
project.markProjectAsEdited()
project.saveProject()




System.exit(0)