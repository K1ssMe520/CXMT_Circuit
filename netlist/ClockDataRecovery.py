import sys
from pathlib import Path
root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory
from netlist.PhaseDetector import PhaseDetector
from netlist.LoopFilter import LoopFilter
from netlist.VoltageControlledOscillator import VoltageControlledOscillator
from netlist.DataRecoveryUnit import DataRecoveryUnit

class ClockDataRecovery(SubCircuitFactory):
    NAME = 'ClockDataRecovery'
    NODES = ('DataIn', 'Vctrl_Init', 'RecoveredClk', 'RecoveredData', 'VDD', 'VSS')

    def __init__(self):
        super().__init__()
        
        # Parameters
        PhaseDetector_Param = {
            'nmos_width': 2e-6,
            'pmos_width': 4e-6,
            'channel_length': 0.18e-6,
            'filter_capacitance': 1e-12
        }

        LoopFilter_Param = {
            'r1': 10e3,
            'r2': 100e3,
            'c1': 10e-12,
            'c2': 1e-12
        }

        VoltageControlledOscillator_Param = {
            'nmos_width': 2e-6,
            'pmos_width': 4e-6,
            'channel_length': 0.18e-6,
            'ring_stages': 3,
            'load_capacitance': 1e-12
        }

        DataRecoveryUnit_Param = {
            'nmos_width': 2e-6,
            'pmos_width': 4e-6,
            'channel_length': 0.18e-6
        }

        # Subcircuits
        self.subcircuit(PhaseDetector(
            nmos_width=PhaseDetector_Param['nmos_width'],
            pmos_width=PhaseDetector_Param['pmos_width'],
            channel_length=PhaseDetector_Param['channel_length'],
            filter_capacitance=PhaseDetector_Param['filter_capacitance']
        ))

        self.subcircuit(LoopFilter(
            r1=LoopFilter_Param['r1'],
            r2=LoopFilter_Param['r2'],
            c1=LoopFilter_Param['c1'],
            c2=LoopFilter_Param['c2']
        ))

        self.subcircuit(VoltageControlledOscillator(
            nmos_width=VoltageControlledOscillator_Param['nmos_width'],
            pmos_width=VoltageControlledOscillator_Param['pmos_width'],
            channel_length=VoltageControlledOscillator_Param['channel_length'],
            ring_stages=VoltageControlledOscillator_Param['ring_stages'],
            load_capacitance=VoltageControlledOscillator_Param['load_capacitance']
        ))

        self.subcircuit(DataRecoveryUnit(
            nmos_width=DataRecoveryUnit_Param['nmos_width'],
            pmos_width=DataRecoveryUnit_Param['pmos_width'],
            channel_length=DataRecoveryUnit_Param['channel_length']
        ))

        # Circuit connections
        self.X('PD', 'PhaseDetector',
               'DataIn', 'RecoveredClk', 'PhaseError',
               'VDD', 'VSS')

        self.X('LF', 'LoopFilter',
               'PhaseError', 'Vctrl',
               'VDD', 'VSS')

        self.X('VCO', 'VoltageControlledOscillator',
               'Vctrl', 'Vctrl_Init', 'RecoveredClk',
               'VDD', 'VSS')

        self.X('DRU', 'DataRecoveryUnit',
               'DataIn', 'RecoveredClk', 'RecoveredData',
               'VDD', 'VSS')

        # Connect the loop
        self.V('Vctrl', 'Vctrl', 'VSS', 0)  # Initial control voltage