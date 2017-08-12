import subprocess as sp

def get_file_list():
    #Add the name of the python scripts to the list that needs to be tested
    file_list = ['RegenerateConnectome.py', 'c302/SpreadsheetDataReader.py', 'c302/OpenWormReader.py']
    return file_list


def test_python_scripts(file_list = get_file_list()):
    '''
    Executes the desired python scripts and check whether they exit correctly(code 0) or not.
    :param file_list: contains files that are to be tested
    :return: none
    '''

    #stores returncode of each file.
    returncode_list = []

    for each_script in file_list:
        exit_code = sp.call("python "+each_script, shell=True)
        returncode_list.append(exit_code)

    for i in range(len(file_list)):
        assert(returncode_list[i] == 0),"Test Failed for " + file_list[i]
        print(("Test passed for " + file_list[i]))

