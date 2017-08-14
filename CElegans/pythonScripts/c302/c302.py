#! /usr/bin/env python

from neuroml import NeuroMLDocument
from neuroml import Network
from neuroml import Population
from neuroml import Instance
from neuroml import IncludeType
from neuroml import Location
from neuroml import Input
from neuroml import InputList
from neuroml import Projection
from neuroml import Connection
from neuroml import ConnectionWD
from neuroml import ElectricalProjection
from neuroml import ElectricalConnectionInstanceW
from neuroml import ContinuousProjection
from neuroml import ContinuousConnectionInstanceW
from neuroml import ExpTwoSynapse
from neuroml import GapJunction
from neuroml import GradedSynapse
from neuroml import Property
from neuroml import PulseGenerator
from neuroml import SineGenerator
from neuroml import SilentSynapse

import neuroml.writers as writers
import neuroml.loaders as loaders

import bioparameters

import airspeed

import random
import argparse
import shutil
import os
import importlib
import math
import re

from parameters_C0 import GradedSynapse2

try:
    from urllib2 import URLError  # Python 2
except:
    from urllib import URLError  # Python 3

import sys
sys.path.append("..")
#import SpreadsheetDataReader

LEMS_TEMPLATE_FILE = "LEMS_c302_TEMPLATE.xml"

def load_data_reader(data_reader="SpreadsheetDataReader"):
    """
    Imports and returns data reader module
    Args:
        data_reader (str): The name of the data reader
    Returns:
        reader (obj): The data reader object
    """
    reader = importlib.import_module(data_reader)
    return reader

def get_str_from_expnotation(num):
    """
    Returns a formatted string representing a floating point number, e.g. 1*0.00001 would result into 1e-05. Returning 0.00001.
    Args:
        num (float): A number. Can be of type int or float,  float can have exponential notation.
    Returns:
       (str): A string representing a float with 15 fractional digits.
    """
    return '{0:.15f}'.format(num)

def get_muscle_position(muscle, data_reader="SpreadsheetDataReader"):
    """if data_reader == "UpdatedSpreadsheetDataReader":
        x = 80 * (-1 if muscle[0] == 'v' else 1)
        z = 80 * (-1 if muscle[4] == 'L' else 1)
        y = -300 + 30 * int(muscle[5:7])
        return x, y, z"""
    
    x = 80 * (-1 if muscle[1] == 'V' else 1)
    z = 80 * (-1 if muscle[2] == 'L' else 1)
    y = -300 + 30 * int(muscle[3:5])
    return x, y, z

def is_muscle(cell_name):
    return cell_name.startswith('MDL') or \
           cell_name.startswith('MDR') or  \
           cell_name.startswith('MVL') or  \
           cell_name.startswith('MVR')

def process_args():
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description="A script which can generate NeuroML2 compliant networks based on the C elegans connectome, along with LEMS files to run them")

    parser.add_argument('reference', type=str, metavar='<reference>',
                        help='Unique reference for new network')

    parser.add_argument('parameters', type=str, metavar='<parameters>',
                        help='Set of biophysical parametes to use, e.g. parameters_A')

    parser.add_argument('-datareader',
                        type=str,
                        metavar='<data-reader>',
                        default="SpreadsheetDataReader",
                        help='Use a specific data reader. Possible values are: "SpreadsheetDataReader". (default: SpreadsheetDataReader)')

    parser.add_argument('-cells',
                        type=str,
                        metavar='<cells>',
                        default=None,
                        help='List of cells to include in network (default: all)')

    parser.add_argument('-cellstoplot',
                        type=str,
                        metavar='<cells-to-plot>',
                        default=None,
                        help='List of cells to plot (default: all)')

    parser.add_argument('-cellstostimulate',
                        type=str,
                        metavar='<cells-to-stimulate>',
                        default=None,
                        help='List of cells to stimulate (default: all)')

    parser.add_argument('-connpolarityoverride',
                        type=str,
                        metavar='<conn-polarity-override>',
                        default=None,
                        help='Map of connection polarities to override, e.g. {"AVAL-AVBR":"inh", ...} => use inhibitory connection for AVAL-AVBR')

    parser.add_argument('-connnumberoverride',
                        type=str,
                        metavar='<conn-number-override>',
                        default=None,
                        help='Map of connection numbers to override, e.g. {"I1L-I3":2.5, "AVAR-AVBL_GJ":2} => use 2.5 connections from I1L to I3, use 2 connections for GJ AVAR-AVBL')

    parser.add_argument('-connnumberscaling',
                        type=str,
                        metavar='<conn-number-scaling>',
                        default=None,
                        help='Map of scaling factors for connection numbers, e.g. {"I1L-I3":2, "AVAR-AVBL_GJ":2} => use 2 times as many connections from I1L to I3, use 2 times as many connections for GJ AVAR-AVBL')

    parser.add_argument('-musclestoinclude',
                        type=str,
                        metavar='<muscles-to-include>',
                        default=None,
                        help='List of muscles to include (default: none)')

    parser.add_argument('-duration',
                        type=float,
                        metavar='<duration>',
                        default=100,
                        help='Duration of simulation in ms')

    parser.add_argument('-dt',
                        type=float,
                        metavar='<time step>',
                        default=0.01,
                        help='Timestep for simulations (dt) in ms')

    parser.add_argument('-vmin',
                        type=float,
                        metavar='<vmin>',
                        default=-80,
                        help='Minimum voltage for plot in mV')

    parser.add_argument('-vmax',
                        type=float,
                        metavar='<vmax>',
                        default=-40,
                        help='Maximum voltage for plot in mV')

    return parser.parse_args()

