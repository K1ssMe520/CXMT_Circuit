import sys
from pathlib import Path
import numpy as np

root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

from netlist.VoltageControlledOscillator import VoltageControlledOscillator
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_vco_psrr():
    circuit = Circuit('VCO Power Supply Rejection Test')
    
    # Test power supply voltages
    vdd_values = [4.5, 5.0, 5.5]  # in volts
    frequencies = []
    
    for vdd_val in vdd_values:
        # Create fresh circuit for each test
        test_circuit = Circuit(f'VCO PSRR Test {vdd_val}V')
        
        # Power supplies
        vdd = test_circuit.V('dd', 'VDD', test_circuit.gnd, vdd_val@u_V)
        vss = test_circuit.V('ss', 'VSS', test_circuit.gnd, 0@u_V)
        
        # Add VCO
        test_circuit.subcircuit(VoltageControlledOscillator())
        test_circuit.X('vco', 'VoltageControlledOscillator', 
                      'Vctrl', 'Vctrl_Init', 'RecoveredClk', 'VSS', 'VDD')
        
        # Set control voltages (fixed)
        vctrl_init = test_circuit.V('init', 'Vctrl_Init', test_circuit.gnd, 2.5@u_V)
        vctrl = test_circuit.V('ctrl', 'Vctrl', test_circuit.gnd, 2.5@u_V)
        
        # Run transient analysis
        simulator = test_circuit.simulator(temperature=25, nominal_temperature=25)
        analysis = simulator.transient(step_time=10@u_ns, end_time=1@u_us)
        
        # Measure frequency
        time = np.array(analysis.time)
        vout = np.array(analysis['RecoveredClk'])
        
        crossings = np.where(np.diff(vout > vdd_val/2))[0]
        if len(crossings) >= 2:
            period = time[crossings[2]] - time[crossings[0]]
            freq = 1 / period
        else:
            freq = 0
            
        frequencies.append(freq)
    
    # Calculate frequency variation
    freq_variation = (max(frequencies) - min(frequencies)) / np.mean(frequencies)
    
    # Allow up to 10% variation
    test_passed = freq_variation <= 0.10
    
    print("\nVCO Power Supply Rejection Test Results:")
    print("VDD (V)\tFrequency (MHz)")
    for v, f in zip(vdd_values, frequencies):
        print(f"{v:.1f}\t{f/1e6:.2f}")
    
    print(f"\nFrequency variation: {freq_variation*100:.1f}%")
    
    if test_passed:
        print("Test_Passed: Frequency variation within 10%")
    else:
        print("Test_Failed: Excessive frequency variation with supply voltage")
    
    return test_passed

if __name__ == "__main__":
    test_vco_psrr()