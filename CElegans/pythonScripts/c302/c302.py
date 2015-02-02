#! /usr/bin/env python

from neuroml import NeuroMLDocument
from neuroml import Network
from neuroml import Population
from neuroml import Instance
from neuroml import Location
from neuroml import ExplicitInput
from neuroml import Projection
from neuroml import Connection
from neuroml import SynapticConnection
from neuroml import ElectricalProjection
from neuroml import ElectricalConnection
from neuroml import ExpTwoSynapse
from neuroml import GapJunction
from neuroml import Property

import neuroml.writers as writers
import neuroml.loaders as loaders
from bioparameters import bioparameter_info

import airspeed

import random

import argparse

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



def write_to_file(nml_doc, lems_info, reference, template_path='', validate=True):

    #######   Write to file  ######

    nml_file = reference+'.nml'
    writers.NeuroMLWriter.write(nml_doc, nml_file)

    print("Written network file to: "+nml_file)

    lems_file_name = 'LEMS_%s.xml'%reference
    lems = open(lems_file_name, 'w')

    # if running unittest concat template_path

    merged = merge_with_template(lems_info, template_path+LEMS_TEMPLATE_FILE)
    lems.write(merged)

    print("Written LEMS file to: "+lems_file_name)

    if validate:

        ###### Validate the NeuroML ######

        from neuroml.utils import validate_neuroml2
        try:
            validate_neuroml2(nml_file)
        except URLError:
            print("Problem validating against remote Schema!")


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


existing_synapses = {}