"""
def get_specific_elec_syn_params(params, pre_cell, post_cell, syn_type, polarity):
    prefix = "%s_to_%s_%s_syn" % (pre_cell, post_cell, polarity)
    # delayed_gj_prefix = "%s_to_%s_delayed_%s_syn" % (pre_cell, post_cell, polarity)
    weight = params.get_bioparameter("%s_weight" % prefix)
    conductance = params.get_bioparameter("%s_gbase" % prefix)
    # delay = self.get_bioparameter("%s_delay" % prefix)
    sigma = params.get_bioparameter("%s_sigma" % prefix)
    mu = params.get_bioparameter("%s_mu" % prefix)
    overridden = False
    if weight or conductance or sigma or mu:
        overridden = True
    def_prefix = "%s_%s_syn" % (syn_type, polarity)
    if not weight:
        weight = params.get_bioparameter("%s_weight" % def_prefix)
    if not conductance:
        conductance = params.get_bioparameter("%s_gbase" % def_prefix)
    if overridden:
        syn_id = prefix
    else:
        syn_id = def_prefix
    return syn_id, weight, conductance, sigma, mu


def get_specific_chem_syn_params(params, pre_cell, post_cell, syn_type, polarity):
    prefix = "%s_to_%s_%s_syn" % (pre_cell, post_cell, polarity)
    weight = params.get_bioparameter("%s_weight" % prefix)
    conductance = params.get_bioparameter("%s_conductance" % prefix)
    delta = params.get_bioparameter("%s_delta" % prefix)
    vth = params.get_bioparameter("%s_vth" % prefix)
    erev = params.get_bioparameter("%s_erev" % prefix)
    k = params.get_bioparameter("%s_k" % prefix)
    sigma = params.get_bioparameter("%s_sigma" % prefix)
    mu = params.get_bioparameter("%s_mu" % prefix)

    # Load default parameters unless there are more specific parameters for the current synapse
    def_prefix = "%s_%s_syn" % (syn_type, polarity)
    overridden = False
    if weight or conductance or delta or vth or erev or k or sigma or mu:
        overridden = True
    if not weight:
        weight = params.get_bioparameter("%s_weight" % def_prefix)
    if not conductance:
        conductance = params.get_bioparameter("%s_conductance" % def_prefix)
    if not delta:
        delta = params.get_bioparameter("%s_delta" % def_prefix)
    if not vth:
        vth = params.get_bioparameter("%s_vth" % def_prefix)
    if not erev:
        erev = params.get_bioparameter("%s_erev" % def_prefix)
    if not k:
        k = params.get_bioparameter("%s_k" % def_prefix)

    if overridden:
        syn_id = prefix
    else:
        syn_id = def_prefix

    return syn_id, weight, conductance, delta, vth, erev, k, sigma, mu
"""

def get_syn(params, pre_cell, post_cell, syn_type, polarity):
    return params.get_syn(pre_cell, post_cell, syn_type, polarity)
    """if polarity == "elec":
        syn_id, weight, conductance, sigma, mu = get_specific_elec_syn_params(params, pre_cell, post_cell, syn_type, polarity)
        if sigma or mu:
            return DelayedGapJunction(id=syn_id,
                                      weight=weight.value,
                                      conductance=conductance.value,
                                      sigma=sigma.value,
                                      mu=mu.value)
        return GapJunction(id=syn_id,
                           conductance=conductance.value)

    syn_id, weight, conductance, delta, vth, erev, k, sigma, mu = get_specific_chem_syn_params(params, pre_cell, post_cell, syn_type, polarity)
    if sigma or mu:
        return DelayedGradedSynapse(id=syn_id,
                                    weight=weight.value,
                                    conductance=conductance.value,
                                    delta=delta.value,
                                    Vth=vth.value,
                                    erev=erev.value,
                                    k=k.value,
                                    sigma=sigma.value,
                                    mu=mu.value)
    return GradedSynapse(id=syn_id,
                         conductance=conductance.value,
                         delta=delta.value,
                         Vth=vth.value,
                         erev=erev.value,
                         k=k.value)"""


quadrant0 = 'MDR'
quadrant1 = 'MVR'
quadrant2 = 'MVL'
quadrant3 = 'MDL'


def get_next_stim_id(nml_doc, cell):
    i = 1
    for stim in nml_doc.pulse_generators:
        if stim.id.startswith("%s_%s" % ("stim", cell)):
            i += 1
    id = "%s_%s_%s" % ("stim", cell, i)
    return id

def get_cell_position(cell):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    #cell_file_path = root_dir + "/../../../" if test else root_dir + "/../../"  # if running test
    cell_file_path = root_dir + "/../../" 
    cell_file = cell_file_path + 'generatedNeuroML2/%s.cell.nml' % cell
    doc = loaders.NeuroMLLoader.load(cell_file)
    location = doc.cells[0].morphology.segments[0].proximal
    #print "%s, %s, %s" %(location.x, location.y, location.z)
    return location

def append_input_to_nml_input_list(stim, nml_doc, cell, params):
    target = get_cell_id_string(cell, params, muscle=is_muscle(cell))

    input_list = InputList(id="Input_%s_%s" % (cell, stim.id), component=stim.id, populations='%s' % cell)

    input_list.input.append(Input(id=0, target=target, destination="synapses"))

    nml_doc.networks[0].input_lists.append(input_list)


def add_new_sinusoidal_input(nml_doc, cell, delay, duration, amplitude, period, params):
    id = get_next_stim_id(nml_doc, cell)
    
    phase = get_cell_position(cell).x
    print "### CELL %s PHASE: %s" % (cell, phase)
    
    input = SineGenerator(id=id, delay=delay, phase=phase, duration=duration, amplitude=amplitude, period=period)
    nml_doc.sine_generators.append(input)

    append_input_to_nml_input_list(input, nml_doc, cell, params)
    
    

def add_new_input(nml_doc, cell, delay, duration, amplitude, params):
    id = get_next_stim_id(nml_doc, cell)
    input = PulseGenerator(id=id, delay=delay, duration=duration, amplitude=amplitude)
    nml_doc.pulse_generators.append(input)

    append_input_to_nml_input_list(input, nml_doc, cell, params)


def get_muscle_names():
    names = []
    for i in range(24):
        names.append("%s%s"%(quadrant0, i+1 if i>8 else ("0%i"%(i+1))))
    for i in range(23):
        names.append("%s%s"%(quadrant1, i+1 if i>8 else ("0%i"%(i+1))))
    for i in range(24):
        names.append("%s%s"%(quadrant2, i+1 if i>8 else ("0%i"%(i+1))))
    for i in range(24):
        names.append("%s%s"%(quadrant3, i+1 if i>8 else ("0%i"%(i+1))))

    return names


