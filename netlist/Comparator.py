from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory

class Comparator(SubCircuitFactory):
    NAME = 'Comparator'
    NODES = ('Vsh', 'Vdac', 'CmpOut')
  
    def __init__(self, nmos_width=0.5e-6, pmos_width=1e-6, channel_length=0.18e-6, load_capacitance=10e-15):
        super().__init__()
        # Define MOSFET models (level 1)
        self.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
        self.model('pmos_model', 'pmos', level=1, kp=40e-6, vto=-0.5)
        
        # Differential pair input stage
        self.MOSFET('M1', 'Node1', 'Vsh', 'Tail', 'Tail', model='nmos_model', w=nmos_width, l=channel_length)
        self.MOSFET('M2', 'Node2', 'Vdac', 'Tail', 'Tail', model='nmos_model', w=nmos_width, l=channel_length)
        self.MOSFET('M3', 'Tail', 'Bias', 'VSS', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        
        # Active load (current mirror)
        self.MOSFET('M4', 'Node1', 'Node1', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        self.MOSFET('M5', 'Node2', 'Node1', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        
        # Output stage (inverter)
        self.MOSFET('M6', 'CmpOut', 'Node2', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        self.MOSFET('M7', 'CmpOut', 'Node2', 'VSS', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        
        # Bias voltage (fixed at midpoint)
        self.V('Bias', 'Bias', 'VSS', 0.9@u_V)  # Assuming VDD=1.8V
        
        # Power supply connections
        self.V('VDD', 'VDD', 'VSS', 1.8@u_V)
        
        # Optional load capacitor
        if load_capacitance > 0:
            self.C('C1', 'CmpOut', 'VSS', load_capacitance)