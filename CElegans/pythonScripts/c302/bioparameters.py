

'''
    Subject to much change & refactoring once PyOpenWorm is stable...
'''
class BioParameter():

    def __init__(self, name, value, source, certainty):
        self.name = name
        self.value = value
        self.source = source
        self.certainty = certainty 
    
    def __str__(self):
        return "BioParameter: %s = %s (SRC: %s, certainty %s)"%(self.name, self.value, self.source, self.certainty)
    
    def change_magnitude(self, magnitude):
        if not ' ' in self.value:
            # TODO check for case where no space is used in value, e.g. -60mV
            self.value = magnitude
        else:
            self.value = '%f %s'%(magnitude, self.value.split(' ')[1])


class ParameterisedModelPrototype():
    
    bioparameters = []

    def add_bioparameter(self, name, value, source, certainty):
        bp = BioParameter(name, value, source, certainty)
        self.bioparameters.append(bp)

    def get_bioparameter(self, name):
        for bp in self.bioparameters:
            if bp.name == name:
                return bp
        return None

    def set_bioparameter(self, name, value, source, certainty):

        for bp in self.bioparameters:
            if bp.name == name:
                bp.value = value
                bp.source = source
                bp.certainty = certainty

    def bioparameter_info(self, indent=""):
        info = indent+"Known BioParameters:\n"
        for bp in self.bioparameters:
            info += indent+indent+"%s\n"%bp
        return info
    
    
class c302ModelPrototype(ParameterisedModelPrototype):

    level = "Level not yet set"
    generic_cell = None
    exc_syn = None
    inh_syn = None
    elec_syn = None
    offset_current = None