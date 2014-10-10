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
    
    file = open('README.md','w')
    
    info = ""
    
    info+="Cells which have been adopted in the OpenWorm project\n"
    info+="=====================================================\n\n"
    
    url = "https://github.com/openworm/CElegansNeuroML/blob/master/CElegans/pythonScripts/c302/c302_A_Full.nml#L%i"
    
    for cell in sorted(ads.keys()):
        name = ads[cell]
        info+=cell+"\n"
        info+="----------\n\n"
        info+="Adopted name: **"+name+"**\n\n\n"
        i = 0
        search_file = open("../CElegans/pythonScripts/c302/c302_A_Full.nml",'r')
        for line in search_file:
            i+=1
            if 'tag="OpenWormBackerAssignedName" value="%s"'%name in line:
                info+="Added to c302 network files [here](%s).\n\n"%(url%i)
        
    print info
    file.write(info)
    file.close()
        
    
    