'''

    Still under developemnt!!
    
    Subject to change without notice!!
    
'''

import os.path
import os
import sys
import time
#import multiprocessing
#import functools
#import logging
#import traceback

from collections import OrderedDict


# https://stackoverflow.com/questions/6126007/python-getting-a-traceback-from-a-multiprocessing-process
#import tblib.pickling_support
#tblib.pickling_support.install()

if not os.path.isfile('c302.py'):
    print('This script should be run from dir: CElegansNeuroML/CElegans/pythonScripts/c302')
    exit()
        
sys.path.append(".")

import C302Simulation
import pyneuroml.pynml

last_results = None



# https://stackoverflow.com/questions/6126007/python-getting-a-traceback-from-a-multiprocessing-process
"""class ExceptionWrapper(object):
    def __init__(self, ee):
        self.ee = ee
        __, __, self.tb = sys.exc_info()

    def re_raise(self):
        #python3:
        #raise self.ee.with_traceback(self.tb)
        #python2:
        raise self.ee, None, self.tb"""


class C302Controller():

    def __init__(self, 
                 ref, 
                 params, 
                 config,
                 sim_time=1000, 
                 dt=0.05,
                 data_reader="SpreadsheetDataReader",
                 config_package=None,
                 generate_dir = './', 
                 simulator='jNeuroML',
                 input_list=None,
                 pool=None,
                 job_server=None,
                 num_local_procesors_to_use=1,
                 conns_to_include=[],
                 conns_to_exclude=[],
                 param_overrides=None):
        
        self.ref = ref
        self.params = params
        self.config = config
        self.data_reader = data_reader
        self.config_package = config_package
        self.sim_time = sim_time
        self.dt = dt
        self.simulator = simulator
        self.generate_dir = generate_dir if generate_dir.endswith('/') else generate_dir+'/'
        self.input_list = input_list
        
        self.num_local_procesors_to_use = num_local_procesors_to_use
        
        if int(num_local_procesors_to_use) != num_local_procesors_to_use or \
            num_local_procesors_to_use < 1:
                raise Exception('Error with num_local_procesors_to_use = %s\nPlease use an integer value greater then 1.'%num_local_procesors_to_use)

        self.pool = pool
        self.job_server = job_server

        self.conns_to_include = conns_to_include
        self.conns_to_exclude = conns_to_exclude
        self.param_overrides = param_overrides

        self.traces = []

        self.count = 0

        self.total_runs = 0

    """def get_traces_from_job(self, vars):
        job_id, t, v = vars
        print "++++++++++++++++++++++++++++++++ %s" % job_id
        self.traces.append([t, v])"""

    def run(self,candidates,parameters):


        """
        Run simulation for each candidate
        
        This run method will loop through each candidate and run the simulation
        corresponding to it's parameter values. It will populate an array called
        traces with the resulting voltage traces for the simulation and return it.
        """

        traces = []
        start_time = time.time()

        
        #if self.num_local_procesors_to_use == 1:
        if not self.job_server:
            for candidate_i in range(len(candidates)):
                
                candidate = candidates[candidate_i]
                sim_var = dict(zip(parameters,candidate))
                if isinstance(parameters, dict):
                    # new version
                    i = 0
                    for k, v in parameters.iteritems():
                        sim_var[k] = {'value': candidate[i], 'unit': v["default_unit"]}
                        i = i + 1
                pyneuroml.pynml.print_comment_v('\n\n  - RUN %i (%i/%i); variables: %s\n'%(self.count,candidate_i+1,len(candidates),sim_var))
                self.count+=1
                t,v = self.run_individual(sim_var)
                traces.append([t,v])

        else:
            #import pp
            #ppservers = ()
            #job_server = pp.Server(self.num_local_procesors_to_use, ppservers=ppservers, secret="password")
            pyneuroml.pynml.print_comment_v('Running %i candidates across %i local processors'%(len(candidates),self.job_server.get_ncpus()))
            jobs = []

            #import multiprocessing
            #import signal

            #original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)

            #pool = multiprocessing.Pool(self.num_local_procesors_to_use)

            #signal.signal(signal.SIGINT, original_sigint_handler)

            tasks = []
            #import pp

            
            for candidate_i in range(len(candidates)):
                
                candidate = candidates[candidate_i]
                sim_var = dict(zip(parameters,candidate))

                if isinstance(parameters, dict):
                    # new version
                    i = 0
                    for k, v in parameters.iteritems():
                        sim_var[k] = {'value': candidate[i], 'unit': v["default_unit"]}
                        i = i + 1



                pyneuroml.pynml.print_comment_v('\n\n  - PARALLEL RUN %i (%i/%i curr candidates); variables: %s\n'%(self.count,candidate_i+1,len(candidates),sim_var))
                self.count+=1
                cand_dir = self.generate_dir+"/CANDIDATE_%s"%candidate_i
                if not os.path.exists(cand_dir):
                    os.mkdir(cand_dir)
                pyneuroml.pynml.print_comment_v('Running in %s'%cand_dir)

                self.total_runs += 1

                #job_id = "%s/%s_%s" % (candidate_i, len(candidates), self.total_runs)
                job_id = None

                vars = (sim_var,
                   self.ref,
                   self.params,
                   self.config,
                   self.config_package,
                   self.data_reader,
                   self.sim_time,
                   self.dt,
                   self.simulator,
                   cand_dir,
                   False,
                   self.input_list,
                   self.conns_to_include,
                   self.conns_to_exclude,
                   job_id,
                        self.param_overrides)

                job = self.job_server.submit(run_individual, vars, (), ("pyneuroml.pynml",'C302Simulation'))
                jobs.append(job)

                #tasks.append(vars)

            for job_i in range(len(jobs)):

                job = jobs[job_i]

                #if job is None or job() is None:
                #    print "             !!!!!!!!!!!!! JOB = NONE !!!!!!!!!!!!!!"
                #    #return None

                pyneuroml.pynml.print_comment_v("Checking job %i of %i current jobs"%(job_i,len(candidates)))

                t,v = job()

                if not t or not v:
                    print "             !!!!!!!!!!!!! JOB = NONE (t or v is None) !!!!!!!!!!!!!!"


                traces.append([t,v])
                
                #pyneuroml.pynml.print_comment_v("Obtained: %s"%result) 
                
            #job_server.destroy()

            """try:
                results = [self.pool.apply_async(run_individual_wrapper, args=task) for task in tasks]
                for idx, result in enumerate(results):
                    if isinstance(result, ExceptionWrapper):
                        result.re_raise()
                    pyneuroml.pynml.print_comment_v("Checking job %i of %i current jobs" % (idx, len(candidates)))
                    job_id, t, v = result.get(9999)  # Without the timeout this blocking call ignores all signals.
                    #print "##################### Execution of job %s has finished" % job_id
                    traces.append([t, v])
            except KeyboardInterrupt:
                print("Caught KeyboardInterrupt, terminating workers")
                self.pool.terminate()"""

            #else:
            #    #print("Normal termination")
            #    pool.close()
            #self.pool.join()


            #for task in tasks:
            #    pool.apply_async(run_individual, args=task, callback=self.get_traces_from_job)

            #pool.close()
            #pool.join()
                
            
        end_time = time.time()
        tot = (end_time-start_time)
        pyneuroml.pynml.print_comment_v('Ran %i candidates in %s seconds (~%ss per job)'%(len(candidates),tot,tot/len(candidates)))

        return traces

    def run_individual(self, sim_var, show=False):
        
        t, volts = run_individual(sim_var,
                   self.ref,
                   self.params,
                   self.config,
                   self.config_package,
                   self.data_reader,
                   self.sim_time,
                   self.dt,
                   self.simulator,
                   self.generate_dir,
                   show=show,
                   input_list=self.input_list,
                   conns_to_include=self.conns_to_include,
                   conns_to_exclude=self.conns_to_exclude,
                                  param_overrides=self.param_overrides)

        global last_results
        
        self.last_results = last_results
        
        return t, volts

    '''def _poolFunctionWrapper(self, function, arg):
        """Run function under the pool

        Wrapper around function to catch exceptions that don't inherit from
        Exception (which aren't caught by multiprocessing, so that you end
        up hitting the timeout).
        """
        try:
            return function(arg)
        except:
            cls, exc, tb = sys.exc_info()
            if issubclass(cls, Exception):
                raise  # No worries
            # Need to wrap the exception with something multiprocessing will recognise
            import traceback
            print "Unhandled exception %s (%s):\n%s" % (cls.__name__, exc, traceback.format_exc())
            raise Exception("Unhandled exception: %s (%s)" % (cls.__name__, exc))

    def _runPool(self, timeout, function, iterable):
        """Run the pool

        Wrapper around pool.map_async, to handle timeout.  This is required so as to
        trigger an immediate interrupt on the KeyboardInterrupt (Ctrl-C); see
        http://stackoverflow.com/questions/1408356/keyboard-interrupts-with-pythons-multiprocessing-pool

        Further wraps the function in _poolFunctionWrapper to catch exceptions
        that don't inherit from Exception.
        """
        return self.pool.map_async(functools.partial(self._poolFunctionWrapper, function), iterable).get(timeout)

    def myMap(self, function, iterable, timeout=9999):
        """Run the function on the iterable, optionally with multiprocessing"""
        if self.pool:
            mapFunc = functools.partial(self._runPool, timeout)
        else:
            mapFunc = map
        results = mapFunc(function, iterable)
        #if pool is not None:
        #    pool.close()
        #    pool.join()
        return results'''


