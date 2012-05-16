
#
#
#   A file which opens the CElegans neuroConstruct project, and saves generated network in NeuroML format
#
#   Author: Padraig Gleeson
#
#   This file has been developed as part of the neuroConstruct and OpenWorm projects
#   This work has been funded by the Wellcome Trust
#
#

try:
	from java.io import File
except ImportError:
	print "Note: this file should be run using ..\\nC.bat -python XXX.py' or './nC.sh -python XXX.py'"
	print "See http://www.neuroconstruct.org/docs/python.html for more details"
	quit()
	
import sys
from time import *

from ucl.physiol.neuroconstruct.project import ProjectManager



# Load an existing neuroConstruct project
projFile = File("../CElegans.ncx")
print "Loading project from file: " + projFile.getAbsolutePath()+", exists: "+ str(projFile.exists())

pm = ProjectManager()
project = pm.loadProject(projFile)
print "Loaded project: " + project.getProjectName()


simConfig = project.simConfigInfo.getSimConfig("CellsOnly")

expectedNumberCells = 302


##########################


pm.doGenerate(simConfig.getName(), 1234)

while pm.isGenerating():
        print "Waiting for the project to be generated with Simulation Configuration: "+str(simConfig)
        sleep(2)

numGenerated = project.generatedCellPositions.getNumberInAllCellGroups()

print "Number of cells generated: " + str(numGenerated)

assert numGenerated == expectedNumberCells

print "Correct number of cells generated!"

nmlFileName = "GeneratedNeuroML.xml"

pm.saveLevel3NetworkXML(project,
                        File(nmlFileName),
                        False,
                        True,
                        False,
                        simConfig.getName(),
                        "Physiological Units")

print "Done!"




