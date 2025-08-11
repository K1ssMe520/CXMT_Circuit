from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory

class SampleAndHold(SubCircuitFactory):
    NAME = 'SampleAndHold'
    NODES = ('Vin', 'Clk', 'Vsh')
  
    def __init__(self, nmos_width=0.5e-6, pmos_width=1e-6, channel_length=0.18e-6, hold_capacitance=10e-12):
        super().__init__()
        # Define MOSFET models (level 1)
        self.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
        self.model('pmos_model', 'pmos', level=1, kp=40e-6, vto=-0.5)
        
        # Sampling switch (transmission gate)
        self.MOSFET('M1', 'Vsh', 'Clk', 'Vin', 'Vin', model='nmos_model', w=nmos_width, l=channel_length)
        self.MOSFET('M2', 'Vsh', 'Clk_bar', 'Vin', 'Vin', model='pmos_model', w=pmos_width, l=channel_length)
        
        # Inverter for complementary clock generation
        self.MOSFET('M3', 'Clk_bar', 'Clk', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        self.MOSFET('M4', 'Clk_bar', 'Clk', 'VSS', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        
        # Hold capacitor
        self.C('C1', 'Vsh', 'VSS', hold_capacitance)
        
        # Power supply nodes (internal)
        self.V('VDD', 'VDD', 'VSS', 1.8@u_V)
        self.V('VSS', 'VSS', 'GND', 0@u_V)