#!usr/bin/env python

from neuron import h, gui
from neuron.units import ms, mV
h.load_file('stdrun.hoc')

import matplotlib.pyplot as plt

from neurons.simpleneuron import SimpleNeuron

# Initialize cells
neuronA = SimpleNeuron(0, soma_diameter=15, axon_length=200)
neuronB = SimpleNeuron(1, soma_diameter=15, axon_length=500)

#
#  A---< B---<
#

# Add stimulus current to neuronA
iclamp = h.IClamp(neuronA.soma(0.5))
iclamp.delay = 2
iclamp.dur = 0.1 * ms
iclamp.amp = 2

# Add excitatory synapses from neuronA axon end -> neuronB soma 
syn_excite = h.ExpSyn(neuronB.soma(0.5))
syn_excite.e = -120 * mV
syn_excite.tau = 2

network_connection_AB = h.NetCon(neuronA.axon(1)._ref_v, syn_excite, sec=neuronA.axon)
network_connection_AB.delay = 1 * ms
network_connection_AB.weight[0] = 0.04

# Initialize recording vectors
things_to_record = [
    neuronA.soma(0.5)._ref_v,
    neuronA.axon(1)._ref_v,
    neuronB.soma(0.5)._ref_v
]

recordings = [h.Vector().record(thing) for thing in things_to_record]
t = h.Vector().record(h._ref_t)                     # Time stamp vector

# Experimental Manipulations
h.finitialize(-65 * mV)
h.continuerun(40 * ms)

fig, ax = plt.subplots(1,1)
for recording in recordings:
    ax.plot(t, recording)
plt.show()