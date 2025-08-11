import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.Comparator import Comparator
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_comparator_response_time():
    circuit = Circuit('Comparator Response Time Test')
    
    # Power supply
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    
    # Add comparator
    circuit.subcircuit(Comparator())
    circuit.X('cmp', 'Comparator', 'Vsh', 'Vdac', 'CmpOut', circuit.gnd, 'VDD')
    
    # Input voltages
    vsh_value = 2.5
    circuit.V('sh', 'Vsh', circuit.gnd, vsh_value@u_V)
    
    # Create fast-rising edge on Vdac
    circuit.PulseVoltageSource('dac', 'Vdac', circuit.gnd,
                              initial_value=0@u_V, pulsed_value=5@u_V,
                              pulse_width=10@u_ns, period=20@u_ns,
                              rise_time=0.1@u_ns, fall_time=0.1@u_ns)
    
    # Setup simulator
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    
    # Run transient analysis
    analysis = simulator.transient(step_time=0.01@u_ns, end_time=20@u_ns)
    
    # Extract time points and signals
    time = np.array(analysis.time)
    vdac = np.array(analysis['Vdac'])
    vout = np.array(analysis['CmpOut'])
    
    # Find input crossing time (when Vdac crosses Vsh)
    input_cross_idx = np.argmax(vdac > vsh_value)
    t_input_cross = time[input_cross_idx]
    
    # Find output switching time (when Vout crosses 2.5V)
    output_cross_idx = np.argmax(vout < 2.5)
    t_output_cross = time[output_cross_idx]
    
    # Calculate propagation delay
    propagation_delay = t_output_cross - t_input_cross
    
    # Check if delay is within specification
    max_delay = 2@u_ns  # 2ns maximum allowed delay
    test_passed = propagation_delay <= max_delay
    
    # Print test report
    print("\nComparator Response Time Test Results")
    print("="*50)
    print(f"Input crossing time: {t_input_cross*1e9:.2f}ns")
    print(f"Output switching time: {t_output_cross*1e9:.2f}ns")
    print(f"Measured propagation delay: {propagation_delay*1e9:.2f}ns")
    print(f"Maximum allowed delay: {max_delay*1e9:.0f}ns")
    
    if test_passed:
        print("\nTest_Passed: Propagation delay within specification")
    else:
        print("\nTest_Failed: Propagation delay exceeds maximum allowed")
    
    return test_passed

if __name__ == "__main__":
    test_comparator_response_time()