
bioparameters = []

'''
    Subject to much change & refactoring once PyOpenWorm is stable...
'''
class BioParameter():

    def __init__(self, name, value, source, certainty):
        self.name = name
        self.value = value
        self.source = source
        self.certainty = certainty
        bioparameters.append(self) 
    
    def __str__(self):
        return "BioParameter: %s = %s (SRC: %s, certainty %s)"%(self.name, self.value, self.source, self.certainty)


def bioparameter_info(indent=""):
    info = indent+"Known BioParameters:\n"
    for bp in bioparameters:
        info += indent+indent+"%s\n"%bp
    return info

