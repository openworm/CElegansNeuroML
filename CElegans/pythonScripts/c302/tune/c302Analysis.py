from scipy.signal import correlate
from pyelectro import analysis

import scipy.stats
import numpy


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
	
	'''
	This method (analyse_phase_offset) contains code sourced from the following response post:

	deprecated (https://stackoverflow.com/users/353062/deprecated), Find phase difference between two (inharmonic) waves, URL (version: 2020-04-15): https://stackoverflow.com/a/6157997

	Explicitly:

	https://stackoverflow.com/a/6157997 by ‘deprecated’ https://stackoverflow.com/users/353062/deprecated (last edited May 31 '11 at 16:16) in Stack Overflow in response to the question https://stackoverflow.com/q/6157791 posted by Doa https://stackoverflow.com/users/773761/doa

	The code used in this method (analyse_phase_offset) that has been sourced from https://stackoverflow.com/a/6157997 has been modified by the renaming of the variables to names that are more specific for the project.  Any modifications (e.g. remix, transform) or code built upon in this method (analyse_phase_offset) of code from https://stackoverflow.com/a/6157997 are under the same licence of Stack Overflow user contributions (CC BY-SA 4.0, https://creativecommons.org/licenses/by-sa/4.0/; previously CC BY-SA 3.0, https://creativecommons.org/licenses/by-sa/3.0/)

	The additional functionality in the method includes data extraction in the format used by this project, and to prepare the data so the data can be used by the code from  https://stackoverflow.com/a/6157997.
	'''
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

	'''
	This method (get_time_shift) contains code sourced from the following response post

	deprecated (https://stackoverflow.com/users/353062/deprecated), Find phase difference between two (inharmonic) waves, URL (version: 2020-04-15): https://stackoverflow.com/a/6157997

	Explicitly:

	https://stackoverflow.com/a/6157997 by ‘deprecated’ https://stackoverflow.com/users/353062/deprecated (last edited May 31 '11 at 16:16) in Stack Overflow in response to the question https://stackoverflow.com/q/6157791 posted by Doa https://stackoverflow.com/users/773761/doa

	The code used in this method (get_time_shift) that has been sourced https://stackoverflow.com/a/6157997 has been modified by the renaming of the variables to names that are more specific for the project.  Any modifications (e.g. remix, transform) or code built upon in this method (get_time_shift) of code from https://stackoverflow.com/a/6157997 are under the same licence of Stack Overflow user contributions (CC BY-SA 4.0, https://creativecommons.org/licenses/by-sa/4.0/; previously CC BY-SA 3.0, https://creativecommons.org/licenses/by-sa/3.0/)
	'''	
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

