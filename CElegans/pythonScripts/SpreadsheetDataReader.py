# -*- coding: utf-8 -*-
from NeuroMLUtilities import ConnectionInfo

from xlrd import open_workbook

############################################################

#    A simple script to read the values in CElegansNeuronTables.xls.

############################################################


def readDataFromSpreadsheet(dir="../../", include_nonconnected_cells=False):

    conns = []
    cells = []
    filename = dir+"CElegansNeuronTables.xls"
    rb = open_workbook(filename)

    print "Opened Excel file: "+ filename
    
    known_nonconnected_cells = ['CANL', 'CANR', 'VC6']


    for row in range(2,rb.sheet_by_index(0).nrows):
        pre = str(rb.sheet_by_index(0).cell(row,0).value)
        post = str(rb.sheet_by_index(0).cell(row,1).value)
        syntype = rb.sheet_by_index(0).cell(row,2).value
        num = int(rb.sheet_by_index(0).cell(row,3).value)
        synclass = rb.sheet_by_index(0).cell(row,4).value

        conns.append(ConnectionInfo(pre, post, num, syntype, synclass))
        if pre not in cells:
            cells.append(pre)
        if post not in cells:
            cells.append(post)
       
    if include_nonconnected_cells:
        for c in known_nonconnected_cells: cells.append(c)


    return cells, conns



def main():

    cells, conns = readDataFromSpreadsheet()
    
    print("%i cells in spreadsheet: %s"%(len(cells),sorted(cells)))
    
    from os import listdir
    from os.path import isfile
    cell_names = [ f[:-9] for f in listdir('../morphologies/') if f.endswith('.java.xml')]
    
    cell_names.remove('MDL08') # muscle 
    
    print("%i cell morphologies found: %s"%(len(cell_names),sorted(cell_names)))
    
    for c in cells: cell_names.remove(c)
    
    print("Difference: %s"%cell_names)
    
    
    cells2, conns2 = readDataFromSpreadsheet(include_nonconnected_cells=True)
    
    
    assert(len(cells2) == 302)
    
if __name__ == '__main__':
        
    main()