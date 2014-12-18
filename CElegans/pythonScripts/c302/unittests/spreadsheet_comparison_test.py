# -*- coding: utf-8 -*-

############################################################################

#  Test to compare values in CElegansNeuronTables.xls with a formatted version
#  of NeuronConnect.xls. Errors written to log file comparison_error_log.xls

############################################################################

import unittest

from xlrd import open_workbook
import xlwt


class DataIntegrityTest(unittest.TestCase):

    def setUp(self):

        # change path if not in /c302/unittest folder
        dir = "../../../../"

        # reading the NeuronConnect.xls file
        comparison_filename = dir + "NeuronConnectFormatted.xlsx"
        self.rb1 = open_workbook(comparison_filename)
        print("Opened Excel file: " + comparison_filename)

        # reading the CElegansNeuronTables.xls file
        data_filename = dir + "CElegansNeuronTables.xls"
        self.rb2 = open_workbook(data_filename)
        print("Opened Excel file: " + data_filename)

        # initiate error log file
        self.book = xlwt.Workbook()
        self.sh = self.book.add_sheet('Error Log')
        col1_name = 'Origin'
        col2_name = 'Target'
        col3_name = 'Issue'
        col4_name = 'No. of Connections Found'
        col5_name = 'No. of Connections Expected'
        self.sh.write(0, 0, col1_name)
        self.sh.write(0, 1, col2_name)
        self.sh.write(0, 2, col3_name)
        self.sh.write(0, 3, col4_name)
        self.sh.write(0, 4, col5_name)
        self.logcounter = 1

    def test_comparison(self):
        cells_not_found = []
        for row in range(1, self.rb2.sheet_by_index(0).nrows):
            c_pre = str(self.rb2.sheet_by_index(0).cell(row, 0).value)
            c_post = str(self.rb2.sheet_by_index(0).cell(row, 1).value)
            c_syntype = self.rb2.sheet_by_index(0).cell(row, 2).value
            c_num = int(self.rb2.sheet_by_index(0).cell(row, 3).value)

            found_flag = False
            pre_test = ''
            post_test = ''
            num_test = 0

            for row_counter in range(1, self.rb1.sheet_by_index(0).nrows):
                pre = str(self.rb1.sheet_by_index(0).cell(row_counter, 0).value)
                post = str(self.rb1.sheet_by_index(0).cell(row_counter, 1).value)
                syntype = self.rb1.sheet_by_index(0).cell(row_counter, 2).value
                num = int(self.rb1.sheet_by_index(0).cell(row_counter, 3).value)

                if c_syntype == 'GapJunction':
                    if pre == c_pre and post == c_post and syntype == 'EJ':
                        num_test = num
                        pre_test = pre
                        post_test = post
                        found_flag = True
                        break
                else:
                    if pre == c_pre and post == c_post and syntype in ['S', 'Sp']:
                        found_flag = True
                        pre_test = pre
                        post_test = post
                        num_test = num_test + num

            if found_flag:
                try:
                    self.assertEqual(c_num, num_test)

                except:
                    self.sh.write(self.logcounter, 0, c_pre)
                    self.sh.write(self.logcounter, 1, c_post)
                    self.sh.write(self.logcounter, 2, 'Connection Number Mismatch')
                    self.sh.write(self.logcounter, 3, c_num)
                    self.sh.write(self.logcounter, 4, num_test)
                    self.logcounter += 1

            else:
                self.sh.write(self.logcounter, 0, c_pre)
                self.sh.write(self.logcounter, 1, c_post)
                self.sh.write(self.logcounter, 2, 'Pair Not Found')
                self.logcounter += 1
                if c_pre not in cells_not_found:
                    cells_not_found.append(c_pre)
                if c_post not in cells_not_found:
                    cells_not_found.append(c_post)

        print "Total Connections tested: " + str(row)

        # write errors to a log file
        if self.logcounter > 1:
            cells = ', '.join(cells_not_found)
            print "Total Errors Found %i"%(self.logcounter-1)
            self.sh.write(1, 6, str(len(cells_not_found)) + ' cells not found')
            self.sh.write(2, 6, cells)
            self.book.save('comparison_error_log.xls')
            print "Errors written to comparison_error_log.xls"

if __name__ == '__main__':
    unittest.main()
