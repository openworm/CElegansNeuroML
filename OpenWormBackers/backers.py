'''
    This method reads a generated list of cells vs. names as assigned by OpenWorm backers
    
    This information will eventually be moved to PyOpenWorm
'''
def get_adopted_cell_names(root="./"):
    
    file = open(root+"adopters.txt")
    ads = {}
    for line in file:
        cell = line.split(":")[0].strip()
        name = line.split(":")[1].strip()
        ads[cell] = name
        
    return ads

    
if __name__ == '__main__':
    
    ads = get_adopted_cell_names()
    
    for ad in ads:
        print "%s: %s"% (ad, ads[ad]) 
    
    