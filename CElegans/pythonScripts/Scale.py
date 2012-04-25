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
	print "Note: this file should be run using ..\\nC.bat -python XXX.py' or './nC.sh -python XXX.py'"
	print "See http://www.neuroconstruct.org/docs/python.html for more details"
	quit()

from ucl.physiol.neuroconstruct.project import ProjectManager

from math import *
from random import *

# Load an existing neuroConstruct project
projFile = File("../CElegans.ncx")
print "Loading project from file: " + projFile.getAbsolutePath()+", exists: "+ str(projFile.exists())

pm = ProjectManager()
project = pm.loadProject(projFile)
print "Loaded project: " + project.getProjectName()

scale = 100

cells = project.cellManager.getAllCells()

for cell in cells:

    print "--- Looking at cell: "+cell.getInstanceName()+", "+cell.getMorphSummary()

    for seg in cell.getAllSegments():
        if seg.isFirstSectionSegment():
            sec = seg.getSection()
            p = sec.getStartPointPosition()
            sec.setStartPointPositionX(p.x * scale)
            sec.setStartPointPositionY(p.y * scale)
            sec.setStartPointPositionZ(p.z * scale)
            sec.setStartRadius(sec.getStartRadius() * scale)
            print sec

        p = seg.getEndPointPosition()
        seg.setEndPointPositionX(p.x * scale)
        seg.setEndPointPositionY(p.y * scale)
        seg.setEndPointPositionZ(p.z * scale)
        seg.setRadius(seg.getRadius() * scale)
        

# Save project & exit
project.markProjectAsEdited()
project.saveProject()


##System.exit(0)

