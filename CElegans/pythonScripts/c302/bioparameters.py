
'''
    Subject to much change & refactoring once PyOpenWorm is stable...
'''


def split_neuroml_quantity(quantity):

    i=len(quantity)
    while i>0:
        magnitude = quantity[0:i].strip()
        unit = quantity[i:].strip()

        try:
            magnitude = float(magnitude)
            i=0
        except ValueError:
            i -= 1
    return magnitude, unit

class BioParameter():

    def __init__(self, name, value, source, certainty):
        self.name = name
        self.value = value
        self.source = source
        self.certainty = certainty 
    
    def __str__(self):
        return "BioParameter: %s = %s (SRC: %s, certainty %s)"%(self.name, self.value, self.source, self.certainty)
    
    def change_magnitude(self, magnitude):
        
        self.value = '%f %s'%(magnitude, split_neuroml_quantity(self.value)[1])
        
    def x(self):
        
        return split_neuroml_quantity(self.value)[0]


class ParameterisedModelPrototype(object):

    #bioparameters = []
    def __init__(self):
        self.bioparameters = []

    def add_bioparameter(self, name, value, source, certainty):
        found = False
        for bp in self.bioparameters:
            if bp.name == name:
                bp.value = value
                bp.source = source
                bp.certainty = certainty
                found = True
        if not found:
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

    def __init__(self):
        super(c302ModelPrototype, self).__init__()

        self.level = "Level not yet set"
        self.custom_component_types_definitions = None
        self.generic_neuron_cell = None
        self.generic_muscle_cell = None
        self.exc_syn = None
        self.inh_syn = None
        self.elec_syn = None
        self.offset_current = None
        self.concentration_model = None
    
    def is_level_A(self):
        return self.level.startswith('A')
    
    def is_level_B(self):
        return self.level.startswith('B')
    
    def is_level_C(self):
        return self.level.startswith('C')
    
    def is_level_C0(self):
        return self.level == 'C0'

    def is_level_C2(self):
        return self.level == 'C2'
    
    def is_level_D(self):
        return self.level.startswith('D')
