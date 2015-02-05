from c302 import generate
import sys
import random

if __name__ == '__main__':
    
    parameter_set = sys.argv[1] if len(sys.argv)==2 else 'A'
    exec('from parameters_%s import ParameterisedModel'%parameter_set)
    params = ParameterisedModel()
    
    # Any neurons connected to muscles
    
    cells = ['AS1', 'AS10', 'AS11', 'AS2', 'AS3', 'AS4', 'AS5', 'AS6', 'AS7', 'AS8', 'AS9', 
             'AVFL', 'AVFR', 'AVKR', 'AVL', 
             'CEPVL', 'CEPVR', 
             'DA1', 'DA2', 'DA3', 'DA4', 'DA5', 'DA6', 'DA7', 'DA8', 'DA9', 
             'DB1', 'DB2', 'DB3', 'DB4', 'DB5', 'DB6', 'DB7', 
             'DD1', 'DD2', 'DD3', 'DD4', 'DD5', 'DD6', 
             'DVB', 
             'HSNL', 'HSNR', 
             'IL1DL', 'IL1DR', 'IL1L', 'IL1R', 'IL1VL', 'IL1VR', 
             'PDA', 'PDB', 
             'PVNL', 'PVNR', 
             'RID', 'RIML', 'RIMR', 'RIVL', 'RIVR', 
             'RMDDL', 'RMDDR', 'RMDL', 'RMDR', 'RMDVL', 'RMDVR', 'RMED', 'RMEL', 'RMER', 'RMEV', 'RMFL', 'RMGL', 'RMGR', 'RMHL', 'RMHR', 
             'SMBDL', 'SMBDR', 'SMBVL', 'SMBVR', 'SMDDL', 'SMDDR', 'SMDVL', 'SMDVR', 
             'URADL', 'URADR', 'URAVL', 'URAVR', 
             'VA1', 'VA10', 'VA11', 'VA12', 'VA2', 'VA3', 'VA4', 'VA5', 'VA6', 'VA7', 'VA8', 'VA9', 
             'VB1', 'VB10', 'VB11', 'VB2', 'VB3', 'VB4', 'VB5', 'VB6', 'VB7', 'VB8', 'VB9', 
             'VC1', 'VC2', 'VC3', 'VC4', 'VC5', 'VC6', 
             'VD1', 'VD10', 'VD11', 'VD12', 'VD13', 'VD2', 'VD3', 'VD4', 'VD5', 'VD6', 'VD7', 'VD8', 'VD9']
    cells+=['AVBL', 'AVBR','PVCL', 'PVCR']
    #cells=[]         
    
    # Some random set of neurons
    probability = 0.1
    cells_to_stimulate = []
    for cell in cells:
        #if random.random()<probability:
        #    cells_to_stimulate.append(cell)
        if cell.startswith("xxVB") or cell.startswith("DB"):
            cells_to_stimulate.append(cell)
    #cells_to_stimulate = ['DB1', 'VB1']
    cells_to_stimulate = ['PVCL', 'PVCR',  'VB1', 'VB2', 'VB3']
    
    # Plot some directly stimulated & some not stimulated
    cells_to_plot      = ['AS1', 'AS10', 'AVFL', 'DA1','DB1','DB4','DB7','IL1DL','RID', 'RIML','SMBDL', 'SMBDR', 'VB1', 'VB5', 'VB10','VC1', 'VC2']
    cells_to_plot      = ['AVBL', 'AVBR','PVCL', 'PVCR', 'DB1','DB2','VB1','VB2','DD1','DD2','VD1','VD2']
    
    reference = "c302_%s_Muscles"%parameter_set
    
    generate(reference, 
             params, 
             cells=cells,
             cells_to_plot=cells_to_plot, 
             cells_to_stimulate=cells_to_stimulate, 
             include_muscles = True,
             duration=500, 
             dt=0.1, 
             vmin=-52, 
             vmax=-28, 
             validate=(parameter_set!='B'))    
