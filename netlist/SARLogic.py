from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory

class SARLogic(SubCircuitFactory):
    NAME = 'SARLogic'
    NODES = ('Clk', 'Start', 'CmpOut', 
             'Dout0', 'Dout1', 'Dout2', 'Dout3',
             'EOC', 'DacCtrl0', 'DacCtrl1', 'DacCtrl2', 'DacCtrl3',
             'VDD', 'VSS')
  
    def __init__(self, nmos_width=0.5e-6, pmos_width=1e-6, channel_length=0.18e-6):
        super().__init__()
        # Define MOSFET models (level 1)
        self.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
        self.model('pmos_model', 'pmos', level=1, kp=40e-6, vto=-0.5)
        
        # Internal nodes for the SAR logic
        self.node('Q0', 'Q1', 'Q2', 'Q3')  # Internal flip-flop outputs
        self.node('State0', 'State1', 'State2', 'State3')  # State machine nodes
        
        # Clocked D flip-flops for the SAR register
        for i in range(4):
            # Transmission gate implementation of DFF
            # Clock phase
            self.MOSFET(f'M{i}_1', f'Q{i}_int', 'Clk', f'Q{i}', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
            self.MOSFET(f'M{i}_2', f'Q{i}_int', 'Clk', f'Q{i}', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
            
            # Data input (from comparator or previous stage)
            input_node = 'CmpOut' if i == 0 else f'Q{i-1}'
            self.MOSFET(f'M{i}_3', f'Q{i}', 'State{i}', input_node, 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
            self.MOSFET(f'M{i}_4', f'Q{i}', 'State{i}', input_node, 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
            
            # Output buffers
            self.MOSFET(f'M{i}_5', f'Dout{i}', f'Q{i}', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
            self.MOSFET(f'M{i}_6', f'Dout{i}', f'Q{i}', 'VSS', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
            
            # DAC control signals
            self.MOSFET(f'M{i}_7', f'DacCtrl{i}', f'Q{i}', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
            self.MOSFET(f'M{i}_8', f'DacCtrl{i}', f'Q{i}', 'VSS', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        
        # State machine logic (simplified implementation)
        self.MOSFET('Mstate0', 'State0', 'Start', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        self.MOSFET('Mstate1', 'State1', 'State0', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        self.MOSFET('Mstate2', 'State2', 'State1', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        self.MOSFET('Mstate3', 'State3', 'State2', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        self.MOSFET('Mstate4', 'EOC', 'State3', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        
        # Reset transistors
        for i in range(4):
            self.MOSFET(f'Mreset{i}', f'State{i}', 'Start', 'VSS', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        self.MOSFET('Mreset_eoc', 'EOC', 'Start', 'VSS', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)