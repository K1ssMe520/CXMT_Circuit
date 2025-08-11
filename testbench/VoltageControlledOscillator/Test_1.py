import sys
from pathlib import Path
import numpy as np

root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

from netlist.VoltageControlledOscillator import VoltageControlledOscillator
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_vco_frequency_control():
    circuit = Circuit('VCO Frequency Control Test')
    
    # Power supplies
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    vss = circuit.V('ss', 'VSS', circuit.gnd, 0@u_V)
    
    # Add VCO
    circuit.subcircuit(VoltageControlledOscillator(
        nmos_width=0.5e-6,
        pmos_width=1e-6,
        channel_length=0.18e-6,
        timing_capacitance=10e-12
    ))
    circuit.X('vco', 'VoltageControlledOscillator', 
              'Vctrl', 'Vctrl_Init', 'RecoveredClk', 'VSS', 'VDD')
    
    # Initial control voltage for startup
    vctrl_init = circuit.V('init', 'Vctrl_Init', circuit.gnd, 2.5@u_V)
    
    # Test control voltages
    test_voltages = [1.0, 2.0, 3.0, 4.0]  # in volts
    frequencies = []
    
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    
    for vctrl_val in test_voltages:
        # Set control voltage
        circuit.V('ctrl', 'Vctrl', circuit.gnd, vctrl_val@u_V)
        
        # Run transient analysis
        analysis = simulator.transient(step_time=10@u_ns, end_time=1@u_us)
        
        # Simple frequency measurement (count zero crossings)
        time = np.array(analysis.time)
        vout = np.array(analysis['RecoveredClk'])
        
        # Count zero crossings (assuming midpoint is 2.5V)
        crossings = np.where(np.diff(vout > 2.5))[0]
        if len(crossings) >= 2:
            period = time[crossings[2]] - time[crossings[0]]
            freq = 1 / period
        else:
            freq = 0
            
        frequencies.append(freq)
    
    # Check frequency increases with control voltage
    test_passed = True
    for i in range(1, len(frequencies)):
        if frequencies[i] <= frequencies[i-1]:
            test_passed = False
            break
    
    print("\nVCO Frequency Control Test Results:")
    print("Control Voltage (V)\tFrequency (MHz)")
    for v, f in zip(test_voltages, frequencies):
        print(f"{v:.1f}\t\t\t{f/1e6:.2f}")
    
    if test_passed:
        print("\nTest_Passed: Frequency increases with control voltage")
    else:
        print("\nTest_Failed: Frequency does not consistently increase with control voltage")
    
    return test_passed

if __name__ == "__main__":
    test_vco_frequency_control()