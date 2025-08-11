import sys
from pathlib import Path
import numpy as np

root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

from netlist.VoltageControlledOscillator import VoltageControlledOscillator
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_vco_startup():
    circuit = Circuit('VCO Startup Test')
    
    # Power supplies
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    vss = circuit.V('ss', 'VSS', circuit.gnd, 0@u_V)
    
    # Add VCO with typical parameters
    circuit.subcircuit(VoltageControlledOscillator(
        nmos_width=0.5e-6,
        pmos_width=1e-6,
        channel_length=0.18e-6,
        timing_capacitance=10e-12
    ))
    circuit.X('vco', 'VoltageControlledOscillator', 
              'Vctrl', 'Vctrl_Init', 'RecoveredClk', 'VSS', 'VDD')
    
    # Set control voltages
    vctrl_init = circuit.V('init', 'Vctrl_Init', circuit.gnd, 2.5@u_V)
    vctrl = circuit.V('ctrl', 'Vctrl', circuit.gnd, 2.5@u_V)
    
    # Run transient analysis
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.transient(step_time=10@u_ns, end_time=2@u_us)
    
    # Analyze output for oscillations
    time = np.array(analysis.time)
    vout = np.array(analysis['RecoveredClk'])
    
    # Count transitions (assuming midpoint is 2.5V)
    crossings = np.where(np.diff(vout > 2.5))[0]
    num_oscillations = len(crossings) // 2
    
    test_passed = num_oscillations >= 3  # At least 3 full cycles
    
    print("\nVCO Startup Test Results:")
    print(f"Number of complete oscillations: {num_oscillations}")
    
    if test_passed:
        print("Test_Passed: Oscillator started successfully")
    else:
        print("Test_Failed: Insufficient oscillations detected")
    
    return test_passed

if __name__ == "__main__":
    test_vco_startup()