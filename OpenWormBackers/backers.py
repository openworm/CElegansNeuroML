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
    
    file = open('AdoptedCells.md','w')
    
    info = ""
    
    info+="Cells which have been adopted in the OpenWorm project\n"
    info+="=====================================================\n\n"
    
    for cell in ads:
        name = ads[cell]
        info+=cell+"\n"
        info+="----------\n\n"
        info+="Adopted name: "+name+"\n\n\n"
        
    print info
    file.write(info)
    file.close()
        
    
    