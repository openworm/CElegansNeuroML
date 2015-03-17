# The MIT License (MIT)
#
# Copyright (c) 2011, 2013 OpenWorm.
# http://openworm.org
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the MIT License
# which accompanies this distribution, and is available at
# http://opensource.org/licenses/MIT
#
# Contributors:
#      OpenWorm - http://openworm.org/people.html
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
# USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import with_statement
#import numpy as np
from matplotlib import pyplot
from pyelectro import analysis
import numpy as np

data_fname = "redacted_data.txt"
dt = 0.0002

#load the voltage:
file=open(data_fname)

#make voltage into a numpy array in mV:
v = np.array([float(i) for i in file.readlines()])*1000

t_init = 0.0
t_final = len(v)*dt

t = np.linspace(t_init,t_final,len(v))*1000

pyplot.plot(t,v)
pyplot.show()

analysis_var={'peak_delta':0.0,'baseline':5,'dvdt_threshold':0.0}

analysis_i=analysis.IClampAnalysis(v,t,analysis_var,
				      start_analysis=0,
				      end_analysis=5000,
				      smooth_data=True,
				      show_smoothed_data=True,
				      smoothing_window_len=33)

analysis_i.analyse()
print(analysis_i.analysis_results)