"""def run_individual_wrapper(sim_var,
                           ref,
                           params,
                           config,
                           config_package,
                           data_reader,
                           sim_time,
                           dt,
                           simulator,
                           generate_dir,
                           show=False,
                           input_list=None,
                           conns_to_include=[],
                           conns_to_exclude=[],
                           job_id=None,
                           param_overrides=None):
    try:
        return run_individual(sim_var, ref, params, config, config_package, data_reader, sim_time, dt, simulator, generate_dir,
                           show,
                           input_list,
                           conns_to_include,
                           conns_to_exclude,
                           job_id,
                              param_overrides=param_overrides)
    except Exception as e:
        return ExceptionWrapper(e)"""


def run_individual(sim_var, 
                   ref,
                   params,
                   config,
                   config_package,
                   data_reader,
                   sim_time,
                   dt,
                   simulator,
                   generate_dir,
                   show=False,
                   input_list=None,
                   conns_to_include=[],
                   conns_to_exclude=[],
                   job_id=None,
                   param_overrides=None):
    """
    Run an individual simulation.

    The candidate data has been flattened into the sim_var dict. The
    sim_var dict contains parameter:value key value pairs, which are
    applied to the model before it is simulated.

    The simulation itself is carried out via the instantiation of a
    Simulation object (see Simulation class above).

    """
    global last_results

    sim = C302Simulation.C302Simulation(ref, 
                         params, 
                         config,
                         config_package=config_package,
                         data_reader=data_reader,
                         sim_time = sim_time, 
                         dt = dt,
                         input_list=input_list,
                         simulator = simulator, 
                         generate_dir = generate_dir,
                         conns_to_include=conns_to_include,
                         conns_to_exclude=conns_to_exclude,
                                        param_overrides=param_overrides)
                         
    for var_name, v in sim_var.iteritems():
        bp = sim.params.get_bioparameter(var_name)

        if bp is None:
            if isinstance(v, dict):
                unit = "" if not v['unit'] else " %s" % v['unit']
                print "Adding param %s = %s%s" % (var_name, v['value'], v['unit'])

                if '_mirrored' in var_name:
                    print "found mirrored var_name %s: %s" % (var_name, v['value'])
                    var_name = '_'.join(var_name.split('_')[:-1])

                    pattern = var_name.split('_')
                    pre = pattern[0]
                    pattern[0] = '%s'
                    post = pattern[2]
                    pattern[2] = '%s'
                    tmp_param = pattern[5]
                    pattern[5] = '%s'
                    pattern = '_'.join(pattern)

                    override_key1 = pattern % (pre, post, tmp_param)
                    override_key2 = pattern % (post, pre, tmp_param)

                    sim.params.add_bioparameter(override_key1, "%s%s" % (v['value'], unit), "C302Controller", "0")
                    sim.params.add_bioparameter(override_key2, "%s%s" % (v['value'], unit), "C302Controller", "0")

                else:
                    sim.params.add_bioparameter(var_name, "%s%s" % (v['value'], unit), "C302Controller", "0")
            else:
                raise Exception(
                    "Cannot add %s=%s.\nIt is only possible to add new parameters with a dict containing the value and the unit" % (var_name, v))
        else:
            if isinstance(v, dict):
                print("Changing param %s: %s -> %s" % (var_name, bp.value, v['value']))
                #bp.change_magnitude(v['value'])
                unit = "" if not v['unit'] else " %s" % v['unit']
                sim.params.set_bioparameter(var_name, "%s%s" % (v['value'], unit), "C302Controller", "0")
            else:
                print("Changing param %s: %s -> %s" % (var_name, bp.value, v))
                bp.change_magnitude(v)

    sim.go()
    
    global last_results
    last_results = sim.results

    if show:
        sim.show()

    if job_id:
        return job_id, sim.t, sim.volts
    return sim.t, sim.volts



