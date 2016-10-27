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
from neuroml import SynapticConnection
from neuroml import ElectricalProjection
from neuroml import ElectricalConnection
from neuroml import ElectricalConnectionInstance
from neuroml import ContinuousProjection
from neuroml import ContinuousConnectionInstance
from neuroml import ExpTwoSynapse
from neuroml import GapJunction
from neuroml import GradedSynapse
from neuroml import Property
from neuroml import PulseGenerator
from neuroml import SilentSynapse

import neuroml.writers as writers
import neuroml.loaders as loaders

import bioparameters

import airspeed

import random
import argparse
import shutil
import os

try:
    from urllib2 import URLError  # Python 2
except:
    from urllib import URLError  # Python 3

import sys
sys.path.append("..")
import SpreadsheetDataReader

LEMS_TEMPLATE_FILE = "LEMS_c302_TEMPLATE.xml"


def process_args():
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description="A script which can generate NeuroML2 compliant networks based on the C elegans connectome, along with LEMS files to run them")

    parser.add_argument('reference', type=str, metavar='<reference>',
                        help='Unique reference for new network')

    parser.add_argument('parameters', type=str, metavar='<parameters>',
                        help='Set of biophysical parametes to use, e.g. parameters_A')

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

    parser.add_argument('-connnumberoverride',
                        type=str,
                        metavar='<conn-number-override>',
                        default=None,
                        help='Map of connection numbers to override, e.g. {"I1L-I3":2.5} => use 2.5 connections from I1L to I3')

    parser.add_argument('-connnumberscaling',
                        type=str,
                        metavar='<conn-number-scaling>',
                        default=None,
                        help='Map of scaling factors for connection numbers, e.g. {"I1L-I3":2} => use 2 times as many connections from I1L to I3')

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


quadrant0 = 'MDR'
quadrant1 = 'MVR'
quadrant2 = 'MVL'
quadrant3 = 'MDL'


def add_new_input(nml_doc, cell, delay, duration, amplitude, params):
    
    stim = PulseGenerator(id="stim_"+cell, delay=delay, duration=duration, amplitude=amplitude)
    
    nml_doc.pulse_generators.append(stim)
    
    
    target = get_cell_id_string(cell, params)
        
    input_list = InputList(id="Input_%s_%s"%(cell,stim.id),
                         component=stim.id,
                         populations='%s'%cell)

    input_list.input.append(Input(id=0, 
                  target=target, 
                  destination="synapses"))
                  
    nml_doc.networks[0].input_lists.append(input_list)


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
    lems = open(lems_file_name, 'w')

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

    new_id = "%s_%sconns"%(prototype_syn.id, str(n).replace('.', '_'))
    
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
            new_syn = GapJunction(id=new_id,
                                  conductance =       "%s%s"%(magnitude*n, unit))

            existing_synapses[new_id] = new_syn
            nml_doc.gap_junctions.append(new_syn)

        elif isinstance(prototype_syn, GradedSynapse):
            magnitude, unit = bioparameters.split_neuroml_quantity(prototype_syn.conductance)
            new_syn = GradedSynapse(id=new_id,
                                    conductance =       "%s%s"%(magnitude*n, unit),
                                    delta =             prototype_syn.delta,
                                    Vth =               prototype_syn.Vth,
                                    erev =              prototype_syn.erev,
                                    k =                 prototype_syn.k)

            existing_synapses[new_id] = new_syn
            nml_doc.graded_synapses.append(new_syn)

    else:
        new_syn = existing_synapses[new_id]

    return new_syn


def get_file_name_relative_to_c302(file_name):
    
    if os.environ.has_key('C302_HOME'):
        return os.path.relpath(os.environ['C302_HOME'],file_name)
    
    
def get_cell_names_and_connection(test=False):
    
    # Use the spreadsheet reader to give a list of all cells and a list of all connections
    # This could be replaced with a call to "DatabaseReader" or "OpenWormNeuroLexReader" in future...
    # If called from unittest folder ammend path to "../../../../"
    
    spreadsheet_location = os.path.dirname(os.path.abspath(__file__))+"/../../../"

    cell_names, conns = SpreadsheetDataReader.readDataFromSpreadsheet(include_nonconnected_cells=True)

    cell_names.sort()
    
    return cell_names, conns


