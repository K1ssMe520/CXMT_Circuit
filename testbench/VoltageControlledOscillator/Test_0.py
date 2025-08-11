import sys
from pathlib import Path
root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

from netlist.VoltageControlledOscillator import VoltageControlledOscillator
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_vco_power_supply():
    circuit = Circuit('VCO Power Supply Test')
    
    # Power supplies
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    vss = circuit.V('ss', 'VSS', circuit.gnd, 0@u_V)
    
    # Add VCO with initial control voltage
    circuit.subcircuit(VoltageControlledOscillator())
    circuit.X('vco', 'VoltageControlledOscillator', 
              'Vctrl', 'Vctrl_Init', 'RecoveredClk', 'VSS', 'VDD')
    
    # Set initial control voltage (mid-range)
    vctrl_init = circuit.V('init', 'Vctrl_Init', circuit.gnd, 2.5@u_V)
    vctrl = circuit.V('ctrl', 'Vctrl', circuit.gnd, 2.5@u_V)
    
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.operating_point()
    
    # Check output voltage is within valid range
    vout = analysis['RecoveredClk'].as_ndarray().item()
    valid_min = 0.1
    valid_max = 4.9
    
    test_passed = valid_min <= vout <= valid_max
    
    print("\nVCO Power Supply Test Results:")
    print(f"Output Voltage: {vout:.3f}V")
    print(f"Valid Range: {valid_min}V to {valid_max}V")
    
    if test_passed:
        print("Test_Passed: Output voltage within valid range")
    else:
        print("Test_Failed: Output voltage outside valid range")
    
    return test_passed

if __name__ == "__main__":
    test_vco_power_supply()