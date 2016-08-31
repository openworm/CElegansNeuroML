import matplotlib.pyplot
import time
import numpy, scipy
import sys
from scipy.signal import correlate
from pyelectro import analysis

import scipy.stats
import numpy as np
import math
import logging
from scipy import interpolate
import operator


class Data_Analyser(analysis.NetworkAnalysis):

	def __init__(self, 
				volts,
				t,
				analysis_var,
				start_analysis,
				end_analysis ):

		super(Data_Analyser, self).__init__(volts, 
						t, 
						analysis_var,
						start_analysis, 
						end_analysis)

		self.volts = volts
		self.t = t

	def analyse_phase_offset(self,targets, analysis_results):

		for key in targets.keys():

			time_shift = self.get_time_shift(self.volts[key.split(";")[0]], self.volts[key.split(";")[1]], self.t)
			
			if analysis_results [key.split(";")[0] + ":max_peak_no"] > 0:
				num_peaks = analysis_results [key.split(";")[0] + ":max_peak_no"]
			elif analysis_results [key.split(";")[1] + ":max_peak_no"] > 0:
				num_peaks = analysis_results [key.split(";")[1] + ":max_peak_no"]
			else:
				num_peaks = 1

			period = max(self.t) / num_peaks
			
			offset = 2*scipy.pi*(((0.5 + time_shift/period) %1.0) -0.5) #in terms of radians
			offset =  offset*180/scipy.pi #in terms of degrees

			analysis_results [key] = (180 - offset) if offset < 0 else offset

		return analysis_results

	def get_time_shift(self, volts1, volts2, t):

		volts1 -= numpy.mean(volts1); volts1 /= numpy.std(volts1)
		volts2 -= numpy.mean(volts2); volts2 /= numpy.std(volts2)

		xcorr =correlate(volts1, volts2)
		dt = numpy.linspace(-t[-1], t[-1], 2*len(t)-1)
		return dt[xcorr.argmax()]

	'''
	Builds on analysis from pyElectro: includes phase offset target
	targets: the standard targets to evaluate (min_peak_no, minimum, spike_broadening, etc). If None, evaluate all 
	extra_targets: used if targets==None for specifying additional targets, e.g. cell0:value_100
	'''
	def analyse(self, targets=None, extra_targets=None):
	    """ Analyses and puts all results into a dict"""  

	    phase_targets = None  

	    if targets and any("phase_offset" in s for s in targets.keys()):

	    	phase_targets = {}
	    	tempTargets = {}

	    	for key in targets.keys():

	    		if "phase_offset" in key:

	    			phase_targets[key] = targets[key]
		    		tempTargets[key.split(";")[0] + ":max_peak_no"] = targets[key]
		    		tempTargets[key.split(";")[1]+ ":max_peak_no"] = targets[key]
		    	
		    	else:

		    		tempTargets[key] = targets[key]

	    	targets = tempTargets


	    analysis_results = {}
	    
	    analysis_results = super(Data_Analyser, self).analyse(targets)

	    if(phase_targets != None):  

	    	analysis_results = self.analyse_phase_offset(phase_targets, analysis_results)
	            
	    self.analysis_results=analysis_results

	    return self.analysis_results

