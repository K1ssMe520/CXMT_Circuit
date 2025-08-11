from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory

class DiffInputStage(SubCircuitFactory):
    NAME = 'DiffInputStage'
    NODES = ('Vinp', 'Vinn', 'Vbias3', 'Vbias1', 'Vout_int', 'VDD', 'VSS')
  
    def __init__(self, nmos_width=0.5e-6, pmos_width=1e-6, channel_length=0.18e-6, tail_current=100e-6):
        super().__init__()
        # Define MOSFET models (level 1)
        self.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
        self.model('pmos_model', 'pmos', level=1, kp=40e-6, vto=-0.5)
    
        # Differential pair
        self.MOSFET('M1', 'Node1', 'Vinp', 'Node3', 'Node3', model='nmos_model', w=nmos_width, l=channel_length)
        self.MOSFET('M2', 'Node2', 'Vinn', 'Node3', 'Node3', model='nmos_model', w=nmos_width, l=channel_length)
        
        # Tail current source
        self.MOSFET('M3', 'Node3', 'Vbias3', 'VSS', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        
        # Active load (current mirror)
        self.MOSFET('M4', 'Node1', 'Vbias1', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        self.MOSFET('M5', 'Node2', 'Vbias1', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        
        # Output stage (converts differential to single-ended)
        self.MOSFET('M6', 'Vout_int', 'Node2', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)