def merge_with_template(model, templfile):
    with open(templfile) as f:
        templ = airspeed.Template(f.read())
    return templ.merge(model)


def print_(msg):
    pre = "c302      >>> "
    print('%s %s'%(pre,msg.replace('\n','\n'+pre)))


def write_to_file(nml_doc, 
                  lems_info, 
                  reference, 
                  template_path='', 
                  validate=True, 
                  verbose=True,
                  target_directory='.'):

    #######   Write to file  ######

    nml_file = target_directory+'/'+reference+'.nml'
    print_("Writing generated network to: %s"%os.path.realpath(nml_file))
    writers.NeuroMLWriter.write(nml_doc, nml_file)

    if verbose: 
        print_("Written network file to: "+nml_file)

    lems_file_name = target_directory+'/'+'LEMS_%s.xml'%reference
    with open(lems_file_name, 'w') as lems:
        # if running unittest concat template_path
    	merged = merge_with_template(lems_info, template_path+LEMS_TEMPLATE_FILE)
        lems.write(merged)

    if verbose: 
        print_("Written LEMS file to: "+lems_file_name)

    if validate:

        ###### Validate the NeuroML ######

        from neuroml.utils import validate_neuroml2
        try:
            validate_neuroml2(nml_file)
        except URLError:
            print_("Problem validating against remote Schema!")


# Get the standard name for a network connection
def get_projection_id(pre, post, synclass, syntype):

    proj_id = "NC_%s_%s_%s"%(pre, post, synclass)
    '''
    if "GapJunction" in syntype:
       proj_id += '_GJ' '''

    return proj_id


def get_random_colour_hex():
    rgb = [ hex(random.randint(0,256)), hex(random.randint(0,256)), hex(random.randint(0,256)) ]
    col = "#"
    for c in rgb: col+= ( c[2:4] if len(c)==4 else "00")
    return col


def create_n_connection_synapse(prototype_syn, n, nml_doc, existing_synapses):

    #print_("Creating synapse from %s with %i connections"%(prototype_syn.id, n))
    new_id = "%s"%(prototype_syn.id)
    #if type(n) is float:
    #    new_id = "%s_%sconns" % (prototype_syn.id, get_str_from_expnotation(n).replace('.', '_'))
    
    if isinstance(prototype_syn, ExpTwoSynapse):
        new_id = "%s"%(prototype_syn.id)

    if not existing_synapses.has_key(new_id):

        if isinstance(prototype_syn, ExpTwoSynapse):
            
            new_syn = ExpTwoSynapse(id=new_id,
                                gbase =       prototype_syn.gbase,
                                erev =        prototype_syn.erev,
                                tau_decay =   prototype_syn.tau_decay,
                                tau_rise =    prototype_syn.tau_rise)

            existing_synapses[new_id] = new_syn
            nml_doc.exp_two_synapses.append(new_syn)

        elif isinstance(prototype_syn, GapJunction):
            magnitude, unit = bioparameters.split_neuroml_quantity(prototype_syn.conductance)
            cond = "%s%s" % (magnitude, unit)
            #if type(n) is float:
            #    cond = "%s%s" % (get_str_from_expnotation(magnitude * n), unit)
            new_syn = GapJunction(id=new_id,
                                  conductance =       cond)

            existing_synapses[new_id] = new_syn
            nml_doc.gap_junctions.append(new_syn)

        elif isinstance(prototype_syn, DelayedGapJunction):
            magnitude, unit = bioparameters.split_neuroml_quantity(prototype_syn.conductance)
            cond = "%s%s" % (magnitude, unit)
            #if type(n) is float:
            #    cond = "%s%s" % (get_str_from_expnotation(magnitude * n), unit)
            new_syn = DelayedGapJunction(id=new_id,
                                         weight=prototype_syn.weight,
                                         conductance=cond,
                                         sigma=prototype_syn.sigma,
                                         mu=prototype_syn.mu)

            existing_synapses[new_id] = new_syn
            nml_doc.gap_junctions.append(new_syn)

        elif isinstance(prototype_syn, GradedSynapse):
            magnitude, unit = bioparameters.split_neuroml_quantity(prototype_syn.conductance)
            cond = "%s%s" % (magnitude, unit)
            #if type(n) is float:
            #    cond = "%s%s" % (get_str_from_expnotation(magnitude * n), unit)
            new_syn = GradedSynapse(id=new_id,
                                    conductance =       cond,
                                    delta =             prototype_syn.delta,
                                    Vth =               prototype_syn.Vth,
                                    erev =              prototype_syn.erev,
                                    k =                 prototype_syn.k)

            existing_synapses[new_id] = new_syn
            nml_doc.graded_synapses.append(new_syn)

        elif isinstance(prototype_syn, DelayedGradedSynapse):
            magnitude, unit = bioparameters.split_neuroml_quantity(prototype_syn.conductance)
            cond = "%s%s" % (magnitude, unit)
            #if type(n) is float:
            #    cond = "%s%s" % (get_str_from_expnotation(magnitude * n), unit)
            new_syn = DelayedGradedSynapse(id=new_id,
                                           weight=prototype_syn.weight,
                                           conductance=cond,
                                           delta=prototype_syn.delta,
                                           vth=prototype_syn.vth,
                                           erev=prototype_syn.erev,
                                           k=prototype_syn.k,
                                           sigma=prototype_syn.sigma,
                                           mu=prototype_syn.mu)

            existing_synapses[new_id] = new_syn
            nml_doc.graded_synapses.append(new_syn)

        elif isinstance(prototype_syn, GradedSynapse2):
            magnitude, unit = bioparameters.split_neuroml_quantity(prototype_syn.conductance)
            cond = "%s%s" % (magnitude, unit)
            #if type(n) is float:
            #    cond = "%s%s" % (get_str_from_expnotation(magnitude * n), unit)
            new_syn = GradedSynapse2(id=new_id,
                                    conductance =       cond,
                                    ar =                prototype_syn.ar,
                                    ad =                prototype_syn.ad,
                                    beta =              prototype_syn.beta,
                                    vth =               prototype_syn.vth,
                                    erev =              prototype_syn.erev)

            existing_synapses[new_id] = new_syn
            nml_doc.graded_synapses.append(new_syn)

    else:
        new_syn = existing_synapses[new_id]

    return new_syn


