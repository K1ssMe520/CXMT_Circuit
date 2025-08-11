import sys
from pathlib import Path
root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

# 2. External imports
from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory
from netlist.DiffInputStage import DiffInputStage
from netlist.CSGainStage import CSGainStage

# 3. Main class definition
class TwoStageDifferentialOpamp(SubCircuitFactory):
    NAME  = 'TwoStageDifferentialOpamp'
    NODES = ('Vinp', 'Vinn',   # differential inputs
             'Vbias1', 'Vbias2', 'Vbias3',  # bias voltages
             'Voutp', 'Vout',  # differential outputs
             'VDD', 'GND')     # power rails

    def __init__(self):
        super().__init__()
        
        # Parameters
        DiffInputStage_Param = {
            'nmos_width': 10e-6,
            'pmos_width': 20e-6,
            'channel_length': 0.18e-6,
            'tail_current': 100e-6
        }

        CSGainStage_Param = {
            'nmos_width': 20e-6,
            'pmos_width': 20e-6,
            'channel_length': 0.18e-6,
            'load_capacitance': 1e-12
        }

        self.model('nmos_model', 'nmos', level=1, kp=200e-6, vto=0.5)
        self.model('pmos_model', 'pmos', level=1, kp=100e-6, vto=-0.5)

        # Sub-circuits
        self.subcircuit(DiffInputStage(
            nmos_width=DiffInputStage_Param['nmos_width'],
            pmos_width=DiffInputStage_Param['pmos_width'],
            channel_length=DiffInputStage_Param['channel_length'],
            tail_current=DiffInputStage_Param['tail_current']))

        self.subcircuit(CSGainStage(
            nmos_width=CSGainStage_Param['nmos_width'],
            pmos_width=CSGainStage_Param['pmos_width'],
            channel_length=CSGainStage_Param['channel_length'],
            load_capacitance=CSGainStage_Param['load_capacitance']))

        # Circuit instantiation
        # Differential input stage
        self.X('diff_stage', 'DiffInputStage',
               'Vinp', 'Vinn', 'Vbias3', 'Vbias1', 'Vout_int',
               'VDD', 'GND')

        # Two common-source gain stages for differential outputs
        self.X('cs_stage_p', 'CSGainStage',
               'Vout_int', 'Vbias2', 'Voutp',
               'VDD', 'GND')
               
        self.X('cs_stage_n', 'CSGainStage',
               'Vout_int', 'Vbias2', 'Vout',
               'VDD', 'GND')

        # Load capacitor between differential outputs
        self.C('load', 'Voutp', 'Vout', CSGainStage_Param['load_capacitance'])

        # Bias generation
        # For tail current source
        self.M('Mtail_bias', 'Vbias3', 'Vbias3', 'GND', 'GND',
               model='nmos_model',
               l=DiffInputStage_Param['channel_length'],
               w=DiffInputStage_Param['nmos_width']*2)

        # For active load in first stage
        self.M('Mload_bias1', 'Vbias1', 'Vbias1', 'VDD', 'VDD',
               model='pmos_model',
               l=DiffInputStage_Param['channel_length'],
               w=DiffInputStage_Param['pmos_width'])

        # For second stage active loads
        self.M('Mload_bias2', 'Vbias2', 'Vbias2', 'VDD', 'VDD',
               model='pmos_model',
               l=CSGainStage_Param['channel_length'],
               w=CSGainStage_Param['pmos_width'])