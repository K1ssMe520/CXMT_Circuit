from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory

class VoltageControlledOscillator(SubCircuitFactory):
    NAME = 'VoltageControlledOscillator'
    NODES = ('Vctrl', 'Vctrl_Init', 'RecoveredClk', 'VDD', 'VSS')
    
    def __init__(self, nmos_width=0.5e-6, pmos_width=1e-6, channel_length=0.18e-6, 
                 ring_stages=3, load_capacitance=10e-15):
        super().__init__()
        # Define MOSFET models (level 1)
        self.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
        self.model('pmos_model', 'pmos', level=1, kp=40e-6, vto=-0.5)
        
        # Current mirror for bias generation
        self.MOSFET('M1', 'Bias', 'Bias', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        self.MOSFET('M2', 'Bias', 'Vctrl', 'VSS', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        
        # Startup circuit using initial control voltage
        self.MOSFET('M3', 'Bias', 'Vctrl_Init', 'VSS', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        
        # Ring oscillator with voltage-controlled delay
        previous_node = 'RecoveredClk'
        for i in range(ring_stages):
            current_node = f'Node{i}'
            next_node = f'Node{i+1}' if i < ring_stages-1 else 'RecoveredClk'
            
            # Inverter stage with current-starved configuration
            self.MOSFET(f'M_p{i}', current_node, previous_node, 'VDD', 'VDD', 
                        model='pmos_model', w=pmos_width, l=channel_length)
            self.MOSFET(f'M_n{i}a', current_node, previous_node, 'Starve{i}', 'VSS', 
                        model='nmos_model', w=nmos_width, l=channel_length)
            self.MOSFET(f'M_n{i}b', 'Starve{i}', 'Bias', 'VSS', 'VSS', 
                        model='nmos_model', w=nmos_width, l=channel_length)
            
            previous_node = current_node
        
        # Output buffer
        self.MOSFET('M_outp', 'RecoveredClk', previous_node, 'VDD', 'VDD', 
                    model='pmos_model', w=pmos_width*2, l=channel_length)
        self.MOSFET('M_outn', 'RecoveredClk', previous_node, 'VSS', 'VSS', 
                    model='nmos_model', w=nmos_width*2, l=channel_length)
        
        # Optional load capacitor
        if load_capacitance > 0:
            self.C('C1', 'RecoveredClk', 'VSS', load_capacitance)