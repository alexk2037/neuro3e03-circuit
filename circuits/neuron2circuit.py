#!usr/bin/env python

from neuron import h, gui
from neuron.units import ms, mV
h.load_file('stdrun.hoc')

import matplotlib.pyplot as plt

from neurons.simpleneuron import SimpleNeuron

# Initialize cells
neuronA = SimpleNeuron(gid=0, soma_diameter=15, axon_length=200)
neuronB = SimpleNeuron(gid=1, soma_diameter=15, axon_length=500)

#
#  A---< B---<
#

# Add stimulus current to neuronA soma
iclamp = h.IClamp(neuronA.soma(0.5))
iclamp.delay = 2
iclamp.dur = 0.1 * ms
iclamp.amp = 2

# Add excitatory synapses from neuronA axon end -> neuronB soma 
syn_excite = h.ExpSyn(neuronB.soma(0.5))
syn_excite.e = -120 * mV
syn_excite.tau = 2

# netcon = network connection
netcon_AB = h.NetCon(neuronA.axon(1)._ref_v, syn_excite, sec=neuronA.axon)
netcon_AB.delay = 1 * ms
netcon_AB.weight[0] = 0.04

# Initalize recording vectors
locations_to_record = [
    neuronA.soma(0.5),
    neuronA.axon(1),
    neuronB.soma(0.5)
]

v_recordings = [h.Vector().record(thing._ref_v) for thing in locations_to_record] # Voltage recording vectors
t = h.Vector().record(h._ref_t) # Time stamp vector

# Run experiment
h.finitialize(-65 * mV)
h.continuerun(40 * ms)

# Plot results
fig, axes = plt.subplots(1,3)
fig.suptitle('Membrane Potential (mV) vs Time (ms)')
for recording, axis, location in zip(v_recordings, axes, locations_to_record):
    axis.plot(t, recording)
    axis.set_title(str(location))
plt.show()