def get_file_name_relative_to_c302(file_name):
    
    if os.environ.has_key('C302_HOME'):
        return os.path.relpath(os.environ['C302_HOME'],file_name)
    
    
def get_cell_names_and_connection(data_reader="SpreadsheetDataReader", test=False):
    
    # Use the spreadsheet reader to give a list of all cells and a list of all connections
    # This could be replaced with a call to "DatabaseReader" or "OpenWormNeuroLexReader" in future...
    # If called from unittest folder ammend path to "../../../../"
    
    spreadsheet_location = os.path.dirname(os.path.abspath(__file__))+"/../../../"

    cell_names, conns = load_data_reader(data_reader).readDataFromSpreadsheet(include_nonconnected_cells=True)

    cell_names.sort()
    
    return cell_names, conns


def get_cell_muscle_names_and_connection(data_reader="SpreadsheetDataReader", test=False):
    
    #spreadsheet_location = os.path.dirname(os.path.abspath(__file__))+"/../../../"

    mneurons, all_muscles, muscle_conns = load_data_reader(data_reader).readMuscleDataFromSpreadsheet()

    all_muscles = get_muscle_names()
        
    return mneurons, all_muscles, muscle_conns


def is_cond_based_cell(params):
    return params.is_level_C() or params.is_level_D()


def get_cell_id_string(cell, params, muscle=False):
    if cell in get_muscle_names():
        muscle = True
    if not params.is_level_D():
        if not muscle:
            return "../%s/0/%s"%(cell, params.generic_neuron_cell.id)
        else:
            return "../%s/0/%s"%(cell, params.generic_muscle_cell.id)
    
    else:
        if not muscle:
            return "../%s/0/%s"%(cell, cell)
        else:
            return "../%s/0/%s"%(cell, params.generic_muscle_cell.id)
    
    
