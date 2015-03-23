'''

    Script to plot evolution of parameters in tuner

    Still under developemnt!!
    
    Subject to change without notice!!
    
'''
        
import matplotlib.pyplot as pylab


individuals_file_name = '../data/ga_individuals.csv'

individuals_file = open(individuals_file_name)


pylab.xlabel('Generation')

generations = []
generations_all = []
generations_offset = []

f = []
nrows = 3
ncols = 3
val_num = 9
population_total = 30

vals = {}
colours = {}
sizes = {}

for i in range(val_num):
    vals[i]=[]
    colours[i]=[]
    sizes[i]=[]

for line in individuals_file:
    main_info = line.split('[')[0]
    values = line.split('[')[1]
    generation = int(main_info.split(',')[0])
    individual = int(main_info.split(',')[1].strip())
    fitness = float(main_info.split(',')[2].strip())
    
    if individual == 0:
        generations.append(generation)
    generations_all.append(generation)
    generations_offset.append(generation+(individual/40.0))
    f.append(fitness)
    
    val_strings = values[:-2].split(',')

    for i in range(len(val_strings)):
        vals[i].append(float(val_strings[i].strip()))
        colours[i].append(individual)
        sizes[i].append((population_total-individual)*2)
    
for i in range(val_num):
    
    pylab.subplot(nrows, ncols, i)
    pylab.scatter(generations_offset, vals[i], s=sizes[i], c=colours[i], alpha=0.4)


fig = pylab.figure()
fig.canvas.set_window_title("Analysis of %s"%individuals_file_name)
  
pylab.scatter(generations_offset, f, alpha=0.5)

pylab.show()