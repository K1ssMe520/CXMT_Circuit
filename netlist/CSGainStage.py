from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory

class CSGainStage(SubCircuitFactory):
    NAME = 'CSGainStage'
    NODES = ('Vin_int', 'Vbias2', 'Vout', 'VDD', 'VSS')
    
    def __init__(self, nmos_width=1e-6, pmos_width=2e-6, channel_length=0.18e-6, load_capacitance=10e-15):
        super().__init__()
        # Define MOSFET models (level 1)
        self.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
        self.model('pmos_model', 'pmos', level=1, kp=40e-6, vto=-0.5)
        
        # Common-source amplifier transistor
        self.MOSFET('M1', 'Vout', 'Vin_int', 'VSS', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        
        # Active load (PMOS current source)
        self.MOSFET('M2', 'Vout', 'Vbias2', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        
        # Optional load capacitor
        if load_capacitance > 0:
            self.C('C1', 'Vout', 'VSS', load_capacitance)