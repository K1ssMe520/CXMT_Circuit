import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.Comparator import Comparator
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_comparator_offset_voltage():
    circuit = Circuit('Comparator Offset Voltage Test')
    
    # Power supply
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    
    # Add comparator
    circuit.subcircuit(Comparator())
    circuit.X('cmp', 'Comparator', 'Vsh', 'Vdac', 'CmpOut', circuit.gnd, 'VDD')
    
    # Input voltages - both set to same value initially
    vsh_value = 2.5
    circuit.V('sh', 'Vsh', circuit.gnd, vsh_value@u_V)
    vdac = circuit.V('dac', 'Vdac', circuit.gnd, vsh_value@u_V)
    
    # Setup simulator
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    
    # Perform fine DC sweep around expected switching point
    sweep_range = 0.1  # ±100mV around expected point
    analysis = simulator.dc(Vdac=slice(vsh_value-sweep_range, vsh_value+sweep_range, 0.001))
    
    # Extract results
    vdac_sweep = np.array(analysis.sweep)
    vout = np.array(analysis['CmpOut'])
    
    # Find actual switching point (where output crosses 2.5V)
    switch_index = np.argmax(vout < 2.5)
    vdac_switch = vdac_sweep[switch_index]
    offset_voltage = vdac_switch - vsh_value
    
    # Check if offset is within acceptable range
    max_offset = 0.01  # 10mV maximum acceptable offset
    test_passed = abs(offset_voltage) <= max_offset
    
    # Print test report
    print("\nComparator Offset Voltage Test Results")
    print("="*50)
    print(f"Expected switching point: {vsh_value}V")
    print(f"Actual switching point: {vdac_switch:.4f}V")
    print(f"Input-referred offset voltage: {offset_voltage*1000:.2f}mV")
    print(f"Maximum allowed offset: ±{max_offset*1000:.0f}mV")
    
    if test_passed:
        print("\nTest_Passed: Offset voltage within acceptable range")
    else:
        print("\nTest_Failed: Offset voltage exceeds maximum allowed")
    
    return test_passed

if __name__ == "__main__":
    test_comparator_offset_voltage()