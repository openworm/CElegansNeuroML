# -*- coding: utf-8 -*-
from xlrd import open_workbook

############################################################

#    A simple script to read the values in CElegansNeuronTables.xls.
#    Should work with python or: nC.sh -python
#    Needs library xlrd, but this is included now with neuroConstruct

############################################################

filename = "../../../CElegansNeuronTables.xls"
rb = open_workbook(filename)

print(("Opened Excel file: "+ filename))


for row in range(2,rb.sheet_by_index(0).nrows):
  pre = rb.sheet_by_index(0).cell(row,0).value
  post = rb.sheet_by_index(0).cell(row,1).value
  syntype = rb.sheet_by_index(0).cell(row,2).value
  num = int(rb.sheet_by_index(0).cell(row,3).value)
  synclass = rb.sheet_by_index(0).cell(row,4).value

 
  
  print(("------------------------------------------\nConnection %i has %i from %s to %s (type: %s, synapse: %s)" %(row, num, pre, post, syntype, synclass)))
  

print("----------------------------------------------------------------------")