def generate(net_id,
             params,
             data_reader = "SpreadsheetDataReader",
             cells = None,
             cells_to_plot = None,
             cells_to_stimulate = None,
             muscles_to_include=[],
             conns_to_include=[],
             conns_to_exclude=[],
             conn_number_override = None,
             conn_number_scaling = None,
             conn_polarity_override = None,
             duration = 500,
             dt = 0.01,
             vmin = None,
             vmax = None,
             seed = 1234,
             test=False,
             verbose=True,
             param_overrides={},
             target_directory='./'):
                 
    validate = not (params.is_level_B() or params.is_level_C0())
                
    root_dir = os.path.dirname(os.path.abspath(__file__))
    for k in param_overrides.keys():
        v = param_overrides[k]
        if params.get_bioparameter(k):
            print_("Setting parameter %s = %s"%(k,v))
            params.set_bioparameter(k, v, "Set with param_overrides", 0)
        else:
            print_("Adding parameter %s = %s" % (k, v))
            params.add_bioparameter(k, v, "Add with param_overrides", 0)
    

    params.create_models()
    
    if vmin==None:
        if params.is_level_A():
            vmin=-72
        elif params.is_level_B():
            vmin=-52 
        elif params.is_level_C():
            vmin=-60
        elif params.is_level_D():
            vmin=-60
        else:
            vmin=-52 
            
    
    if vmax==None:
        if params.is_level_A():
            vmax=-48
        elif params.is_level_B():
            vmax=-28
        elif params.is_level_C():
            vmax=25
        elif params.is_level_D():
            vmax=25
        else:
            vmax=-28
    
    random.seed(seed)

    info = "\n\nParameters and setting used to generate this network:\n\n"+\
           "    Data reader:                    %s\n" % data_reader+\
           "    Cells:                          %s\n" % (cells if cells is not None else "All cells")+\
           "    Cell stimulated:                %s\n" % (cells_to_stimulate if cells_to_stimulate is not None else "All neurons")+\
           "    Connection:                     %s\n" % (conns_to_include if conns_to_include is not None else "All connections") + \
           "    Connection numbers overridden:  %s\n" % (conn_number_override if conn_number_override is not None else "None")+\
           "    Connection numbers scaled:      %s\n" % (conn_number_scaling if conn_number_scaling is not None else "None")+ \
           "    Connection polarities override: %s\n" % conn_polarity_override + \
           "    Muscles:                        %s\n" % (muscles_to_include if muscles_to_include is not None else "All muscles")
    if verbose: print_(info)
    info += "\n%s\n"%(params.bioparameter_info("    "))

    nml_doc = NeuroMLDocument(id=net_id, notes=info)

    if params.is_level_A() or params.is_level_B() or params.level == "BC1":
        nml_doc.iaf_cells.append(params.generic_muscle_cell) 
        nml_doc.iaf_cells.append(params.generic_neuron_cell) 
    elif params.is_level_C():
        nml_doc.cells.append(params.generic_muscle_cell)
        nml_doc.cells.append(params.generic_neuron_cell)
    elif params.is_level_D():
        nml_doc.cells.append(params.generic_muscle_cell)
         

    net = Network(id=net_id)


    nml_doc.networks.append(net)

    nml_doc.pulse_generators.append(params.offset_current)

    if is_cond_based_cell(params):
        nml_doc.fixed_factor_concentration_models.append(params.concentration_model)

    cell_names, conns = get_cell_names_and_connection(data_reader)

    # To hold all Cell NeuroML objects vs. names
    all_cells = {}

    # lems_file = ""
    lems_info = {"comment":    info,
                 "reference":  net_id,
                 "duration":   duration,
                 "dt":         dt,
                 "vmin":       vmin,
                 "vmax":       vmax}

    lems_info["plots"] = []
    lems_info["activity_plots"] = []
    lems_info["muscle_plots"] = []
    lems_info["muscle_activity_plots"] = []

    lems_info["to_save"] = []
    lems_info["activity_to_save"] = []
    lems_info["muscles_to_save"] = []
    lems_info["muscles_activity_to_save"] = []
    lems_info["cells"] = []
    lems_info["muscles"] = []
    lems_info["includes"] = []

    if params.custom_component_types_definitions:
        if isinstance(params.custom_component_types_definitions, str):
            params.custom_component_types_definitions = [params.custom_component_types_definitions]
        for ctd in params.custom_component_types_definitions:
            lems_info["includes"].append(ctd)
            if target_directory != './':
                #def_file = './%s' % ctd
                def_file = "%s/%s"%(os.path.dirname(os.path.abspath(__file__)), ctd)
                shutil.copy(def_file, target_directory)
            nml_doc.includes.append(IncludeType(href=ctd))
    
    
    backers_dir = root_dir+"/../../../../OpenWormBackers/" if test else root_dir+"/../../../OpenWormBackers/"
    sys.path.append(backers_dir)
    import backers
    cells_vs_name = backers.get_adopted_cell_names(backers_dir)


    count = 0
    for cell in cell_names:

        if cells is None or cell in cells:

            inst = Instance(id="0")

            if not params.is_level_D():
                # build a Population data structure out of the cell name
                pop0 = Population(id=cell,
                                  component=params.generic_neuron_cell.id,
                                  type="populationList")
                cell_id = params.generic_neuron_cell.id
            else:
                # build a Population data structure out of the cell name
                pop0 = Population(id=cell,
                                  component=cell,
                                  type="populationList")
                cell_id = cell
                                  
            pop0.instances.append(inst)



            # put that Population into the Network data structure from above
            net.populations.append(pop0)
            
            if cells_vs_name.has_key(cell):
                p = Property(tag="OpenWormBackerAssignedName", value=cells_vs_name[cell])
                pop0.properties.append(p)

            # also use the cell name to grab the morphology file, as a NeuroML data structure
            #  into the 'all_cells' dict
            cell_file_path = root_dir+"/../../../" if test else root_dir+"/../../" #if running test
            cell_file = cell_file_path+'generatedNeuroML2/%s.cell.nml'%cell
            doc = loaders.NeuroMLLoader.load(cell_file)
            all_cells[cell] = doc.cells[0]
            
            
            if params.is_level_D():
                new_cell = params.create_neuron_cell(cell, doc.cells[0].morphology)
                
                nml_cell_doc = NeuroMLDocument(id=cell)
                nml_cell_doc.cells.append(new_cell)
                new_cell_file = 'cells/'+cell+'_D.cell.nml'
                nml_file = target_directory+'/'+new_cell_file
                print_("Writing new cell to: %s"%os.path.realpath(nml_file))
                writers.NeuroMLWriter.write(nml_cell_doc, nml_file)
                
                nml_doc.includes.append(IncludeType(href=new_cell_file))
                lems_info["includes"].append(new_cell_file)
                
                inst.location = Location(0,0,0)
            else:
                location = doc.cells[0].morphology.segments[0].proximal
            
                inst.location = Location(float(location.x), float(location.y), float(location.z))
            
            if verbose: 
                print_("Loaded morphology: %s; id: %s; placing at location: (%s, %s, %s)"%(os.path.realpath(cell_file), all_cells[cell].id, inst.location.x, inst.location.y, inst.location.z))


                
            if cells_to_stimulate is None or cell in cells_to_stimulate:

                target = "../%s/0/%s"%(pop0.id, cell_id)
                if params.is_level_D():
                    target+="/0"
                
                input_list = InputList(id="Input_%s_%s"%(cell,params.offset_current.id),
                                     component=params.offset_current.id,
                                     populations='%s'%cell)

                input_list.input.append(Input(id=0, 
                              target=target, 
                              destination="synapses"))

                net.input_lists.append(input_list)


            if cells_to_plot is None or cell in cells_to_plot:
                plot = {}

                plot["cell"] = cell
                plot["colour"] = get_random_colour_hex()
                plot["quantity"] = "%s/0/%s/v" % (cell, cell_id)
                lems_info["plots"].append(plot)

                if params.is_level_B():
                    plot = {}

                    plot["cell"] = cell
                    plot["colour"] = get_random_colour_hex()
                    plot["quantity"] = "%s/0/%s/activity" % (cell, cell_id)
                    lems_info["activity_plots"].append(plot)

                if is_cond_based_cell(params):
                    plot = {}

                    plot["cell"] = cell
                    plot["colour"] = get_random_colour_hex()
                    plot["quantity"] = "%s/0/%s/caConc" % (cell, cell_id)
                    lems_info["activity_plots"].append(plot)

            save = {}
            save["cell"] = cell
            save["quantity"] = "%s/0/%s/v" % (cell, cell_id)
            lems_info["to_save"].append(save)

            if params.is_level_B():
                save = {}
                save["cell"] = cell
                save["quantity"] = "%s/0/%s/activity" % (cell, cell_id)
                lems_info["activity_to_save"].append(save)
            if is_cond_based_cell(params):
                save = {}
                save["cell"] = cell
                save["quantity"] = "%s/0/%s/caConc" % (cell, cell_id)
                lems_info["activity_to_save"].append(save)

            lems_info["cells"].append(cell)

            count+=1

    if verbose: 
        print_("Finished loading %i cells"%count)

    
    mneurons, all_muscles, muscle_conns = get_cell_muscle_names_and_connection(data_reader)

    #if data_reader == "SpreadsheetDataReader":
    #    all_muscles = get_muscle_names()
        
    if muscles_to_include == None or muscles_to_include == True:
        muscles_to_include = all_muscles
    elif muscles_to_include == False:
        muscles_to_include = []
        
    for m in muscles_to_include:
        assert m in all_muscles

    if len(muscles_to_include)>0:

        muscle_count = 0
        for muscle in muscles_to_include:

            inst = Instance(id="0")

            # build a Population data structure out of the cell name
            pop0 = Population(id=muscle,
                              component=params.generic_muscle_cell.id,
                              type="populationList")
            pop0.instances.append(inst)


            # put that Population into the Network data structure from above
            net.populations.append(pop0)

            if cells_vs_name.has_key(muscle):
                # No muscles adopted yet, but just in case they are in future...
                p = Property(tag="OpenWormBackerAssignedName", value=cells_vs_name[muscle])
                pop0.properties.append(p)

            x, y, z = get_muscle_position(muscle, data_reader)
            #print_('Positioning muscle: %s at (%s,%s,%s)'%(muscle,x,y,z))
            inst.location = Location(x,y,z)

            #target = "%s/0/%s"%(pop0.id, params.generic_muscle_cell.id) # unused

            plot = {}

            plot["cell"] = muscle
            plot["colour"] = get_random_colour_hex()
            plot["quantity"] = "%s/0/%s/v" % (muscle, params.generic_muscle_cell.id)
            lems_info["muscle_plots"].append(plot)

            if params.generic_muscle_cell.__class__.__name__ == 'IafActivityCell':
                plot = {}

                plot["cell"] = muscle
                plot["colour"] = get_random_colour_hex()
                plot["quantity"] = "%s/0/%s/activity" % (muscle, params.generic_muscle_cell.id)
                lems_info["muscle_activity_plots"].append(plot)
                
            if params.generic_muscle_cell.__class__.__name__ == 'Cell':
                plot = {}

                plot["cell"] = muscle
                plot["colour"] = get_random_colour_hex()
                plot["quantity"] = "%s/0/%s/caConc" % (muscle, params.generic_muscle_cell.id)
                lems_info["muscle_activity_plots"].append(plot)

            save = {}
            save["cell"] = muscle
            save["quantity"] = "%s/0/%s/v" % (muscle, params.generic_muscle_cell.id)
            lems_info["muscles_to_save"].append(save)

            if params.generic_muscle_cell.__class__.__name__ == 'IafActivityCell':
                save = {}
                save["cell"] = muscle
                save["quantity"] = "%s/0/%s/activity" % (muscle, params.generic_muscle_cell.id)
                lems_info["muscles_activity_to_save"].append(save)
            if params.generic_muscle_cell.__class__.__name__ == 'Cell':
                save = {}
                save["cell"] = muscle
                save["quantity"] = "%s/0/%s/caConc" % (muscle, params.generic_muscle_cell.id)
                lems_info["muscles_activity_to_save"].append(save)

            lems_info["muscles"].append(muscle)

            muscle_count+=1
            
            if muscle in cells_to_stimulate:

                target = "../%s/0/%s"%(pop0.id, params.generic_muscle_cell.id)
                if params.is_level_D():
                    target+="/0"
                
                input_list = InputList(id="Input_%s_%s"%(muscle,params.offset_current.id),
                                     component=params.offset_current.id,
                                     populations='%s'%pop0.id)

                input_list.input.append(Input(id=0, 
                              target=target, 
                              destination="synapses"))

                net.input_lists.append(input_list)

        if verbose: 
            print_("Finished creating %i muscles"%muscle_count)
        
    
    existing_synapses = {}

    for conn in conns:

        if conn.pre_cell in lems_info["cells"] and conn.post_cell in lems_info["cells"]:
            # take information about each connection and package it into a
            # NeuroML Projection data structure
            proj_id = get_projection_id(conn.pre_cell, conn.post_cell, conn.synclass, conn.syntype)
            conn_shorthand = "%s-%s" % (conn.pre_cell, conn.post_cell)

            elect_conn = False
            analog_conn = False

            conn_type = "neuron_to_neuron"
            conn_pol = "exc"

            orig_pol = "exc"
            
            if 'GABA' in conn.synclass:
                conn_pol = "inh"
                orig_pol = "inh"
            if '_GJ' in conn.synclass:
                conn_pol = "elec"
                elect_conn = isinstance(params.neuron_to_neuron_elec_syn, GapJunction) or isinstance(params.neuron_to_neuron_elec_syn, DelayedGapJunction)
                conn_shorthand = "%s-%s_GJ" % (conn.pre_cell, conn.post_cell)

            if conns_to_include and conn_shorthand not in conns_to_include:
                include = False
                for conn_include in conns_to_include:
                    if any(regex_part in conn_include for regex_part in ['*', '\d', '.', '+']):
                        if re.match(conn_include, conn_shorthand):
                            include = True
                            break
                if not include:
                    continue
            if conns_to_exclude and conn_shorthand in conns_to_exclude:
                continue

            syn0 = get_syn(params, conn.pre_cell, conn.post_cell, conn_type, conn_pol)

            if print_connections:
                print conn_shorthand + " " + str(conn.number) + " " + orig_pol + " " + conn.synclass + " " + syn0.id


            polarity = None
            if conn_polarity_override and conn_polarity_override.has_key(conn_shorthand):
                polarity = conn_polarity_override[conn_shorthand]

            if polarity and not elect_conn:
                syn0 = get_syn(params, conn.pre_cell, conn.post_cell, conn_type, polarity)
                if verbose and polarity != orig_pol:
                    print_(">> Changing polarity of connection %s -> %s: was: %s, becomes %s " % \
                       (conn.pre_cell, conn.post_cell, orig_pol, polarity))
                
                
                
            if isinstance(syn0, GradedSynapse) or isinstance(syn0, GradedSynapse2):
                analog_conn = True
                if len(nml_doc.silent_synapses)==0:
                    silent = SilentSynapse(id="silent")
                    nml_doc.silent_synapses.append(silent)

            number_syns = conn.number
            
            
            if params.get_bioparameter('global_connectivity_power_scaling'):
                scale = params.get_bioparameter('global_connectivity_power_scaling').x()
                #print("Scaling by %s"%scale)
                number_syns = math.pow(number_syns,scale)

            if conn_number_override is not None and (conn_number_override.has_key(conn_shorthand)):
                number_syns = conn_number_override[conn_shorthand]
            elif conn_number_scaling is not None and (conn_number_scaling.has_key(conn_shorthand)):
                number_syns = conn.number*conn_number_scaling[conn_shorthand]
            '''
            else:
                print conn_shorthand
                print conn_number_override
                print conn_number_scaling'''
            """if polarity:
                print "%s %s num:%s" % (conn_shorthand, polarity, number_syns)
            elif elect_conn:
                print "%s num:%s" % (conn_shorthand, number_syns)
            else:
                print "%s %s num:%s" % (conn_shorthand, orig_pol, number_syns)"""
            
            if number_syns != conn.number:
                if analog_conn or elect_conn:
                    magnitude, unit = bioparameters.split_neuroml_quantity(syn0.conductance)
                else:
                    magnitude, unit = bioparameters.split_neuroml_quantity(syn0.gbase)
                cond0 = "%s%s"%(magnitude*conn.number, unit)
                cond1 = "%s%s" % (get_str_from_expnotation(magnitude * number_syns), unit)
                gj = "" if not elect_conn else " GapJunction"
                if verbose: 
                    print_(">> Changing number of effective synapses connection %s -> %s%s: was: %s (total cond: %s), becomes %s (total cond: %s)" % \
                     (conn.pre_cell, conn.post_cell, gj, conn.number, cond0, number_syns, cond1))

            #print "######## %s-%s %s %s" % (conn.pre_cell, conn.post_cell, conn.synclass, number_syns)
            #known_motor_prefixes = ["VA"]
            #if conn.pre_cell.startswith(tuple(known_motor_prefixes)) or conn.post_cell.startswith(tuple(known_motor_prefixes)):
            #    print "######### %s-%s %s %s" % (conn.pre_cell, conn.post_cell, number_syns, conn.synclass)

            syn_new = create_n_connection_synapse(syn0, number_syns, nml_doc, existing_synapses)

            if elect_conn:

                proj0 = ElectricalProjection(id=proj_id, \
                                   presynaptic_population=conn.pre_cell,
                                   postsynaptic_population=conn.post_cell)

                net.electrical_projections.append(proj0)

                pre_cell_id=get_cell_id_string(conn.pre_cell, params)
                post_cell_id= get_cell_id_string(conn.post_cell, params)

                #print_("Conn %s -> %s"%(pre_cell_id,post_cell_id))

                # Add a Connection with the closest locations
                conn0 = ElectricalConnectionInstanceW(id="0", \
                           pre_cell=pre_cell_id,
                           post_cell=post_cell_id,
                           synapse=syn_new.id,
                           weight=number_syns)

                proj0.electrical_connection_instance_ws.append(conn0)
                
            elif analog_conn:
        
                proj0 = ContinuousProjection(id=proj_id, \
                                   presynaptic_population=conn.pre_cell,
                                   postsynaptic_population=conn.post_cell)

                net.continuous_projections.append(proj0)

                pre_cell_id= get_cell_id_string(conn.pre_cell, params)
                post_cell_id= get_cell_id_string(conn.post_cell, params)

                conn0 = ContinuousConnectionInstanceW(id="0", \
                           pre_cell=pre_cell_id,
                           post_cell=post_cell_id,
                           pre_component="silent",
                           post_component=syn_new.id,
                           weight=number_syns)

                proj0.continuous_connection_instance_ws.append(conn0)
                
                
            else:

                proj0 = Projection(id=proj_id, \
                                   presynaptic_population=conn.pre_cell,
                                   postsynaptic_population=conn.post_cell,
                                   synapse=syn_new.id)

                net.projections.append(proj0)

                pre_cell_id= get_cell_id_string(conn.pre_cell, params)
                post_cell_id= get_cell_id_string(conn.post_cell, params)

                conn0 = ConnectionWD(id="0", \
                           pre_cell_id=pre_cell_id,
                           post_cell_id=post_cell_id,
                           weight = number_syns,
                           delay = '0ms')

                proj0.connection_wds.append(conn0)



    if len(muscles_to_include)>0:
        for conn in muscle_conns:
            if not conn.post_cell in muscles_to_include:
                continue
            if not conn.pre_cell in lems_info["cells"] and not conn.pre_cell in muscles_to_include:
                continue

            # take information about each connection and package it into a
            # NeuroML Projection data structure
            proj_id = get_projection_id(conn.pre_cell, conn.post_cell, conn.synclass, conn.syntype)
            conn_shorthand = "%s-%s" % (conn.pre_cell, conn.post_cell)

            elect_conn = False
            analog_conn = False

            conn_type = "neuron_to_muscle"
            if conn.pre_cell in muscles_to_include:
                conn_type = "muscle_to_muscle"
            conn_pol = "exc"
            orig_pol = "exc"


            if 'GABA' in conn.synclass:
                conn_pol = "inh"
                orig_pol = "inh"

            if '_GJ' in conn.synclass :
                conn_pol = "elec"
                orig_pol = "elec"
                elect_conn = isinstance(params.neuron_to_neuron_elec_syn, GapJunction) or isinstance(params.neuron_to_neuron_elec_syn, DelayedGapJunction)
                conn_shorthand = "%s-%s_GJ" % (conn.pre_cell, conn.post_cell)

            if conns_to_include and conn_shorthand not in conns_to_include:
                include = False
                for conn_include in conns_to_include:
                    if any(regex_part in conn_include for regex_part in ['*', '\d', '.', '+']):
                        if re.match(conn_include, conn_shorthand):
                            include = True
                            break
                if not include:
                    continue
            if conns_to_exclude and conn_shorthand in conns_to_exclude:
                continue

            syn0 = get_syn(params, conn.pre_cell, conn.post_cell, conn_type, conn_pol)

            if print_connections:
                print conn_shorthand + " " + str(conn.number) + " " + orig_pol + " " + conn.synclass


            polarity = None
            if conn_polarity_override and conn_polarity_override.has_key(conn_shorthand):
                polarity = conn_polarity_override[conn_shorthand]

            if polarity and not elect_conn:
                syn0 = get_syn(params, conn.pre_cell, conn.post_cell, conn_type, polarity)
                if verbose and polarity != orig_pol:
                    print_(">> Changing polarity of connection %s -> %s: was: %s, becomes %s " % \
                           (conn.pre_cell, conn.post_cell, orig_pol, polarity))

            if isinstance(syn0, GradedSynapse) or isinstance(syn0, GradedSynapse2):
                analog_conn = True
                if len(nml_doc.silent_synapses)==0:
                    silent = SilentSynapse(id="silent")
                    nml_doc.silent_synapses.append(silent)

            number_syns = conn.number

            if params.get_bioparameter('global_connectivity_power_scaling'):
                scale = params.get_bioparameter('global_connectivity_power_scaling').x()
                #print("Scaling by %s"%scale)
                number_syns = math.pow(number_syns,scale)
            
            if conn_number_override is not None and (conn_number_override.has_key(conn_shorthand)):
                number_syns = conn_number_override[conn_shorthand]
            elif conn_number_scaling is not None and (conn_number_scaling.has_key(conn_shorthand)):
                number_syns = conn.number*conn_number_scaling[conn_shorthand]
            '''
            else:
                print conn_shorthand
                print conn_number_override
                print conn_number_scaling'''
            """if polarity:
                print "%s %s num:%s" % (conn_shorthand, polarity, number_syns)
            elif elect_conn:
                print "%s num:%s" % (conn_shorthand, number_syns)
            else:
                print "%s %s num:%s" % (conn_shorthand, orig_pol, number_syns)"""

            if number_syns != conn.number:

                if analog_conn or elect_conn:
                    magnitude, unit = bioparameters.split_neuroml_quantity(syn0.conductance)
                else:
                    magnitude, unit = bioparameters.split_neuroml_quantity(syn0.gbase)
                cond0 = "%s%s"%(magnitude*conn.number, unit)
                cond1 = "%s%s" % (get_str_from_expnotation(magnitude * number_syns), unit)
                gj = "" if not elect_conn else " GapJunction"
                if verbose:
                    print_(">> Changing number of effective synapses connection %s -> %s%s: was: %s (total cond: %s), becomes %s (total cond: %s)" % \
                           (conn.pre_cell, conn.post_cell, gj, conn.number, cond0, number_syns, cond1))


            syn_new = create_n_connection_synapse(syn0, number_syns, nml_doc, existing_synapses)

            if elect_conn:

                proj0 = ElectricalProjection(id=proj_id, \
                                             presynaptic_population=conn.pre_cell,
                                             postsynaptic_population=conn.post_cell)

                net.electrical_projections.append(proj0)

                pre_cell_id= get_cell_id_string(conn.pre_cell, params)
                post_cell_id= get_cell_id_string(conn.post_cell, params, muscle=True)

                #print_("Conn %s -> %s"%(pre_cell_id,post_cell_id))

                # Add a Connection with the closest locations
                conn0 = ElectricalConnectionInstanceW(id="0", \
                           pre_cell=pre_cell_id,
                           post_cell=post_cell_id,
                           synapse=syn_new.id,
                           weight=number_syns)

                proj0.electrical_connection_instance_ws.append(conn0)
                
            elif analog_conn:

                proj0 = ContinuousProjection(id=proj_id, \
                                             presynaptic_population=conn.pre_cell,
                                             postsynaptic_population=conn.post_cell)

                net.continuous_projections.append(proj0)

                pre_cell_id= get_cell_id_string(conn.pre_cell, params)
                post_cell_id= get_cell_id_string(conn.post_cell, params, muscle=True)

                conn0 = ContinuousConnectionInstanceW(id="0", \
                           pre_cell=pre_cell_id,
                           post_cell=post_cell_id,
                           pre_component="silent",
                           post_component=syn_new.id,
                           weight=number_syns)

                proj0.continuous_connection_instance_ws.append(conn0)

            else:

                proj0 = Projection(id=proj_id, \
                                   presynaptic_population=conn.pre_cell,
                                   postsynaptic_population=conn.post_cell,
                                   synapse=syn_new.id)

                net.projections.append(proj0)

                # Add a Connection with the closest locations

                pre_cell_id= get_cell_id_string(conn.pre_cell, params)
                post_cell_id= get_cell_id_string(conn.post_cell, params, muscle=True)

                conn0 = Connection(id="0", \
                                   pre_cell_id=pre_cell_id,
                                   post_cell_id=post_cell_id)

                proj0.connections.append(conn0)



    # import pprint
    # pprint.pprint(lems_info)
    template_path = root_dir+'/../' if test else root_dir+'/' # if running test
    write_to_file(nml_doc, lems_info, net_id, template_path, validate=validate, verbose=verbose, target_directory=target_directory)


    return nml_doc