if __name__ == '__main__':
    
    if len(sys.argv) == 2 and sys.argv[1] == '-net':
                
        cont = C302Controller('NetTest', 'B', 'Muscles')

        sim_vars = OrderedDict([('chem_exc_syn_gbase',0.01),
                  ('chem_exc_syn_decay',10),
                  ('chem_inh_syn_gbase',0.01),
                  ('chem_inh_syn_decay',40)])

        cont.run_individual(sim_vars, show=True)
        
    elif len(sys.argv) == 2 and sys.argv[1] == '-phar':
                
        cont = C302Controller('PharTest', 'B', 'Pharyngeal', generate_dir = 'temp')

        sim_vars = OrderedDict([('chem_exc_syn_gbase',0.01),
                  ('chem_exc_syn_decay',10),
                  ('chem_inh_syn_gbase',0.01),
                  ('chem_inh_syn_decay',40)])

        t, volts = cont.run_individual(sim_vars, show=True)
        print(volts.keys())
        
    elif len(sys.argv) == 2 and sys.argv[1] == '-imC0':
                
        cont = C302Controller('TestIClampMuscle', 'C0', 'IClampMuscle', generate_dir = 'temp')

        sim_vars = OrderedDict([])

        t, volts = cont.run_individual(sim_vars, show=True)
        print(volts.keys())
        
    else:
    
        cont = C302Controller('SimpleTest', 'C', 'IClamp')

        sim_vars = OrderedDict([('leak_cond_density', 0.05), 
                                ('k_slow_cond_density', 0.5), 
                                ('k_fast_cond_density', 0.05), 
                                ('ca_boyle_cond_density', 0.5), 
                                ('specific_capacitance', 1.05), 
                                ('leak_erev', -50), 
                                ('k_slow_erev', -60), 
                                ('k_fast_erev', -60), 
                                ('ca_boyle_erev', 40)])

        cont.run_individual(sim_vars, show=True)