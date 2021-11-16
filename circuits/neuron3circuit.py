#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 14 19:09:19 2021

@author: colin
"""

import matplotlib.pyplot as plt
import pandas as pd

from neuron import h, gui
from neuron.units import ms, mV
h.load_file('stdrun.hoc')

# Create generic cell class, but each cell records: its spike times, some membrane potential timeseries, and keep track of NetCons.

class Cell:
    def __init__(self, gid):
        self._gid = gid
        self._setup_morphology()
        self.all = self.soma.wholetree()
        self._setup_biophysics()
        h.define_shape()
        
        self._spike_detector = h.NetCon(self.soma(0.5)._ref_v, None, sec=self.soma)
        self.spike_times = h.Vector()
        self._spike_detector.record(self.spike_times)
        
        self._ncs = []
        
        self.soma_v = h.Vector().record(self.soma(0.5)._ref_v)

    def __repr__(self):
        return '{}[{}]'.format(self.name, self._gid)



class BallAndStick(Cell):
    name = 'BallAndStick'
    
    def _setup_morphology(self):
        self.soma = h.Section(name='soma', cell=self)
        self.dend = h.Section(name='dend', cell=self)
        self.axon = h.Section(name='axon', cell=self)
        self.dend.connect(self.soma)
        self.soma.connect(self.axon)
        self.soma.L = self.soma.diam = 12.6157
        self.dend.L = 200
        self.dend.diam = 1

    def _setup_biophysics(self):
        for sec in self.all:
            sec.Ra = 100    # Axial resistance in Ohm * cm
            sec.cm = 1      # Membrane capacitance in micro Farads / cm^2
        self.soma.insert('hh')                                          
        for seg in self.soma:
            seg.hh.gnabar = 0.12  # Sodium conductance in S/cm2
            seg.hh.gkbar = 0.036  # Potassium conductance in S/cm2
            seg.hh.gl = 0.0003    # Leak conductance in S/cm2
            seg.hh.el = -54.3     # Reversal potential in mV
        # Insert passive current in the dendrite
        self.dend.insert('pas')                 
        for seg in self.dend:
            seg.pas.g = 0.001  # Passive conductance in S/cm2
            seg.pas.e = -65    # Leak reversal potential mV
        self.axon.insert('hh')                                          
        for seg in self.axon:
            seg.hh.gnabar = 0.12  # Sodium conductance in S/cm2
            seg.hh.gkbar = 0.036  # Potassium conductance in S/cm2
            seg.hh.gl = 0.0003    # Leak conductance in S/cm2
            seg.hh.el = -54.3     # Reversal potential in mV

# Setup single neuron feedback circuit with third output neuron.

# A---< C---<
# v  ^
# \__B

neuronA = BallAndStick(0)
neuronB = BallAndStick(1)
neuronC = BallAndStick(2)

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
syn_inhibit_BA.e = 40 * mV
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


t = h.Vector().record(h._ref_t)
h.finitialize(-65 * mV)
h.continuerun(100)


# Plot shape data
def getNeuronShapes():
  xs, ys, zs, sectiontype = ([] for _ in range(4))

  for sec in h.allsec():
    # for (x, y, z, diam) in sec.psection()['morphology']['pt3d']:
    print(sec)
    for x, y, z, _ in sec.psection()['morphology']['pts3d']:
      sectiontype.append(str(sec).split(".")[1])
      print(f"\tCoordinates { x= }, { y= }, { z= }")
      xs.append(x)
      ys.append(y)
      zs.append(z)

  neuron_shape_data = {
    "x": xs,
    "y": ys,
    "z": zs,
    "sectiontype": sectiontype
  }

  return pd.DataFrame(neuron_shape_data, columns=[label for label in neuron_shape_data.keys()])

neuron_shape_df = getNeuronShapes()

import plotly.express as px
fig = px.scatter_3d(neuron_shape_df, x="x", y="y", z="z", color="sectiontype")
# fig.show()
# fig.write_html("./neurons_in_space.html")


# Plot membrane voltage data
neurons = [neuronA, neuronB, neuronC]

fig, axes = plt.subplots(1, len(neurons))

for some_neuron, ax in zip(neurons, axes):
  ax.plot(t, some_neuron.soma_v)
  ax.set_xlabel('t (ms)')
  ax.set_ylabel('v (mV)')
  ax.set_title(str(some_neuron))

plt.show()

# """
# plt.figure()
# for i, cell in enumerate(ring.cells):
#     plt.vlines(cell.spike_times, i + 0.5, i + 1.5)
# plt.show()

# plt.figure()
# for syn_w, color in [(0.01, 'black'), (0.005, 'red')]:
#     ring = Ring(N=5, syn_w=syn_w)
#     h.finitialize(-65 * mV)
#     h.continuerun(100 * ms)
#     for i, cell in enumerate(ring.cells):
#         plt.vlines(cell.spike_times, i + 0.5, i + 1.5, color=color)

# plt.show()
# """

