""" Convert a selection of files from the subject folder into
a connectome file format for visualization and analysis in the connectomeviewer """

import os, os.path as op
import sys
from time import time
from ...logme import *
import networkx as nx
import numpy as np
try:
    import cfflib as cf
except ImportError:
    print "Please install cfflib to use the connectome file format converter"

def add_cmat2connectome(connectome):
    log.info("Loading cmat.pickle....")
    cmat = nx.read_gpickle(op.join(gconf.get_cmp_matrices(), 'cmat.pickle'))
    resolution = gconf.parcellation.keys()
    for r in resolution:
        log.info("Working on resolution: %s" % r)
        # retrieve the graph
        g = cmat[r]['graph']
        # the graph to use for storage
        gs = nx.Graph()
        # read the parcellation graph for node information
        gp = nx.read_graphml(gconf.parcellation[r]['node_information_graphml'])
        for u,d in gp.nodes_iter(data=True):
            gs.add_node(int(u), d)
        # add edges
        for u,v,d in g.edges_iter(data=True):
            # measures to add, XXX
            di = { 'number_of_fibers' : len(d['fiblist']),
                   'average_fiber_length' : np.mean(d['fiblength'])
                  }
            gs.add_edge(u,v, di)
        cnet = cf.CNetwork(name = 'Network: %s' % r)
        cnet.set_with_nxgraph('connectome_%s' % r, gs)
        #cnet.set_metadata({'segmentation_volume_filename':cmat[r]['graph']})
        
        connectome.add_connectome_network(cnet)
        

def convert_cmat2cff(cmat_fname, cff_fname):
    """ Converts a given cmat file produced by the pipeline into
    a connectome file
    
    Parameters
    ----------
    cmat_fname : string
        The input filename of the graph pickle. Ending .pickle
    cff_fname : string
        Absolute path to the output filename of the cff
    """
    
    cmat = nx.read_gpickle(cmat_fname)
        
    # first, simply create connectome file for networks
    # use the default. graphml, see for correct node labels (integers) to match
    # import cfflib
    # tutorial steps from cfflib for creation, using cmat
    # number of fibers
    # average length
    print "Convert to a connectome file"

    # loop over resolutions and store number of fibers in graphml


def convert2cff():
    
    # filename from metadata name
    # define path in folder structure, maybe root
    
    outputcff = op.join(gconf.get_cffdir(), '%s_%s.cff' % (gconf.subject_name, gconf.subject_timepoint))
    
    c = cf.connectome()
    
    # creating metadata
    c.connectome_meta = cf.CMetadata()                    
    c.connectome_meta.set_name('%s - %s' % (gconf.subject_name, gconf.subject_timepoint) )
    c.connectome_meta.set_generator(gconf.generator)
    c.connectome_meta.set_author(gconf.author)
    c.connectome_meta.set_institution(gconf.institution)
    c.connectome_meta.set_creation_date(gconf.creationdate)
    c.connectome_meta.set_modification_date(gconf.modificationdate)
    c.connectome_meta.set_species(gconf.species)
    c.connectome_meta.set_legal_notice(gconf.legalnotice)
    c.connectome_meta.set_reference(gconf.reference)
    c.connectome_meta.set_url(gconf.url)
    c.connectome_meta.set_description(gconf.description)

    # XXX: depending on what was checked
    if gconf.cff_fullnetworkpickle:
        # adding networks
        add_cmat2connectome(c)
        
    cf.save_to_cff(c,outputcff)
    
# XXX: inputs: need cmat.pickle
    
def run(conf):
    """ Run the CFF Converter module
    
    Parameters
    ----------
    conf : PipelineConfiguration object
        
    """
    # setting the global configuration variable
    globals()['gconf'] = conf
    globals()['log'] = gconf.get_logger() 
    start = time()
    
    log.info("Connectome File Converter")
    log.info("=========================")

    convert2cff()
    
    log.info("Module took %s seconds to process." % (time()-start))
    
    if not len(gconf.emailnotify) == 0:
        msg = "CFF Converter module finished!\nIt took %s seconds." % int(time()-start)
        send_email_notification(msg, gconf.emailnotify, log)
        
def declare_inputs(conf):
    """Declare the inputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)
    
    conf.pipeline_status.AddStageInput(stage, conf.get_cmp_matrices(), 'cmat.pickle', 'cmat-pickle')
        
    
def declare_outputs(conf):
    """Declare the outputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)
       
    conf.pipeline_status.AddStageOutput(stage, conf.get_cffdir(), '%s_%s.cff' % (conf.subject_name, conf.subject_timepoint), 'connectome-cff')