import os

import sys
sys.path.append("../..")
import SpreadsheetDataReader

sys.path.append("..")
from c302 import generate
import parameters_A as params

import xlwt

import neuroml.loaders as loaders

import unittest


class DataIntegrityTest(unittest.TestCase):

    def setUp(self):

        # open excel file NeuronConnect.xls
        self.cell_names, self.conns = SpreadsheetDataReader.readDataFromSpreadsheet(
            "../../../../", neuron_connect = True)
        print len(self.cell_names)

        # generate all files at once. This will throw an error if done with the complete excel file, because all cells in NeuronConnect are not defined in libNeuroML

        self.checked_files = []
        counter = 0
        # self.specify_early_stop = 100     # early stopping
        # early_stop = self.specify_early_stop     # early stopping
        for index in self.conns:
            # if early_stop == 0:  # early stopping
                # break  # and this

            origin = index.pre_cell
            target = index.post_cell

            fn = origin+"_"+target
            fnswap = target+"_"+origin

            if fn not in self.checked_files:
                if fnswap not in self.checked_files:
                    # generate xml and nml file
                    cells_to_plot = "["+origin+","+target+"]"
                    cells_to_stimulate = "["+origin+"]"

                    generate(fn, params, cells=cells_to_plot, cells_to_stimulate=cells_to_stimulate,            duration=500, test=True)

                    # bashCommand = 'python c302.py '+fn+' parameters_A -cells '+cells_to_plot+' -cellstostimulate '+cells_to_stimulate+' -duration 500'
                    # os.system(bashCommand)
                    self.checked_files.append(fn)
                    counter += 1

            # early_stop -= 1         # early stopping
        print "Total files generated %i"%counter

    def test_neuronconnect_connections(self):

        # initiate error log file
        book = xlwt.Workbook()
        sh = book.add_sheet('Error Log')
        col1_name = 'Origin'
        col2_name = 'Target'
        col3_name = 'Issue'
        sh.write(0, 0, col1_name)
        sh.write(0, 1, col2_name)
        sh.write(0, 2, col3_name)
        rowcounter = 1

        # early_stop = self.specify_early_stop         # early stopping
        counter = 0
        for index in self.conns:

            # if early_stop == 0:  # early stopping
                # break  # and this

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

            print test_id, num

            if fn in self.checked_files:
                nml_file = fn+'.nml'
            elif fnswap in self.checked_files:
                nml_file = fnswap+'.nml'
            else:
                print "File not found"

            doc = loaders.NeuroMLLoader.load(nml_file)
            print("Loaded NML file from: "+nml_file)

            conn_list = doc.networks[0].projections

            # test if any connections exist
            try:
                self.assertNotEqual(conn_list, [])
            except AssertionError:
                print "Connection list is empty for "+nml_file
                sh.write(rowcounter, 0, origin)
                sh.write(rowcounter, 1, target)
                sh.write(rowcounter, 2, 'Connection List is empty')
                rowcounter += 1

            if conn_list:

                test_list = []
                test_id_list = []
                test_synapse_list = []
                for connection in conn_list:
                    test_list.append((connection.id, connection.synapse))
                    test_id_list.append(connection.id)
                    test_synapse_list.append(connection.synapse)

                print test_list

            # test if this particular connection exists (Only testing connection end points and number) and writing errors to log file

                # if gap junction
                if gap_junction:

                    try:
                        self.assertIn(test_id, test_id_list)
                    except AssertionError:
                        print "Gap Junction Connection not found for "+nml_file
                        sh.write(rowcounter, 0, origin)
                        sh.write(rowcounter, 1, target)
                        sh.write(rowcounter, 2, syntype+' Connection Not Found')
                        rowcounter += 1
                    try:
                        self.assertIn(test_synapse, test_synapse_list)
                    except AssertionError:
                        print "EJ Number of Connections incorrect for "+nml_file
                        sh.write(rowcounter, 0, origin)
                        sh.write(rowcounter, 1, target)
                        sh.write(rowcounter, 2, syntype+' No. of connections incorrect')
                        rowcounter += 1

                # if chemical synapse (synapse type and number of connections not being tested)
                else:

                    flag1 = False
                    # flag2 = False
                    for id_test in test_list:
                        if test_id in id_test[0]:
                            print id_test
                            flag1 = True
                            # flag2 = True if str(num) in id_test[1] else False
                            break

                    try:
                        self.assertTrue(flag1)
                    except AssertionError:
                        print "Synaptic Connection not found for "+nml_file
                        sh.write(rowcounter, 0, origin)
                        sh.write(rowcounter, 1, target)
                        sh.write(rowcounter, 2, syntype+' Connection Not Found')
                        rowcounter += 1

                    # try:
                    #     self.assertTrue(flag2)
                    # except AssertionError:
                    #     print "Synaptic Connection number incorrect for "+nml_file
                    #     sh.write(rowcounter, 0, origin)
                    #     sh.write(rowcounter, 1, target)
                    #     sh.write(rowcounter, 2, syntype+' Connection number incorrect')
                    #     rowcounter += 1

            counter += 1

            # early_stop -= 1         # early stopping
        print "Total connections tested %i"%counter

        # write errors to a log file
        if rowcounter > 1:
            print "Total Errors Found %i"%(rowcounter-1)
            book.save('error_log.xls')
            print "Errors written to error_log.xls"

    def tearDown(self):
        print "Cleaning up .. "
        for name in self.checked_files:
            bashCommand = "rm "+name+".nml "+"LEMS_"+name+".xml"
            os.system(bashCommand)

if __name__ == '__main__':
    unittest.main()
