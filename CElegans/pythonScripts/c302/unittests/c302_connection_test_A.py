#############################################################################
#  This file contains two unittests that test .nml files generated through
#  parameters_A.py

#  First Test verifies whether connections exist in .nml files as specified in
#  CElegensNeuronTables

#  Second test verifies whether connections exist in .nml files as specified in
#  NeuronConnectFormatted.xls. Test does not verify type or number of
#  connections in case of a chemical synapse. Errors are written to a log file
#  error_log.xls

#############################################################################

import os

import sys
sys.path.append("../..")
import SpreadsheetDataReader

sys.path.append("..")
from c302 import generate
import parameters_A as params

import neuroml.loaders as loaders

import xlwt

import unittest


class DataIntegrityTest(unittest.TestCase):

    checked_files = []
    counter = 0

    @classmethod
    def setUpClass(cls):

        # generate files from pairs in CElegensNeuronTables
        cls.cell_names, cls.conns = SpreadsheetDataReader.readDataFromSpreadsheet("../../../../")
        print (str(len(cls.cell_names))+' unique cell names in CElegensNeuronTables')

        for index in cls.conns:
            origin = index.pre_cell
            target = index.post_cell

            fn = origin+"_"+target
            fnswap = target+"_"+origin

            if fn not in cls.checked_files:
                if fnswap not in cls.checked_files:
                    # generate xml and nml file
                    cells_to_plot = "["+origin+","+target+"]"
                    cells_to_stimulate = "["+origin+"]"

                    generate(fn, params, cells=cells_to_plot, cells_to_stimulate=cells_to_stimulate,            duration=500, test=True)

                    cls.checked_files.append(fn)
                    cls.counter += 1

        # generate files from pairs not present in CElegensNeuronTables but in NeuronConnect.xls

        cls.neuron_cell_names, cls.neuron_conns = SpreadsheetDataReader.readDataFromSpreadsheet("../../../../", neuron_connect=True)

        print (str(len(cls.neuron_cell_names))+' unique cell names in NeuronConnectFormatted')
        for index in cls.neuron_conns:
            origin = index.pre_cell
            target = index.post_cell
            fn = origin+"_"+target
            fnswap = target+"_"+origin

            if fn not in cls.checked_files:
                if fnswap not in cls.checked_files:
                    # generate xml and nml file
                    cells_to_plot = "["+origin+","+target+"]"
                    cells_to_stimulate = "["+origin+"]"

                    generate(fn, params, cells=cells_to_plot, cells_to_stimulate=cells_to_stimulate,            duration=500, test=True)

                    cls.checked_files.append(fn)
                    cls.counter += 1
        print ("Total files generated %i"%cls.counter)

    def test_c302_connections(self):

        # test each connection pair from the excel file

        print('Initiating Connection test for CElegensNeuronTables.xls')
        counter = 0
        for index in self.conns:

            origin = index.pre_cell
            target = index.post_cell
            num = index.number
            synclass = index.synclass

            fn = origin+"_"+target
            fnswap = target+"_"+origin

            test_id = 'NC_'+origin+'_'+target+'_'+synclass
            if '_GJ' in synclass:
                test_synapse = 'elec_syn_'+str(num)+'conns'
            elif 'GABA' in synclass:
                test_synapse = 'inh_syn_'+str(num)+'conns'
            else:
                test_synapse = 'exc_syn_'+str(num)+'conns'

            if fn in self.checked_files:
                nml_file = fn+'.nml'
            elif fnswap in self.checked_files:
                nml_file = fnswap+'.nml'
            else:
                print ("File not found")

            doc = loaders.NeuroMLLoader.load(nml_file)

            conn_list = doc.networks[0].projections

            # test if any connections exist
            self.assertNotEqual(conn_list, [], 'Connection list is empty for %s'+nml_file)

            test_list = []

            test_list = [(connection.id, connection.synapse) for connection in conn_list]

           # test if this particular connection exists
            test_pair = (test_id, test_synapse)
            self.assertIn(test_pair, test_list, "connection not found")
            counter += 1

        print ("Total connections verified %i"%counter)

    def test_neuronconnect_connections(self):

        # initiate error log file
        print('Initiating connection test for NeuronConnectFormatted.xlsx')
        book = xlwt.Workbook()
        sh = book.add_sheet('Error Log')
        col1_name = 'Origin'
        col2_name = 'Target'
        col3_name = 'Issue'
        sh.write(0, 0, col1_name)
        sh.write(0, 1, col2_name)
        sh.write(0, 2, col3_name)
        rowcounter = 1

        counter = 0
        for index in self.neuron_conns:

            origin = index.pre_cell
            target = index.post_cell
            syntype = index.syntype
            num = index.number

            fn = origin+"_"+target
            fnswap = target+"_"+origin

            #check if the connection is a GAP junction or a checmical synapse
            gap_junction = True
            if 'EJ' in syntype:
                test_id = 'NC_'+origin+'_'+target+'_'+'Generic_GJ'
                test_synapse = 'elec_syn_'+str(num)+'conns'

            else:
                test_id = 'NC_'+origin+'_'+target
                gap_junction = False

            if fn in self.checked_files:
                nml_file = fn+'.nml'
            elif fnswap in self.checked_files:
                nml_file = fnswap+'.nml'
            else:
                print ("File not found")

            doc = loaders.NeuroMLLoader.load(nml_file)

            conn_list = doc.networks[0].projections

            # test if any connections exist
            try:
                self.assertNotEqual(conn_list, [])
            except AssertionError:
                sh.write(rowcounter, 0, origin)
                sh.write(rowcounter, 1, target)
                sh.write(rowcounter, 2, 'Connection List is empty in .nml file')
                rowcounter += 1

            if conn_list:

                test_list = []
                test_id_list = []
                test_synapse_list = []
                for connection in conn_list:
                    test_list.append((connection.id, connection.synapse))
                    test_id_list.append(connection.id)
                    test_synapse_list.append(connection.synapse)

            # test if this particular connection exists (Only testing connection end points and number) and writing errors to log file

                # if gap junction
                if gap_junction:

                    try:
                        self.assertIn(test_id, test_id_list)
                    except AssertionError:
                        sh.write(rowcounter, 0, origin)
                        sh.write(rowcounter, 1, target)
                        sh.write(rowcounter, 2, syntype+' Connection Not Found in .nml file')
                        rowcounter += 1
                    try:
                        self.assertIn(test_synapse, test_synapse_list)
                    except AssertionError:
                        sh.write(rowcounter, 0, origin)
                        sh.write(rowcounter, 1, target)
                        sh.write(rowcounter, 2, syntype+' No. of connections incorrect in .nml file')
                        rowcounter += 1

                # if chemical synapse (synapse type and number of connections not being tested)
                else:

                    flag1 = False
                    # flag2 = False
                    for id_test in test_list:
                        if test_id in id_test[0]:
                            flag1 = True
                            # flag2 = True if str(num) in id_test[1] else False
                            break

                    try:
                        self.assertTrue(flag1)
                    except AssertionError:
                        sh.write(rowcounter, 0, origin)
                        sh.write(rowcounter, 1, target)
                        sh.write(rowcounter, 2, syntype+' Connection Not Found in .nml file')
                        rowcounter += 1

            counter += 1

        print ("Total connections tested %i"%counter)

        # write errors to a log file
        if rowcounter > 1:
            print ("Total Errors Found %i"%(rowcounter-1))
            book.save('error_log.xls')
            print ("Errors written to error_log.xls")

    @classmethod
    def tearDownClass(cls):
        print ("Cleaning up .. ")
        for name in cls.checked_files:
            bashCommand = "rm "+name+".nml "+"LEMS_"+name+".xml"
            os.system(bashCommand)

if __name__ == '__main__':
    unittest.main()
