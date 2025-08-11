from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory

class CDAC(SubCircuitFactory):
    NAME = 'CDAC'
    NODES = ('Vrefp', 'Vrefn', 'Vdac', 'DacCtrl0', 'DacCtrl1', 'DacCtrl2', 'DacCtrl3')
  
    def __init__(self, unit_capacitance=1e-15):
        super().__init__()
        
        # Binary-weighted capacitors (4-bit example)
        self.C('C0', 'Vdac', 'DacCtrl0', unit_capacitance)
        self.C('C1', 'Vdac', 'DacCtrl1', 2*unit_capacitance)
        self.C('C2', 'Vdac', 'DacCtrl2', 4*unit_capacitance)
        self.C('C3', 'Vdac', 'DacCtrl3', 8*unit_capacitance)
        
        # Reference capacitor (always connected to Vrefn)
        self.C('Cref', 'Vdac', 'Vrefn', unit_capacitance)
        
        # Reset switch (implemented as MOSFET)
        self.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
        self.MOSFET('Mreset', 'Vdac', 'Reset', 'Vrefn', 'Vrefn', 
                   model='nmos_model', w=1e-6, l=0.18e-6)