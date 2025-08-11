import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.ClockDataRecovery import ClockDataRecovery
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_cdr_data_recovery():
    circuit = Circuit('CDR Data Recovery Test')
    
    # Power supply
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    
    # Add CDR circuit
    circuit.subcircuit(ClockDataRecovery())
    circuit.X('cdr', 'ClockDataRecovery', 'DataIn', 'Vctrl_Init', 
              'RecoveredClk', 'RecoveredData', circuit.gnd, 'VDD')
    
    # Test parameters
    bit_rate = 1@u_Mbps
    initial_vctrl = 2.5@u_V
    test_pattern = [1, 0, 1, 1, 0, 0, 1, 0]  # Alternating and repeated bits
    
    # Create input data signal
    bit_period = 1/bit_rate
    pulse_edges = []
    current_time = 0
    for bit in test_pattern:
        pulse_edges.append((current_time, bit))
        current_time += bit_period
        pulse_edges.append((current_time, bit))
    
    # Create piecewise linear source for data
    pwl_values = []
    for time, value in pulse_edges:
        pwl_values.append(f"{time*1e9:.1f}n {value*5:.1f}")
    
    circuit.V('data', 'DataIn', circuit.gnd, 'PWL(' + ' '.join(pwl_values) + ')')
    
    # Initial control voltage
    circuit.V('vctrl', 'Vctrl_Init', circuit.gnd, initial_vctrl)
    
    # Simulation setup
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.transient(step_time=10@u_ns, end_time=len(test_pattern)*bit_period*1.2)
    
    # Sample recovered data at mid-bit positions
    recovered_data = []
    sample_times = [bit_period*0.5 + i*bit_period for i in range(len(test_pattern))]
    
    for t in sample_times:
        recovered_value = analysis['RecoveredData'].value_at(t)
        recovered_bit = 1 if recovered_value > 2.5 else 0
        recovered_data.append(recovered_bit)
    
    # Compare with test pattern
    errors = 0
    for i in range(len(test_pattern)):
        if test_pattern[i] != recovered_data[i]:
            errors += 1
    
    if errors == 0:
        print("Test_Passed: All bits recovered correctly")
        return True
    else:
        print(f"Test_Failed: {errors} bit errors in {len(test_pattern)} bits")
        print(f"Expected: {test_pattern}")
        print(f"Received: {recovered_data}")
        return False

if __name__ == "__main__":
    test_cdr_data_recovery()