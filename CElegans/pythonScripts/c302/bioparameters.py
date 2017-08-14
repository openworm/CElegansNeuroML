
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
    
    bioparameters = []

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

    level = "Level not yet set"
    custom_component_types_definitions = None
    generic_neuron_cell = None
    generic_muscle_cell = None
    exc_syn = None
    inh_syn = None
    elec_syn = None
    offset_current = None
    concentration_model = None
    
    def is_level_A(self):
        return self.level.startswith('A')
    
    def is_level_B(self):
        return self.level.startswith('B')
    
    def is_level_C(self):
        return self.level.startswith('C')
    
    def is_level_C0(self):
        return self.level == 'C0'
    
    def is_level_D(self):
        return self.level.startswith('D')


    def get_conn_param(self, pre_cell, post_cell, specific_conn_template, default_conn_template, param_name):
        param = self.get_bioparameter(specific_conn_template % (pre_cell, post_cell, param_name))
        if param:
            return param.value, True
        def_param = self.get_bioparameter(default_conn_template % param_name)
        if not def_param:
            return None, False
        return def_param.value, False


    def get_syn(self, pre_cell, post_cell, type, pol):
        if pol == 'elec':
            return self.get_elec_syn(pre_cell, post_cell, type)
        elif pol == 'exc':
            return self.get_exc_syn(pre_cell, post_cell, type)
        elif pol == 'inh':
            return self.get_inh_syn(pre_cell, post_cell, type)

