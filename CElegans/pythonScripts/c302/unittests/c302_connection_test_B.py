#############################################################################

#  Test generates all .nml files for connection pairs in CElegensNeuronTables
#  spreadsheet using parameters_B and checks whether connections exist as
#  specified

#############################################################################

import os

import sys
sys.path.append("../..")
import SpreadsheetDataReader

sys.path.append("..")
from c302 import generate

from parameters_B import ParameterisedModel
params = ParameterisedModel()

import neuroml.loaders as loaders

import unittest


class DataIntegrityTest(unittest.TestCase):

    checked_files = []
    counter = 0

    @classmethod
    def setUpClass(cls):

        # read data from spread sheet
        cls.cell_names, cls.conns = SpreadsheetDataReader.readDataFromSpreadsheet("../../../../")
        print (str(len(cls.cell_names))+' unique cell names in CElegensNeuronTables')

        # generate all nml files once
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

                    generate(fn, params, cells=cells_to_plot, cells_to_stimulate=cells_to_stimulate,            duration=500, validate=False, test=True)

                    cls.checked_files.append(fn)
                    cls.counter += 1

        print "Total files generated %i"%cls.counter

    def test_c302_connections(self):

        # test each connection pair from the excel file

        # early_stop = self.specify_early_stop         # early stopping
        counter = 0
        for index in self.conns:

            # if early_stop == 0:  # early stopping
            #     break  # early stopping

            origin = index.pre_cell
            target = index.post_cell
            num = index.number
            synclass = index.synclass

            fn = origin+"_"+target
            fnswap = target+"_"+origin
            gap_junction = True

            if '_GJ' in synclass:
                test_id = 'NC_'+origin+'_'+target+'_'+synclass
                test_synapse = 'elec_syn_'+str(num)+'conns'
            elif 'GABA' in synclass:
                from_cell = origin+'[0]'
                to_cell = target+'[0]'
                test_synapse = 'inh_syn_'+str(num)+'conns'
                gap_junction = False
            else:
                from_cell = origin+'[0]'
                to_cell = target+'[0]'
                test_synapse = 'exc_syn_'+str(num)+'conns'
                gap_junction = False

            if fn in self.checked_files:
                nml_file = fn+'.nml'
            elif fnswap in self.checked_files:
                nml_file = fnswap+'.nml'
            else:
                print "File not found"

            doc = loaders.NeuroMLLoader.load(nml_file)

            synaptic_conn_list = doc.networks[0].synaptic_connections
            electrical_proj_list = doc.networks[0].electrical_projections

            # test if any connections exist
            flag = True if synaptic_conn_list or electrical_proj_list else False
            self.assertTrue(flag, 'Connection lists are empty for %s'+nml_file)

            # for Gap Junctions

            if gap_junction and electrical_proj_list:
                electrical_proj_test_list = []

                electrical_proj_test_list = [(connection.id, connection.electrical_connections[0].synapse) for connection in electrical_proj_list]

               # test if this particular connection exists
                test_pair = (test_id, test_synapse)
                self.assertIn(test_pair, electrical_proj_test_list, "connection not found")

            # for Synaptic Connections

            if not(gap_junction) and synaptic_conn_list:
                synaptic_conn_test_list = []

                synaptic_conn_test_list = [(connection.to, connection.from_, connection.synapse) for connection in synaptic_conn_list]

               # test if this particular connection exists
                test_pair = (to_cell, from_cell, test_synapse)
                self.assertIn(test_pair, synaptic_conn_test_list, "connection not found")

            counter += 1

            # early_stop -= 1         # early stopping
        print "Total connections verified %i"%counter

    @classmethod
    def tearDownClass(cls):
        print "Cleaning up .. "
        for name in cls.checked_files:
            bashCommand = "rm "+name+".nml "+"LEMS_"+name+".xml"
            os.system(bashCommand)

if __name__ == '__main__':
    unittest.main()