def get_cell_muscle_names_and_connection(test=False):
    
    spreadsheet_location = os.path.dirname(os.path.abspath(__file__))+"/../../../"

    mneurons, all_muscles, muscle_conns = SpreadsheetDataReader.readMuscleDataFromSpreadsheet()
    
    return mneurons, all_muscles, muscle_conns


def is_cond_based_cell(params):
    return params.level == "C" or params.level == "C1" or params.level == "D"


def get_cell_id_string(cell, params, muscle=False):
    
    if not params.level == "D":
        if not muscle:
            return "../%s/0/%s"%(cell, params.generic_neuron_cell.id)
        else:
            return "../%s/0/%s"%(cell, params.generic_muscle_cell.id)
    
    else:
        return "../%s/0/%s"%(cell, cell)
    
    
def generate(net_id,
             params,
             cells = None,
             cells_to_plot = None,
             cells_to_stimulate = None,
             include_muscles=False,
             conn_number_override = None,
             conn_number_scaling = None,
             duration = 500,
             dt = 0.01,
             vmin = None,
             vmax = None,
             seed = 1234,
             validate=True, 
             test=False,
             verbose=True,
             target_directory='./'):
                
    root_dir = os.path.dirname(os.path.abspath(__file__))

    params.create_models()
    
    if vmin==None:
        if params.level == 'A':
            vmin=-72
        elif params.level == 'B':
            vmin=-52 
        elif params.level == 'C':
            vmin=-60
        elif params.level == 'D':
            vmin=-60
        else:
            vmin=-52 
            
    
    if vmax==None:
        if params.level == 'A':
            vmax=-48
        elif params.level == 'B':
            vmax=-28
        elif params.level == 'C':
            vmax=25
        elif params.level == 'D':
            vmax=25
        else:
            vmax=-28
    
    random.seed(seed)

    info = "\n\nParameters and setting used to generate this network:\n\n"+\
           "    Cells:                         %s\n" % (cells if cells is not None else "All cells")+\
           "    Cell stimulated:               %s\n" % (cells_to_stimulate if cells_to_stimulate is not None else "All cells")+\
           "    Connection numbers overridden: %s\n" % (conn_number_override if conn_number_override is not None else "None")+\
           "    Connection numbers scaled:     %s\n" % (conn_number_scaling if conn_number_scaling is not None else "None")+\
           "    Include muscles:               %s\n" % include_muscles
    print_(info)
    info += "\n%s\n"%(params.bioparameter_info("    "))

    nml_doc = NeuroMLDocument(id=net_id, notes=info)

    if params.level == "A" or params.level == "B" or params.level == "BC1":
        nml_doc.iaf_cells.append(params.generic_muscle_cell) 
        nml_doc.iaf_cells.append(params.generic_neuron_cell) 
    elif params.level == "C":
        nml_doc.cells.append(params.generic_muscle_cell)
        nml_doc.cells.append(params.generic_neuron_cell)
    elif params.level == "D":
        nml_doc.cells.append(params.generic_muscle_cell)
         

    net = Network(id=net_id)


    nml_doc.networks.append(net)

    nml_doc.pulse_generators.append(params.offset_current)

    if is_cond_based_cell(params):
        nml_doc.fixed_factor_concentration_models.append(params.concentration_model)


    cell_names, conns = get_cell_names_and_connection()

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
        lems_info["includes"].append(params.custom_component_types_definitions)
        if target_directory != './':
            def_file = "%s/%s"%(os.path.dirname(os.path.abspath(__file__)), params.custom_component_types_definitions)
            shutil.copy(def_file, target_directory)
        nml_doc.includes.append(IncludeType(href=params.custom_component_types_definitions))
    
    
    backers_dir = root_dir+"/../../../../OpenWormBackers/" if test else root_dir+"/../../../OpenWormBackers/"
    sys.path.append(backers_dir)
    import backers
    cells_vs_name = backers.get_adopted_cell_names(backers_dir)


    count = 0
    for cell in cell_names:

        if cells is None or cell in cells:

            inst = Instance(id="0")

            if not params.level == "D":
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
            
            
            if params.level == "D":
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
                if params.level == "D":
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

                if params.level == "B":
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

            if params.level == "B":
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

    mneurons, all_muscles, muscle_conns = get_cell_muscle_names_and_connection()

    muscles = get_muscle_names()

    if include_muscles:

        muscle_count = 0
        for muscle in muscles:

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

            x = 80 * (-1 if muscle[1] == 'V' else 1)
            z = 80 * (-1 if muscle[2] == 'L' else 1)
            y = -300 + 30 * int(muscle[3:5])
            print_('Positioning muscle: %s at (%s,%s,%s)'%(muscle,x,y,z))
            inst.location = Location(x,y,z)

            target = "%s/0/%s"%(pop0.id, params.generic_muscle_cell.id)

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

        if verbose: 
            print_("Finished creating %i muscles"%muscle_count)
        
    
    existing_synapses = {}

    for conn in conns:

        if conn.pre_cell in lems_info["cells"] and conn.post_cell in lems_info["cells"]:
            # take information about each connection and package it into a
            # NeuroML Projection data structure
            proj_id = get_projection_id(conn.pre_cell, conn.post_cell, conn.synclass, conn.syntype)

            elect_conn = False
            analog_conn = False
            syn0 = params.neuron_to_neuron_exc_syn
            if 'GABA' in conn.synclass:
                syn0 = params.neuron_to_neuron_inh_syn
            if '_GJ' in conn.synclass:
                syn0 = params.neuron_to_neuron_elec_syn
                elect_conn = isinstance(params.neuron_to_neuron_elec_syn, GapJunction)
                
            if isinstance(syn0, GradedSynapse):
                analog_conn = True
                if len(nml_doc.silent_synapses)==0:
                    silent = SilentSynapse(id="silent")
                    nml_doc.silent_synapses.append(silent)

            number_syns = conn.number
            conn_shorthand = "%s-%s"%(conn.pre_cell, conn.post_cell)

            if conn_number_override is not None and (conn_number_override.has_key(conn_shorthand)):
                number_syns = conn_number_override[conn_shorthand]
            elif conn_number_scaling is not None and (conn_number_scaling.has_key(conn_shorthand)):
                number_syns = conn.number*conn_number_scaling[conn_shorthand]
            '''
            else:
                print conn_shorthand
                print conn_number_override
                print conn_number_scaling'''

            if number_syns != conn.number:
                magnitude, unit = bioparameters.split_neuroml_quantity(syn0.gbase)
                cond0 = "%s%s"%(magnitude*conn.number, unit)
                cond1 = "%s%s"%(magnitude*number_syns, unit)
                if verbose: 
                    print_(">> Changing number of effective synapses connection %s -> %s: was: %s (total cond: %s), becomes %s (total cond: %s)" % \
                     (conn.pre_cell, conn.post_cell, conn.number, cond0, number_syns, cond1))


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
                conn0 = ElectricalConnectionInstance(id="0", \
                           pre_cell=pre_cell_id,
                           post_cell=post_cell_id,
                           synapse=syn_new.id)

                proj0.electrical_connection_instances.append(conn0)
                
            elif analog_conn:
        
                proj0 = ContinuousProjection(id=proj_id, \
                                   presynaptic_population=conn.pre_cell,
                                   postsynaptic_population=conn.post_cell)

                net.continuous_projections.append(proj0)

                pre_cell_id= get_cell_id_string(conn.pre_cell, params)
                post_cell_id= get_cell_id_string(conn.post_cell, params)

                conn0 = ContinuousConnectionInstance(id="0", \
                           pre_cell=pre_cell_id,
                           post_cell=post_cell_id,
                           pre_component="silent",
                           post_component=syn_new.id)

                proj0.continuous_connection_instances.append(conn0)
                
                
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



    if include_muscles:
      for conn in muscle_conns:

        if conn.pre_cell in lems_info["cells"] and conn.post_cell in muscles:
            # take information about each connection and package it into a
            # NeuroML Projection data structure
            proj_id = get_projection_id(conn.pre_cell, conn.post_cell, conn.synclass, conn.syntype)

            elect_conn = False
            analog_conn = False
            syn0 = params.neuron_to_muscle_exc_syn
            if 'GABA' in conn.synclass:
                syn0 = params.neuron_to_muscle_inh_syn
            if '_GJ' in conn.synclass:
                syn0 = params.neuron_to_muscle_elec_syn
                elect_conn = isinstance(params.neuron_to_muscle_elec_syn, GapJunction)

            if isinstance(syn0, GradedSynapse):
                analog_conn = True
                if len(nml_doc.silent_synapses)==0:
                    silent = SilentSynapse(id="silent")
                    nml_doc.silent_synapses.append(silent)
                    
            number_syns = conn.number
            conn_shorthand = "%s-%s"%(conn.pre_cell, conn.post_cell)

            if conn_number_override is not None and (conn_number_override.has_key(conn_shorthand)):
                number_syns = conn_number_override[conn_shorthand]
            elif conn_number_scaling is not None and (conn_number_scaling.has_key(conn_shorthand)):
                number_syns = conn.number*conn_number_scaling[conn_shorthand]
            '''
            else:
                print conn_shorthand
                print conn_number_override
                print conn_number_scaling'''

            if number_syns != conn.number:
                magnitude, unit = bioparameters.split_neuroml_quantity(syn0.gbase)
                cond0 = "%s%s"%(magnitude*conn.number, unit)
                cond1 = "%s%s"%(magnitude*number_syns, unit)
                if verbose: 
                    print_(">> Changing number of effective synapses connection %s -> %s: was: %s (total cond: %s), becomes %s (total cond: %s)" % \
                     (conn.pre_cell, conn.post_cell, conn.number, cond0, number_syns, cond1))


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
                conn0 = ElectricalConnectionInstance(id="0", \
                           pre_cell=pre_cell_id,
                           post_cell=post_cell_id,
                           synapse=syn_new.id)

                proj0.electrical_connection_instances.append(conn0)
                
            elif analog_conn:
        
                proj0 = ContinuousProjection(id=proj_id, \
                                   presynaptic_population=conn.pre_cell,
                                   postsynaptic_population=conn.post_cell)

                net.continuous_projections.append(proj0)

                pre_cell_id= get_cell_id_string(conn.pre_cell, params)
                post_cell_id= get_cell_id_string(conn.post_cell, params, muscle=True)

                conn0 = ContinuousConnectionInstance(id="0", \
                           pre_cell=pre_cell_id,
                           post_cell=post_cell_id,
                           pre_component="silent",
                           post_component=syn_new.id)

                proj0.continuous_connection_instances.append(conn0)

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
    Input:    string of form ["ADAL-AIBL":2.5,"I1L-I1R":0.5]
    returns:  {}
'''
def parse_dict_arg(dict_arg):
    if not dict_arg: return None
    ret = {}
    entries = str(dict_arg[1:-1]).split(',')
    for e in entries:
        ret[e.split(':')[0]] = float(e.split(':')[1])
    print_("Command line argument %s parsed as: %s"%(dict_arg,ret))
    return ret

def main():

    args = process_args()
    
    exec('from %s import ParameterisedModel'%args.parameters)
    params = ParameterisedModel()

    generate(args.reference,
             params,
             cells =                 args.cells,
             cells_to_plot =         args.cellstoplot,
             cells_to_stimulate =    args.cellstostimulate,
             conn_number_override =  parse_dict_arg(args.connnumberoverride),
             conn_number_scaling =   parse_dict_arg(args.connnumberscaling),
             duration =              args.duration,
             dt =                    args.dt,
             vmin =                  args.vmin,
             vmax =                  args.vmax)




if __name__ == '__main__':

    main()

