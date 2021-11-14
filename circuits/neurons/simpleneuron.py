#!usr/bin/env python

from neuron import h, gui
from neuron.units import ms, mV

class SimpleNeuron:
  """A neuron with a soma, an axon, and Hodgkin-Huxley ion channels"""

  def __init__(self, gid: int, soma_diameter: float, axon_length: float):
    self._gid = gid
    self.name = "SimpleNeuron"
    self._setup_morphology(soma_diameter, axon_length)
    self._setup_biophysics()
    h.define_shape()

  def __repr__(self):
    return f"{self.name}[{self._gid}]"

  def _setup_morphology(self, soma_diameter: float, axon_length: float):
    self.soma = h.Section(name='soma', cell=self)
    self.axon = h.Section(name='axon', cell=self)
    self.axon.connect(self.soma)
    self.soma.L = self.soma.diam = soma_diameter
    self.axon.L = axon_length
    self.axon.diam = 1

  def _setup_biophysics(self):
    self.soma.insert('hh')

    # for sec in self.soma.wholetree():
    #   sec.Ra = 35.4   # Axial resistance in Ohm * cm
    #   sec.cm = 1      # Membrane capacitance in micro Farads / cm^2
    
    # for seg in self.soma:
    #   seg.hh.gnabar = 0.12  # Sodium conductance in S/cm2
    #   seg.hh.gkbar = 0.036  # Potassium conductance in S/cm2
    #   seg.hh.gl = 0.0003    # Leak conductance in S/cm2
    #   seg.hh.el = -54.3     # Reversal potential in mV