'''
    Input:    string of form ["AVAL","AVBL"]
    returns:  ["AVAL", "AVBL"]
'''
def parse_list_arg(list_arg):
    if not list_arg: return None
    entries = list_arg[1:-1].split(',')
    ret = [e for e in entries]
    print_("Command line argument %s parsed as: %s"%(list_arg,ret))
    return ret

'''
    Input:    string of form ["ADAL-AIBL":2.5,"I1L-I1R":0.5]
    returns:  {}
'''
def parse_dict_arg(dict_arg):
    if not dict_arg or dict_arg == "None": return None
    ret = {}
    entries = str(dict_arg[1:-1]).split(',')
    for e in entries:
        try:
            ret[e.split(':')[0]] = float(e.split(':')[1]) # {'AVAL-AVAR':1}
        except ValueError:
            ret[e.split(':')[0]] = str(e.split(':')[1]) # {'AVAL-AVAR':'inh'}
    print_("Command line argument %s parsed as: %s"%(dict_arg,ret))
    return ret

def main():

    args = process_args()
    
    exec('from %s import ParameterisedModel'%args.parameters)
    params = ParameterisedModel()

    generate(args.reference,
             params,
             data_reader =            args.datareader,
             cells =                  parse_list_arg(args.cells),
             cells_to_plot =          parse_list_arg(args.cellstoplot),
             cells_to_stimulate =     parse_list_arg(args.cellstostimulate),
             conn_polarity_override = parse_dict_arg(args.connpolarityoverride),
             conn_number_override =   parse_dict_arg(args.connnumberoverride),
             conn_number_scaling =    parse_dict_arg(args.connnumberscaling),
             muscles_to_include =     parse_list_arg(args.musclestoinclude),
             duration =               args.duration,
             dt =                     args.dt,
             vmin =                   args.vmin,
             vmax =                   args.vmax)




if __name__ == '__main__':

    main()


