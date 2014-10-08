from c302 import generate
import sys

if __name__ == '__main__':
    
    parameter_set = sys.argv[1] if len(sys.argv)==2 else 'A'
    
    exec('import parameters_%s as params'%parameter_set)
    
    cells = ["ADAL", "AIBL", "RIVR", "RMEV"]
    cells_to_stimulate      = ["ADAL", "RIVR"]
    
    reference = "c302_%s_Syns"%parameter_set
    
    generate(reference, params, cells=cells, cells_to_stimulate=cells_to_stimulate, duration=500, dt=0.1, vmin=-72, vmax=-48)