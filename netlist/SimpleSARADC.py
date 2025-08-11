import sys
from pathlib import Path
root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory
from netlist.SampleAndHold import SampleAndHold
from netlist.Comparator import Comparator
from netlist.CDAC import CDAC
from netlist.SARLogic import SARLogic

class SimpleSARADC(SubCircuitFactory):
    NAME = 'SimpleSARADC'
    NODES = ('Vin', 'Clk', 'Vrefp', 'Vrefn', 'Start',
             'Dout0', 'Dout1', 'Dout2', 'Dout3', 'EOC',
             'VDD', 'GND')

    def __init__(self):
        super().__init__()
        
        # Parameters
        SampleAndHold_Param = {
            'nmos_width': 2e-6,
            'pmos_width': 4e-6,
            'channel_length': 0.18e-6,
            'hold_capacitance': 1e-12
        }

        Comparator_Param = {
            'nmos_width': 5e-6,
            'pmos_width': 10e-6,
            'channel_length': 0.18e-6,
            'load_capacitance': 0
        }

        CDAC_Param = {
            'unit_capacitance': 100e-15
        }

        SARLogic_Param = {
            'nmos_width': 1e-6,
            'pmos_width': 2e-6,
            'channel_length': 0.18e-6
        }

        # Subcircuits
        self.subcircuit(SampleAndHold(
            nmos_width=SampleAndHold_Param['nmos_width'],
            pmos_width=SampleAndHold_Param['pmos_width'],
            channel_length=SampleAndHold_Param['channel_length'],
            hold_capacitance=SampleAndHold_Param['hold_capacitance']))

        self.subcircuit(Comparator(
            nmos_width=Comparator_Param['nmos_width'],
            pmos_width=Comparator_Param['pmos_width'],
            channel_length=Comparator_Param['channel_length'],
            load_capacitance=Comparator_Param['load_capacitance']))

        self.subcircuit(CDAC(
            unit_capacitance=CDAC_Param['unit_capacitance']))

        self.subcircuit(SARLogic(
            nmos_width=SARLogic_Param['nmos_width'],
            pmos_width=SARLogic_Param['pmos_width'],
            channel_length=SARLogic_Param['channel_length']))

        # Circuit connections
        self.X('S_H', 'SampleAndHold',
               'Vin', 'Clk', 'Vsh',
               'VDD', 'GND')

        self.X('COMP', 'Comparator',
               'Vsh', 'Vdac', 'CmpOut',
               'VDD', 'GND')

        self.X('DAC', 'CDAC',
               'Vrefp', 'Vrefn', 'DacCtrl0', 'DacCtrl1', 'DacCtrl2', 'DacCtrl3',
               'Vdac',
               'VDD', 'GND')

        self.X('SAR', 'SARLogic',
               'Clk', 'Start', 'CmpOut',
               'Dout0', 'Dout1', 'Dout2', 'Dout3', 'EOC',
               'DacCtrl0', 'DacCtrl1', 'DacCtrl2', 'DacCtrl3',
               'VDD', 'GND')

        # Connect output nodes
        self.alias('Dout0', 'SAR.Dout0')
        self.alias('Dout1', 'SAR.Dout1')
        self.alias('Dout2', 'SAR.Dout2')
        self.alias('Dout3', 'SAR.Dout3')
        self.alias('EOC', 'SAR.EOC')