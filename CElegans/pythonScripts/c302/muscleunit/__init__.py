"""A sciunit library for muscle_model projects"""

import matplotlib.pyplot as plt

def vm_plot(vm,title="Membrane potential vs time"):
    """Plot a neo AnalogSignal object representing a membrane potential (data values vs time)"""
    plt.plot(vm.times,vm)
    plt.xlabel('Time (s)')
    plt.ylabel('Vm (mV)')
    plt.title(title)
    plt.show()