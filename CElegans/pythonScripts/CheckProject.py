#
#
#   A file which opens the CElegans neuroConstruct project, generates a number of Sim Configs
#   and checks for the correct number of cells, connections, etc.
#
#   Author: Padraig Gleeson
#
#   This file has been developed as part of the neuroConstruct and OpenWorm projects
#   This work has been funded by the Wellcome Trust
#
#

try:
	from java.io import File
	from java.lang import System
except ImportError:
	print "Note: this file should be run using ..\\nC.bat -python XXX.py' or './nC.sh -python XXX.py'"
	print "See http://www.neuroconstruct.org/docs/python.html for more details"
	quit()

from ucl.physiol.neuroconstruct.project import ProjectManager
from ucl.physiol.neuroconstruct.project.packing import SinglePositionedCellPackingAdapter
from ucl.physiol.neuroconstruct.neuron import NeuronSettings
from ucl.physiol.neuroconstruct.utils import Display3DProperties

from math import *
from random import *

import sys
from time import *


def testAll(argv=None):
    if argv is None:
        argv = sys.argv

    # Load an existing neuroConstruct project
    projFile = File("../CElegans.ncx")
    print "Loading project from file: " + projFile.getAbsolutePath()+", exists: "+ str(projFile.exists())

    pm = ProjectManager()
    project = pm.loadProject(projFile)
    print "Loaded project: " + project.getProjectName()


    defSimConfig = project.simConfigInfo.getDefaultSimConfig()
    cellsOnlySimConfig = project.simConfigInfo.getSimConfig("CellsOnly")
    pharyngealSimConfig = project.simConfigInfo.getSimConfig("PharyngealNeurons")
    mdl08SimConfig = project.simConfigInfo.getSimConfig("MDL08Connections")

    expectedNumberCells = 302 

    ''' 
    ##########################
    
    print "\n----- Test 1: Check number of cells in sim config "+defSimConfig.getName()+"..."


    pm.doGenerate(defSimConfig.getName(), 1234)

    while pm.isGenerating():
            print "Waiting for the project to be generated with Simulation Configuration: "+str(defSimConfig)
            sleep(2)

    numGenerated = project.generatedCellPositions.getNumberInAllCellGroups()

    print "Number of cells generated: " + str(numGenerated)

    assert numGenerated == expectedNumberCells

    print "Correct number of cells generated!"

    ##########################

    print "\n---- Test 2: number of cells in sim config "+cellsOnlySimConfig.getName()+"..."


    pm.doGenerate(cellsOnlySimConfig.getName(), 1234)

    while pm.isGenerating():
            print "Waiting for the project to be generated with Simulation Configuration: "+str(cellsOnlySimConfig)
            sleep(2)

    numGenerated = project.generatedCellPositions.getNumberInAllCellGroups()

    print "Number of cells generated: " + str(numGenerated)

    assert numGenerated == expectedNumberCells

    print "Correct number of cells generated!"
    
    ##########################

    filename = "../../CElegansNeuronTables.xls"
    print "\n---- Test 3: confirm settings in project match those in  "+filename+"..."

    from xlrd import open_workbook
    rb = open_workbook(filename)

    print "Opened Excel file: "+ filename

    confirmed = 0
    prefix = "NCXLS_"

    for row in range(1,rb.sheet_by_index(0).nrows):
      pre = rb.sheet_by_index(0).cell(row,0).value
      post = rb.sheet_by_index(0).cell(row,1).value
      syntype = rb.sheet_by_index(0).cell(row,2).value
      num = int(rb.sheet_by_index(0).cell(row,3).value)
      synclass = rb.sheet_by_index(0).cell(row,4).value

      #print "------------------------------------------\nConnection %i has %i from %s to %s (type: %s, synapse: %s)" %(row, num, pre, post, syntype, synclass)


      netConnName = prefix+pre+"_"+post

      if "GapJunction" in syntype:
            netConnName = netConnName + "_GJ"

      src = project.morphNetworkConnectionsInfo.getSourceCellGroup(netConnName)
      tgt = project.morphNetworkConnectionsInfo.getTargetCellGroup(netConnName)
      

      if not (src == pre and tgt == post):
          print "------------------------------------------\nConnection %i has %i from %s to %s (type: %s, synapse: %s)" %(row, num, pre, post, syntype, synclass)
          print "*** Couldn't find connection: %s, src: %s, tgt: %s"%(netConnName, src, tgt)
          assert src == pre
          assert tgt == post

      if src == tgt:
          print "------------------------------------------\nConnection %i has %i from %s to %s (type: %s, synapse: %s)" %(row, num, pre, post, syntype, synclass)
          print "*** This connection is from: %s, src: %s, tgt: %s, synaptic connection on same cell!!"%(netConnName, src, tgt)

      confirmed += 1

    print "Confirmed %i connections in project match spreadsheet"%confirmed

    havePrefix = 0
    allNetConnNames = project.morphNetworkConnectionsInfo.getAllSimpleNetConnNames()
    for name in allNetConnNames:
        if name.startswith(prefix):
            havePrefix +=1

    print "Project contains %i Network connections starting with %s"%(havePrefix, prefix)

    assert havePrefix == confirmed

    ##########################
    

    print "\n---- Test 4: number of cells in sim config "+pharyngealSimConfig.getName()+"..."


    pm.doGenerate(pharyngealSimConfig.getName(), 1234471)

    while pm.isGenerating():
            print "Waiting for the project to be generated with Simulation Configuration: "+str(pharyngealSimConfig)
            sleep(2)

    numCells = project.generatedCellPositions.getNumberInAllCellGroups()
    numConns = project.generatedNetworkConnections.getNumAllSynConns()

    print "Number of cells: %i, number of connections: %i"%(numCells,numConns)

    expectedCells = 20
    expectedNetConns = 269
    assert numCells == expectedCells
    assert numConns == expectedNetConns

    print "Correct number of cells & connections generated!"
    ##########################
    

    print "\n---- Test 5: number of cells in sim config "+mdl08SimConfig.getName()+"..."


    pm.doGenerate(mdl08SimConfig.getName(), 1234471)

    while pm.isGenerating():
            print "Waiting for the project to be generated with Simulation Configuration: "+str(mdl08SimConfig)
            sleep(2)

    numCells = project.generatedCellPositions.getNumberInAllCellGroups()
    numConns = project.generatedNetworkConnections.getNumAllSynConns()

    print "Number of cells: %i, number of connections: %i"%(numCells,numConns)

    expectedCells = 9
    expectedNetConns = 21
    assert numCells == expectedCells
    assert numConns == expectedNetConns

    print "Correct number of cells & connections generated!"

    ##########################
    '''
    

    print "\n---- Test 6: General neuroConstruct project settings..."


    assert(project.proj3Dproperties.getDisplayOption() == Display3DProperties.DISPLAY_SOMA_NEURITE_SOLID)

    assert(abs(project.simulationParameters.getDt()-0.025)<=1e-9)

    assert(not project.neuronSettings.isVarTimeStep())

    assert(project.neuronSettings.getDataSaveFormat().equals(NeuronSettings.DataSaveFormat.TEXT_NC))

    assert(abs(project.simulationParameters.getTemperature() - 20.0) < 1e-6)

    ##########################


    print "\n------------------------------------------All tests completed!\n"

    exit()


if __name__ == "__main__":
    testAll()
