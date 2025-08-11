from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory

class PhaseDetector(SubCircuitFactory):
    NAME = 'PhaseDetector'
    NODES = ('DataIn', 'RecoveredClk', 'PhaseError', 'VDD', 'VSS')
  
    def __init__(self, nmos_width=0.5e-6, pmos_width=1e-6, channel_length=0.18e-6, filter_capacitance=10e-15):
        super().__init__()
        # Define MOSFET models (level 1)
        self.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
        self.model('pmos_model', 'pmos', level=1, kp=40e-6, vto=-0.5)
    
        # Phase detector core - D flip-flop implementation
        # Upper PMOS transistors
        self.MOSFET('M1', 'Q', 'RecoveredClk', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        self.MOSFET('M2', 'Qbar', 'RecoveredClk', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        
        # Lower NMOS transistors
        self.MOSFET('M3', 'Q', 'RecoveredClk', 'Node1', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        self.MOSFET('M4', 'Qbar', 'RecoveredClk', 'Node2', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        self.MOSFET('M5', 'Node1', 'Qbar', 'VSS', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        self.MOSFET('M6', 'Node2', 'Q', 'VSS', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        
        # Data input stage
        self.MOSFET('M7', 'Node1', 'DataIn', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        self.MOSFET('M8', 'Node2', 'DataIn', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        
        # Output stage (charge pump)
        self.MOSFET('M9', 'PhaseError', 'Q', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        self.MOSFET('M10', 'PhaseError', 'Qbar', 'VSS', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        
        # Optional filter capacitor
        if filter_capacitance > 0:
            self.C('C1', 'PhaseError', 'VSS', filter_capacitance)