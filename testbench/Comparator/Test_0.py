import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.Comparator import Comparator
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_comparator_basic_functionality():
    circuit = Circuit('Comparator Basic Functionality Test')
    
    # Power supply
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    
    # Add comparator
    circuit.subcircuit(Comparator())
    circuit.X('cmp', 'Comparator', 'Vsh', 'Vdac', 'CmpOut', circuit.gnd, 'VDD')
    
    # Input voltages
    vsh_value = 2.5
    circuit.V('sh', 'Vsh', circuit.gnd, vsh_value@u_V)
    vdac = circuit.V('dac', 'Vdac', circuit.gnd, 0@u_V)
    
    # Setup simulator
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    
    # Perform DC sweep
    analysis = simulator.dc(Vdac=slice(0, 5, 0.01))  # Sweep Vdac from 0V to 5V
    
    # Extract results
    vdac_sweep = np.array(analysis.sweep)
    vout = np.array(analysis['CmpOut'])
    
    # Determine switching point
    switch_index = np.argmax(vout < 2.5)  # Find where output drops below midpoint
    vdac_switch = vdac_sweep[switch_index]
    
    # Check test results
    tolerance = 0.05 * vdd.dc_value  # 5% tolerance
    expected_switch = vsh_value
    
    test_passed = True
    if abs(vdac_switch - expected_switch) > tolerance:
        test_passed = False
    
    # Print test report
    print("\nComparator Basic Functionality Test Results")
    print("="*50)
    print(f"Fixed Vsh voltage: {vsh_value}V")
    print(f"Detected switching point: {vdac_switch:.3f}V")
    print(f"Expected switching point: {expected_switch}V")
    print(f"Tolerance: ±{tolerance:.2f}V")
    
    if test_passed:
        print("\nTest_Passed: Comparator switches within expected range")
    else:
        print("\nTest_Failed: Switching point outside tolerance range")
    
    return test_passed

if __name__ == "__main__":
    test_comparator_basic_functionality()