from neuroml import NeuroMLDocument
from neuroml import Network
from neuroml import Population
from neuroml import Instance
from neuroml import Location
from neuroml import ExplicitInput
from neuroml import Projection
from neuroml import Connection
import neuroml.writers as writers
import neuroml.loaders as loaders

import airspeed

import random

try:
    from urllib2 import URLError  # Python 2
except:
    from urllib import URLError  # Python 3

import sys
sys.path.append("..")
import SpreadsheetDataReader

LEMS_TEMPLATE_FILE = "LEMS_c302_TEMPLATE.xml"


def merge_with_template(model, templfile):
    with open(templfile) as f:
        templ = airspeed.Template(f.read())
    return templ.merge(model)

                        
def write_to_file(nml_doc, lems_info, reference, validate=True):

    #######   Write to file  ######    

    nml_file = reference+'.nml'
    writers.NeuroMLWriter.write(nml_doc, nml_file)

    print("Written network file to: "+nml_file)

    lems_file_name = 'LEMS_%s.xml'%reference
    lems = open(lems_file_name, 'w')
    
    merged = merge_with_template(lems_info, LEMS_TEMPLATE_FILE)
    lems.write(merged)

    print("Written LEMS file to: "+lems_file_name)

    if validate:

        ###### Validate the NeuroML ######    

        from neuroml.utils import validate_neuroml2
        try: 
            validate_neuroml2(nml_file)
        except URLError as e:
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
        
def generate(net_id, params, cells = None, cells_to_plot=None, cells_to_stimulate=None, duration=500, dt=0.01, vmin=-75, vmax=20):
    
    nml_doc = NeuroMLDocument(id=net_id)

    nml_doc.iaf_cells.append(params.generic_cell)

    nml_doc.exp_two_synapses.append(params.exc_syn)

    nml_doc.exp_two_synapses.append(params.inh_syn)

    net = Network(id=net_id)

    nml_doc.networks.append(net)

    nml_doc.pulse_generators.append(params.offset_current)

    # Use the spreadsheet reader to give a list of all cells and a list of all connections
    # This could be replaced with a call to "DatabaseReader" or "OpenWormNeuroLexReader" in future...
    cell_names, conns = SpreadsheetDataReader.readDataFromSpreadsheet("../../../")

    cell_names.sort()

    # To hold all Cell NeuroML objects vs. names
    all_cells = {}

    # lems_file = ""
    lems_info = {"reference":  net_id,
                 "duration":   duration,
                 "dt":         dt,
                 "vmin":       vmin,
                 "vmax":       vmax,
                 "cell_component":    params.generic_cell.id}
    
    lems_info["plots"] = []
    lems_info["cells"] = []

    for cell in cell_names:
        
        if cells is None or cell in cells:
            # build a Population data structure out of the cell name
            pop0 = Population(id=cell, 
                              component=params.generic_cell.id,
                              type="populationList")

            inst = Instance(id="0")
            pop0.instances.append(inst)

            # put that Population into the Network data structure from above
            net.populations.append(pop0)

            # also use the cell name to grab the morphology file, as a NeuroML data structure
            #  into the 'all_cells' dict
            cell_file = '../../generatedNeuroML2/%s.nml'%cell
            doc = loaders.NeuroMLLoader.load(cell_file)
            all_cells[cell] = doc.cells[0]
            location = doc.cells[0].morphology.segments[0].proximal
            print("Loaded morphology file from: %s, with id: %s, location: (%s, %s, %s)"%(cell_file, all_cells[cell].id, location.x, location.y, location.z))

            inst.location = Location(float(location.x), float(location.y), float(location.z))

            exp_input = ExplicitInput(target="%s/0/%s"%(pop0.id, params.generic_cell.id),
                                                     input=params.offset_current.id)

            if cells_to_stimulate is None or cell in cells_to_stimulate:
                net.explicit_inputs.append(exp_input)
                
            if cells_to_plot is None or cell in cells_to_plot:
                plot = {}
                
                plot["cell"] = cell
                plot["colour"] = get_random_colour_hex()
                lems_info["plots"].append(plot)
                
            lems_info["cells"].append(cell)
            

    for conn in conns:

        if conn.pre_cell in lems_info["cells"] and conn.post_cell in lems_info["cells"]:
            # take information about each connection and package it into a 
            # NeuroML Projection data structure
            proj_id = get_projection_id(conn.pre_cell, conn.post_cell, conn.synclass, conn.syntype)

            syn = params.exc_syn.id
            if 'GABA' in conn.synclass:
                syn = params.inh_syn.id

            proj0 = Projection(id=proj_id, \
                               presynaptic_population=conn.pre_cell, 
                               postsynaptic_population=conn.post_cell, 
                               synapse=syn)

            # Get the corresponding Cell for each 
            # pre_cell = all_cells[conn.pre_cell]
            # post_cell = all_cells[conn.post_cell]

            net.projections.append(proj0)

            for conn_id in range(0,conn.number):

                # Add a Connection with the closest locations
                conn0 = Connection(id=conn_id, \
                           pre_cell_id="../%s/0/%s"%(conn.pre_cell, params.generic_cell.id),
                           post_cell_id="../%s/0/%s"%(conn.post_cell, params.generic_cell.id))

                proj0.connections.append(conn0)

    

    write_to_file(nml_doc, lems_info, net_id)

