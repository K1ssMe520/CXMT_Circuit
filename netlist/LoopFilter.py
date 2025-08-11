from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory

class LoopFilter(SubCircuitFactory):
    NAME = 'LoopFilter'
    NODES = ('PhaseError', 'Vctrl', 'VDD', 'VSS')
  
    def __init__(self, r1=10e3, r2=100e3, c1=100e-12, c2=10e-12):
        super().__init__()
        # Passive components for the loop filter
        self.R('R1', 'PhaseError', 'Node1', r1)
        self.R('R2', 'Node1', 'Vctrl', r2)
        self.C('C1', 'Node1', 'VSS', c1)
        self.C('C2', 'Vctrl', 'VSS', c2)
        
        # Optional biasing to VDD (if needed)
        self.R('R3', 'VDD', 'Vctrl', 1e6)  # High resistance to provide weak pull-up