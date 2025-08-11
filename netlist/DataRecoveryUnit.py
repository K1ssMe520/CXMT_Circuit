from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory

class DataRecoveryUnit(SubCircuitFactory):
    NAME = 'DataRecoveryUnit'
    NODES = ('DataIn', 'RecoveredClk', 'RecoveredData', 'VDD', 'VSS')
  
    def __init__(self, nmos_width=0.5e-6, pmos_width=1e-6, channel_length=0.18e-6):
        super().__init__()
        # Define MOSFET models (level 1)
        self.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
        self.model('pmos_model', 'pmos', level=1, kp=40e-6, vto=-0.5)
        
        # Master latch (first stage)
        self.MOSFET('M1', 'Qm', 'RecoveredClk', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        self.MOSFET('M2', 'Qm_bar', 'RecoveredClk', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        self.MOSFET('M3', 'Qm', 'RecoveredClk', 'Node1', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        self.MOSFET('M4', 'Qm_bar', 'RecoveredClk', 'Node2', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        self.MOSFET('M5', 'Node1', 'Qm_bar', 'VSS', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        self.MOSFET('M6', 'Node2', 'Qm', 'VSS', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        self.MOSFET('M7', 'Node1', 'DataIn', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        self.MOSFET('M8', 'Node2', 'DataIn', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        
        # Slave latch (second stage)
        self.MOSFET('M9', 'RecoveredData', 'RecoveredClk_bar', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        self.MOSFET('M10', 'RecoveredData_bar', 'RecoveredClk_bar', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        self.MOSFET('M11', 'RecoveredData', 'RecoveredClk_bar', 'Node3', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        self.MOSFET('M12', 'RecoveredData_bar', 'RecoveredClk_bar', 'Node4', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        self.MOSFET('M13', 'Node3', 'RecoveredData_bar', 'VSS', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        self.MOSFET('M14', 'Node4', 'RecoveredData', 'VSS', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        self.MOSFET('M15', 'Node3', 'Qm', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        self.MOSFET('M16', 'Node4', 'Qm_bar', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        
        # Clock inverter
        self.MOSFET('M17', 'RecoveredClk_bar', 'RecoveredClk', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        self.MOSFET('M18', 'RecoveredClk_bar', 'RecoveredClk', 'VSS', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)