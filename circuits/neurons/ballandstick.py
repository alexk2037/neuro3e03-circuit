from neuron import h
from neurons.cell import Cell
import numpy as np

class BallAndStick(Cell):
  """Create generic cell class, but each cell records 
  - its spike times, 
  - some membrane potential timeseries, 
  - and keeps track of NetCons.
  """

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

  def get_morphology_pts(self) -> dict:
    """Each section is defined by three 3D cartesian points"""
    morphology_pts = {}
    for section in self.all:
      section_key = str(section).split(".")[1]
      pts_matrix = np.array([[x, y, z] for x, y, z, _ in section.psection()['morphology']['pts3d']]).T
      pts_3d = {k:list(v) for k, v in zip(("x", "y", "z"), pts_matrix)}
      morphology_pts[section_key] = pts_3d
    return morphology_pts

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

