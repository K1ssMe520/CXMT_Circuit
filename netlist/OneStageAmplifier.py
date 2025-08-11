from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory

class OneStageAmplifier(SubCircuitFactory):
    NAME = 'OneStageAmplifier'
    NODES = ('Vin', 'Vbias', 'Vout', 'VDD', 'GND')
  
    def __init__(self, nmos_width=50e-6, nmos_length=1e-6, load_resistance=10e3, 
                 input_capacitance=1e-12, output_capacitance=1e-12):
        super().__init__()
        # Define MOSFET model (level 1)
        self.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
    
        # Topology
        self.MOSFET('M1', 'Vout', 'Vbias', 'GND', 'GND', model='nmos_model', w=nmos_width, l=nmos_length)
        self.R('R1', 'VDD', 'Vout', load_resistance)
        
        # Coupling capacitors
        if input_capacitance > 0:
            self.C('C1', 'Vin', 'Vbias', input_capacitance)
        if output_capacitance > 0:
            self.C('C2', 'Vout', 'GND', output_capacitance)