def create_n_connection_synapse(prototype_syn, n, nml_doc):

    new_id = "%s_%sconns"%(prototype_syn.id, str(n).replace('.', '_'))

    if not existing_synapses.has_key(new_id):

        if isinstance(prototype_syn, ExpTwoSynapse):
            magnitude, unit = split_neuroml_quantity(prototype_syn.gbase)
            new_syn = ExpTwoSynapse(id=new_id,
                                gbase =       "%s%s"%(magnitude*n, unit),
                                erev =        prototype_syn.erev,
                                tau_decay =   prototype_syn.tau_decay,
                                tau_rise =    prototype_syn.tau_rise)

            existing_synapses[new_id] = new_syn
            nml_doc.exp_two_synapses.append(new_syn)

        elif isinstance(prototype_syn, GapJunction):
            magnitude, unit = split_neuroml_quantity(prototype_syn.conductance)
            new_syn = GapJunction(id=new_id,
                                  conductance =       "%s%s"%(magnitude*n, unit))

            existing_synapses[new_id] = new_syn
            nml_doc.gap_junctions.append(new_syn)

    else:
        new_syn = existing_synapses[new_id]

    return new_syn


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
             vmin = -75,
             vmax = 20,
             seed = 1234,
             validate=True, test=False):

    random.seed(seed)

    info = "\n\nParameters and setting used to generate this network:\n\n"+\
           "    Cells:                         %s\n" % (cells if cells is not None else "All cells")+\
           "    Cell stimulated:               %s\n" % (cells_to_stimulate if cells_to_stimulate is not None else "All cells")+\
           "    Connection numbers overridden: %s\n" % (conn_number_override if conn_number_override is not None else "None")+\
           "    Connection numbers scaled:     %s\n" % (conn_number_scaling if conn_number_scaling is not None else "None")+\
           "    Include muscles:               %s\n" % include_muscles
    info += "\n%s\n"%(bioparameter_info("    "))

    nml_doc = NeuroMLDocument(id=net_id, notes=info)

    nml_doc.iaf_cells.append(params.generic_cell)

    net = Network(id=net_id)


    nml_doc.networks.append(net)

    nml_doc.pulse_generators.append(params.offset_current)

    # Use the spreadsheet reader to give a list of all cells and a list of all connections
    # This could be replaced with a call to "DatabaseReader" or "OpenWormNeuroLexReader" in future...
    # If called from unittest folder ammend path to "../../../../"
    spreadsheet_location = "../../../../" if test else "../../../"

    cell_names, conns = SpreadsheetDataReader.readDataFromSpreadsheet(spreadsheet_location, include_nonconnected_cells=True)

    cell_names.sort()

    # To hold all Cell NeuroML objects vs. names
    all_cells = {}

    # lems_file = ""
    lems_info = {"comment":    info,
                 "reference":  net_id,
                 "duration":   duration,
                 "dt":         dt,
                 "vmin":       vmin,
                 "vmax":       vmax,
                 "cell_component":    params.generic_cell.id}

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

    if hasattr(params.generic_cell, 'custom_component_type_definition'):
        lems_info["includes"].append(params.generic_cell.custom_component_type_definition)

    backers_dir = "../../../../OpenWormBackers/" if test else "../../../OpenWormBackers/"
    sys.path.append(backers_dir)
    import backers
    cells_vs_name = backers.get_adopted_cell_names(backers_dir)

    populations_without_location = isinstance(params.elec_syn, GapJunction)

    count = 0
    for cell in cell_names:

        if cells is None or cell in cells:

            inst = Instance(id="0")

            if not populations_without_location:
                # build a Population data structure out of the cell name
                pop0 = Population(id=cell,
                                  component=params.generic_cell.id,
                                  type="populationList")
                pop0.instances.append(inst)

            else:
                # build a Population data structure out of the cell name
                pop0 = Population(id=cell,
                                  component=params.generic_cell.id,
                                  size="1")


            # put that Population into the Network data structure from above
            net.populations.append(pop0)

            if cells_vs_name.has_key(cell):
                p = Property(tag="OpenWormBackerAssignedName", value=cells_vs_name[cell])
                pop0.properties.append(p)

            # also use the cell name to grab the morphology file, as a NeuroML data structure
            #  into the 'all_cells' dict
            cell_file_path = "../../../" if test else "../../" #if running test
            cell_file = cell_file_path+'generatedNeuroML2/%s.nml'%cell
            doc = loaders.NeuroMLLoader.load(cell_file)
            all_cells[cell] = doc.cells[0]
            location = doc.cells[0].morphology.segments[0].proximal
            print("Loaded morphology file from: %s, with id: %s, location: (%s, %s, %s)"%(cell_file, all_cells[cell].id, location.x, location.y, location.z))


            inst.location = Location(float(location.x), float(location.y), float(location.z))

            target = "%s/0/%s"%(pop0.id, params.generic_cell.id)
            if populations_without_location:
                target = "%s[0]" % (cell)

            exp_input = ExplicitInput(target=target, input=params.offset_current.id)

            if cells_to_stimulate is None or cell in cells_to_stimulate:
                net.explicit_inputs.append(exp_input)

            if cells_to_plot is None or cell in cells_to_plot:
                plot = {}

                plot["cell"] = cell
                plot["colour"] = get_random_colour_hex()
                plot["quantity"] = "%s/0/%s/v" % (cell, params.generic_cell.id)
                if populations_without_location:
                    plot["quantity"] = "%s[0]/v" % (cell)
                lems_info["plots"].append(plot)

                if hasattr(params.generic_cell, 'custom_component_type_definition'):
                    plot = {}

                    plot["cell"] = cell
                    plot["colour"] = get_random_colour_hex()
                    plot["quantity"] = "%s/0/%s/activity" % (cell, params.generic_cell.id)
                    if populations_without_location:
                        plot["quantity"] = "%s[0]/activity" % (cell)
                    lems_info["activity_plots"].append(plot)

            save = {}
            save["cell"] = cell
            save["quantity"] = "%s/0/%s/v" % (cell, params.generic_cell.id)
            if populations_without_location:
                save["quantity"] = "%s[0]/v" % (cell)
            lems_info["to_save"].append(save)

            if hasattr(params.generic_cell, 'custom_component_type_definition'):
                save = {}
                save["cell"] = cell
                save["quantity"] = "%s/0/%s/activity" % (cell, params.generic_cell.id)
                if populations_without_location:
                    save["quantity"] = "%s[0]/activity" % (cell)
                lems_info["activity_to_save"].append(save)

            lems_info["cells"].append(cell)

            count+=1

    print("Finished loading %i cells"%count)

    mneurons, all_muscles, muscle_conns = SpreadsheetDataReader.readMuscleDataFromSpreadsheet(spreadsheet_location)

    muscles = get_muscle_names()

    if include_muscles:

        muscle_count = 0
        for muscle in muscles:

            inst = Instance(id="0")

            if not populations_without_location:
                # build a Population data structure out of the cell name
                pop0 = Population(id=muscle,
                                  component=params.generic_cell.id,
                                  type="populationList")
                pop0.instances.append(inst)

            else:
                # build a Population data structure out of the cell name
                pop0 = Population(id=muscle,
                                  component=params.generic_cell.id,
                                  size="1")

            # put that Population into the Network data structure from above
            net.populations.append(pop0)

            if cells_vs_name.has_key(muscle):
                # No muscles adopted yet, but just in case they are in future...
                p = Property(tag="OpenWormBackerAssignedName", value=cells_vs_name[muscle])
                pop0.properties.append(p)

            inst.location = Location(100, 10*muscle_count, 100)

            target = "%s/0/%s"%(pop0.id, params.generic_cell.id)
            if populations_without_location:
                target = "%s[0]" % (muscle)

            plot = {}

            plot["cell"] = muscle
            plot["colour"] = get_random_colour_hex()
            plot["quantity"] = "%s/0/%s/v" % (muscle, params.generic_cell.id)
            if populations_without_location:
                plot["quantity"] = "%s[0]/v" % (muscle)
            lems_info["muscle_plots"].append(plot)

            if hasattr(params.generic_cell, 'custom_component_type_definition'):
                plot = {}

                plot["cell"] = muscle
                plot["colour"] = get_random_colour_hex()
                plot["quantity"] = "%s/0/%s/activity" % (muscle, params.generic_cell.id)
                if populations_without_location:
                    plot["quantity"] = "%s[0]/activity" % (muscle)
                lems_info["muscle_activity_plots"].append(plot)

            save = {}
            save["cell"] = muscle
            save["quantity"] = "%s/0/%s/v" % (muscle, params.generic_cell.id)
            if populations_without_location:
                save["quantity"] = "%s[0]/v" % (muscle)
            lems_info["muscles_to_save"].append(save)

            if hasattr(params.generic_cell, 'custom_component_type_definition'):
                save = {}
                save["cell"] = muscle
                save["quantity"] = "%s/0/%s/activity" % (muscle, params.generic_cell.id)
                if populations_without_location:
                    save["quantity"] = "%s[0]/activity" % (muscle)
                lems_info["muscles_activity_to_save"].append(save)

            lems_info["muscles"].append(muscle)

            muscle_count+=1

        print("Finished creating %i muscles"%muscle_count)

    for conn in conns:

        if conn.pre_cell in lems_info["cells"] and conn.post_cell in lems_info["cells"]:
            # take information about each connection and package it into a
            # NeuroML Projection data structure
            proj_id = get_projection_id(conn.pre_cell, conn.post_cell, conn.synclass, conn.syntype)

            elect_conn = False
            syn0 = params.exc_syn
            if 'GABA' in conn.synclass:
                syn0 = params.inh_syn
            if '_GJ' in conn.synclass:
                syn0 = params.elec_syn
                elect_conn = isinstance(params.elec_syn, GapJunction)

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
                magnitude, unit = split_neuroml_quantity(syn0.gbase)
                cond0 = "%s%s"%(magnitude*conn.number, unit)
                cond1 = "%s%s"%(magnitude*number_syns, unit)
                print(">> Changing number of effective synapses connection %s -> %s: was: %s (total cond: %s), becomes %s (total cond: %s)" % \
                     (conn.pre_cell, conn.post_cell, conn.number, cond0, number_syns, cond1))


            syn_new = create_n_connection_synapse(syn0, number_syns, nml_doc)

            if not elect_conn:

                if not populations_without_location:
                    proj0 = Projection(id=proj_id, \
                                       presynaptic_population=conn.pre_cell,
                                       postsynaptic_population=conn.post_cell,
                                       synapse=syn_new.id)

                    net.projections.append(proj0)

                    # Add a Connection with the closest locations

                    pre_cell_id="../%s/0/%s"%(conn.pre_cell, params.generic_cell.id)
                    post_cell_id="../%s/0/%s"%(conn.post_cell, params.generic_cell.id)

                    conn0 = Connection(id="0", \
                               pre_cell_id=pre_cell_id,
                               post_cell_id=post_cell_id)

                    proj0.connections.append(conn0)

                if populations_without_location:
                    #         <synapticConnection from="hh1pop[0]" to="hh2pop[0]" synapse="syn1exp" destination="synapses"/>
                    pre_cell_id="%s[0]"%(conn.pre_cell)
                    post_cell_id="%s[0]"%(conn.post_cell)

                    conn0 = SynapticConnection(from_=pre_cell_id,
                               to=post_cell_id,
                               synapse=syn_new.id,
                               destination="synapses")

                    net.synaptic_connections.append(conn0)


            else:
                proj0 = ElectricalProjection(id=proj_id, \
                                   presynaptic_population=conn.pre_cell,
                                   postsynaptic_population=conn.post_cell)

                net.electrical_projections.append(proj0)

                # Add a Connection with the closest locations
                conn0 = ElectricalConnection(id="0", \
                           pre_cell="0",
                           post_cell="0",
                           synapse=syn_new.id)

                proj0.electrical_connections.append(conn0)


    if include_muscles:
      for conn in muscle_conns:

        if conn.pre_cell in lems_info["cells"] and conn.post_cell in muscles:
            # take information about each connection and package it into a
            # NeuroML Projection data structure
            proj_id = get_projection_id(conn.pre_cell, conn.post_cell, conn.synclass, conn.syntype)

            elect_conn = False
            syn0 = params.exc_syn
            if 'GABA' in conn.synclass:
                syn0 = params.inh_syn
            if '_GJ' in conn.synclass:
                syn0 = params.elec_syn
                elect_conn = isinstance(params.elec_syn, GapJunction)

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
                magnitude, unit = split_neuroml_quantity(syn0.gbase)
                cond0 = "%s%s"%(magnitude*conn.number, unit)
                cond1 = "%s%s"%(magnitude*number_syns, unit)
                print(">> Changing number of effective synapses connection %s -> %s: was: %s (total cond: %s), becomes %s (total cond: %s)" % \
                     (conn.pre_cell, conn.post_cell, conn.number, cond0, number_syns, cond1))


            syn_new = create_n_connection_synapse(syn0, number_syns, nml_doc)

            if not elect_conn:

                if not populations_without_location:
                    proj0 = Projection(id=proj_id, \
                                       presynaptic_population=conn.pre_cell,
                                       postsynaptic_population=conn.post_cell,
                                       synapse=syn_new.id)

                    net.projections.append(proj0)

                    # Add a Connection with the closest locations

                    pre_cell_id="../%s/0/%s"%(conn.pre_cell, params.generic_cell.id)
                    post_cell_id="../%s/0/%s"%(conn.post_cell, params.generic_cell.id)

                    conn0 = Connection(id="0", \
                               pre_cell_id=pre_cell_id,
                               post_cell_id=post_cell_id)

                    proj0.connections.append(conn0)

                if populations_without_location:
                    #         <synapticConnection from="hh1pop[0]" to="hh2pop[0]" synapse="syn1exp" destination="synapses"/>
                    pre_cell_id="%s[0]"%(conn.pre_cell)
                    post_cell_id="%s[0]"%(conn.post_cell)

                    conn0 = SynapticConnection(from_=pre_cell_id,
                               to=post_cell_id,
                               synapse=syn_new.id,
                               destination="synapses")

                    net.synaptic_connections.append(conn0)


            else:
                proj0 = ElectricalProjection(id=proj_id, \
                                   presynaptic_population=conn.pre_cell,
                                   postsynaptic_population=conn.post_cell)

                net.electrical_projections.append(proj0)

                # Add a Connection with the closest locations
                conn0 = ElectricalConnection(id="0", \
                           pre_cell="0",
                           post_cell="0",
                           synapse=syn_new.id)

                proj0.electrical_connections.append(conn0)

    # import pprint
    # pprint.pprint(lems_info)
    template_path = '../' if test else '' # if running test
    write_to_file(nml_doc, lems_info, net_id, template_path, validate=validate)


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
    print("Command line argument %s parsed as: %s"%(dict_arg,ret))
    return ret

def main():

    args = process_args()

    exec("import %s as params"%args.parameters)

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

