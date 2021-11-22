#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 14 19:09:19 2021
Modified on Tues Nov 16 2021

@author: colin
@author: alex
"""

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px

from neuron import h, gui
from neuron.units import ms, mV
h.load_file('stdrun.hoc')

from neurons.ballandstick import BallAndStick

# Setup single neuron feedback circuit with third output neuron.

# A---< C---<
# v  ^
# \__B

neuronA = BallAndStick('neuronA')
neuronB = BallAndStick('neuronB')
neuronC = BallAndStick('neuronC')

# Add stimulus current to neuronA soma.
iclamp = h.IClamp(neuronA.soma(0.5))
iclamp.delay = 10
iclamp.dur = 80 * ms
iclamp.amp = 10

# Add excitatory synapses from neuronA to neuronB.
syn_excite_AB = h.ExpSyn(neuronB.soma(0.5))
syn_excite_AB.e = 40 * mV
syn_excite_AB.tau = 2

# Add inhibitory synapses from neuronB to neuronA.
syn_inhibit_BA = h.ExpSyn(neuronA.soma(0.5))
syn_inhibit_BA.e = -65 * mV
syn_inhibit_BA.tau = 2

# Add excitatory synapses from neuronA to neuronC.
syn_excite_AC = h.ExpSyn(neuronC.soma(0.5))
syn_excite_AC.e = 40 * mV
syn_excite_AC.tau = 2

# Netcon neuronA to neuronB.
netcon_AB = h.NetCon(neuronA.axon(1)._ref_v, syn_excite_AB, sec=neuronA.axon)
netcon_AB.delay = 1 * ms
netcon_AB.weight[0] = 0.4

# Netcon neuronB to neuronA.
netcon_BA = h.NetCon(neuronB.axon(1)._ref_v, syn_inhibit_BA, sec=neuronB.axon)
netcon_BA.delay = 1 * ms
netcon_BA.weight[0] = 0.04

# Netcon neuronA to neuronC.
netcon_AC = h.NetCon(neuronA.axon(1)._ref_v, syn_excite_AC, sec=neuronA.axon)
netcon_AC.delay = 1 * ms
netcon_AC.weight[0] = 0.4

# Run simulation
t = h.Vector().record(h._ref_t)
h.finitialize(-65 * mV)
h.continuerun(100)

# Plot cells in space
def get_all_neuron_morphology_df(neurons: list) -> pd.DataFrame:
  all_morphology = {"x": [], "y": [], "z": [], "sectiontype": []}
  for some_neuron in neurons:
    morphology_pts = some_neuron.get_morphology_pts()
    for sectiontype in morphology_pts.keys():
      for axis in morphology_pts[sectiontype].keys():
        all_morphology[axis] += morphology_pts[sectiontype][axis]
        all_morphology["sectiontype"].append(sectiontype)
  return pd.DataFrame(all_morphology, columns=[label for label in all_morphology.keys()])

neurons = [neuronA, neuronB, neuronC]

neuron_morphology_df = get_all_neuron_morphology_df(neurons)

fig = px.scatter_3d(neuron_morphology_df,
  x='x',
  y='y',
  z='z',
  color='sectiontype')
# fig.show()

# Plot membrane voltage data
fig, axes = plt.subplots(1, len(neurons))

for some_neuron, ax in zip(neurons, axes):
  ax.plot(t, some_neuron.soma_v)
  ax.set_xlabel('t (ms)')
  ax.set_ylabel('v (mV)')
  ax.set_title(some_neuron._gid)

plt.show()
