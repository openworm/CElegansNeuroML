import c302
import sys

import neuroml.writers as writers

    
def setup(parameter_set, 
          generate=False,
          duration=2000,
          dt=0.05,
          target_directory='examples',
          data_reader="SpreadsheetDataReader"):
    
    exec('from parameters_%s import ParameterisedModel'%parameter_set)
    params = ParameterisedModel()

    params.set_bioparameter("unphysiological_offset_current", "0pA", "Testing TapWithdrawal", "0")
    params.set_bioparameter("unphysiological_offset_current_del", "0 ms", "Testing TapWithdrawal", "0")
    params.set_bioparameter("unphysiological_offset_current_dur", "2000 ms", "Testing TapWithdrawal", "0")

    cells = ['AVAL', 'AVAR', 'AVBL', 'AVBR', 'PVCL', 'PVCR', 'AVDL', 'AVDR', 'DVA', 'PVDL', 'PVDR', 'PLML', 'PLMR', 'AVM', 'ALML', 'ALMR']
    cells_to_stimulate = ['PLML', 'PLMR', 'AVM']
    cells_to_stimulate = []

    cells_to_plot = ['AVAL', 'AVAR', 'AVBL', 'AVBR', 'PLML', 'PLMR', 'AVM', 'PVDL', 'PVDR', 'AVDL', 'AVDR']
    cells_to_plot = ['PLML', 'AVM', 'AVBL', 'AVAL']
    #cells_to_plot = cells
    reference = "c302_%s_TapWithdrawal"%parameter_set

    
    if generate:
        nml_doc = c302.generate(reference, 
                 params, 
                 cells=cells,
                 cells_to_plot=cells_to_plot,
                 cells_to_stimulate=cells_to_stimulate,
                 conn_polarity_override={
                    'ALML-ALML':'inh',
                    'ALML-PVCL':'inh',
                    'ALML-PVCR':'inh',
                    'ALML-AVDR':'inh',
                    'ALMR-PVCR':'inh',

                    'AVM-PVCL':'inh',
                    'AVM-PVCR':'inh',
                    'AVM-AVBL':'inh',
                    'AVM-AVBR':'inh',
                    'AVM-AVDL':'inh',
                    'AVM-AVDR':'inh',

                    'PVDL-PVDR':'inh',
                    'PVDL-PVCL':'inh',
                    'PVDL-PVCR':'inh',
                    'PVDL-AVAL':'inh',
                    'PVDL-AVAR':'inh',
                    'PVDL-AVDL':'inh',
                    'PVDL-AVDR':'inh',
                    'PVDR-PVDL':'inh',
                    'PVDR-DVA':'inh',
                    'PVDR-PVCL':'inh',
                    'PVDR-PVCR':'inh',
                    'PVDR-AVAL':'inh',
                    'PVDR-AVAR':'inh',
                    'PVDR-AVDL':'inh',

                    'DVA-PVCL':'inh',
                    'DVA-PVCR':'inh',
                    'DVA-AVAL':'inh',
                    'DVA-AVAR':'inh',
                    'DVA-AVBL':'inh',
                    'DVA-AVBR':'inh',
                    'DVA-AVDR':'inh',

                    'PVCL-DVA':'exc',
                    'PVCL-PVCL':'exc',
                    'PVCL-PVCR':'exc',
                    'PVCL-AVAL':'inh',
                    'PVCL-AVAR':'inh',
                    'PVCL-AVBL':'exc',
                    'PVCL-AVBR':'exc',
                    'PVCL-AVDL':'inh',
                    'PVCL-AVDR':'inh',
                    'PVCR-PVDL':'exc',
                    'PVCR-PVDR':'exc',
                    'PVCR-DVA':'exc',
                    'PVCR-PVCL':'exc',
                    'PVCR-AVAL':'inh',
                    'PVCR-AVAR':'inh',
                    'PVCR-AVBL':'exc',
                    'PVCR-AVBR':'exc',
                    'PVCR-AVDL':'inh',
                    'PVCR-AVDR':'inh',

                    'AVAL-PVCL':'inh',
                    'AVAL-PVCR':'inh',
                    'AVAL-AVAR':'inh',
                    'AVAL-AVBL':'inh',
                    'AVAL-AVDL':'inh',
                    'AVAL-AVDR':'inh',

                    'AVAR-PVCL':'inh',
                    'AVAR-PVCR':'inh',
                    'AVAR-AVAL':'inh',
                    'AVAR-AVBL':'inh',
                    'AVAR-AVBR':'inh',
                    'AVAR-AVDL':'inh',
                    'AVAR-AVDR':'inh',

                    'AVBL-DVA':'inh',
                    'AVBL-PVCR':'inh',
                    'AVBL-AVAL':'inh',
                    'AVBL-AVAR':'inh',
                    'AVBL-AVBR':'inh',
                    'AVBL-AVDR':'inh',
                    'AVBR-AVAL':'inh',
                    'AVBR-AVAR':'inh',
                    'AVBR-AVBL':'inh',
                    'AVBR-AVDL':'inh',

                    'AVDL-PVCL':'exc',
                    'AVDL-AVAL':'exc',
                    'AVDL-AVAR':'exc',
                    'AVDL-AVDR':'exc',
                    'AVDR-PVCR':'exc',
                    'AVDR-AVAL':'exc',
                    'AVDR-AVAR':'exc',
                    'AVDR-AVBL':'exc',
                    'AVDR-AVDL':'exc',
                 },
                 conn_number_override={
                    #'PVCL-AVDL':7*0.1,
                    #'PVCL-AVDR':11*0.1,
                    #'PVCR-AVDL':16*0.1,
                    #'PVCR-AVDR':6*0.1,

                    'PVCR-AVDR_GJ':2*0.01,
                    'AVDR-PVCR_GJ':2*0.01,

                    'PVCL-AVAL_GJ':5*0.01,
                    'AVAL-PVCL_GJ':5*0.01,
                    'PVCL-AVAR_GJ':10*0.01,
                    'AVAR-PVCL_GJ':10*0.01,
                    'PVCR-AVAL_GJ':15*0.01,
                    'AVAL-PVCR_GJ':15*0.01,
                    'PVCR-AVAR_GJ':22*0.01,
                    'AVAR-PVCR_GJ':22*0.01,

                    #'AVDL-AVAL':37*0.1,
                    #'AVDL-AVAR':37*0.1,
                    #'AVDR-AVAL':41*0.1,
                    #'AVDR-AVAR':52*0.1,

                    #'AVDL-AVAL_GJ':7*0.1,
                    #'AVAL-AVDL_GJ':7*0.1,
                    #'AVDL-AVAR_GJ':2*0.1,
                    #'AVAR-AVDL_GJ':2*0.1,
                    #'AVDR-AVAL_GJ':9*0.1,
                    #'AVAL-AVDR_GJ':9*0.1,
                    #'AVDR-AVAR_GJ':15*0.1,
                    #'AVAR-AVDR_GJ':15*0.1,


                    #'ALMR-AVDR_GJ':2*5,
                    #'AVDR-ALMR_GJ':2*5,

                    #'AVAR-AVBL_GJ':3*0.01,
                    #'AVBL-AVAR_GJ':3*0.01,

                    #'AVAR-AVAL_GJ':18*2,
                    #'AVAL-AVAR_GJ':18*2,


                    'PVDL-AVAR_GJ':4*0.01,
                    'AVAR-PVDL_GJ':4*0.01,
                    'PVDR-AVAL_GJ':6*0.01,
                    'AVAL-PVDR_GJ':6*0.01,
                 },
                 include_muscles=False,
                 duration=duration,
                 dt=dt,
                 validate=(parameter_set!='B'),
                 target_directory = target_directory,
                 data_reader=data_reader)

        stim_amplitude = "14pA"
        #stim_amplitude = "5.135697186048022pA"

        c302.add_new_input(nml_doc, "PLML", "100ms", "600ms", "14pA", params)
        c302.add_new_input(nml_doc, "PLMR", "100ms", "600ms", "14pA", params)

        c302.add_new_input(nml_doc, "AVM", "1000ms", "600ms", "14pA", params)
        
        nml_file = target_directory+'/'+reference+'.nml'
        writers.NeuroMLWriter.write(nml_doc, nml_file) # Write over network file written above...

        print("(Re)written network file to: "+nml_file)
             
    return cells, cells_to_stimulate, params, False
             
if __name__ == '__main__':
    
    parameter_set = sys.argv[1] if len(sys.argv)==2 else 'C2'
    
    setup(parameter_set, generate=True, data_reader="SpreadsheetDataReader")
