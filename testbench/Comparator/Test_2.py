import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.Comparator import Comparator
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_comparator_psrr():
    circuit = Circuit('Comparator PSRR Test')
    
    # Power supply (will be varied)
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    
    # Add comparator
    circuit.subcircuit(Comparator())
    circuit.X('cmp', 'Comparator', 'Vsh', 'Vdac', 'CmpOut', circuit.gnd, 'VDD')
    
    # Input voltages set near switching point
    vsh_value = 2.5
    vdac_value = 2.51  # Slightly above Vsh to test sensitivity
    circuit.V('sh', 'Vsh', circuit.gnd, vsh_value@u_V)
    circuit.V('dac', 'Vdac', circuit.gnd, vdac_value@u_V)
    
    # Setup simulator
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    
    # Test conditions
    vdd_values = [4.5, 5.0, 5.5]  # Test at different supply voltages
    tolerance = 0.1  # Allowable output variation (V)
    
    test_passed = True
    results = []
    
    for vdd_val in vdd_values:
        vdd.dc_value = vdd_val@u_V
        analysis = simulator.operating_point()
        vout = float(analysis['CmpOut'])
        results.append({'VDD': vdd_val, 'Vout': vout})
    
    # Check if output variation is within tolerance
    vout_values = [r['Vout'] for r in results]
    vout_range = max(vout_values) - min(vout_values)
    
    if vout_range > tolerance:
        test_passed = False
    
    # Print test report
    print("\nComparator Power Supply Rejection Test Results")
    print("="*50)
    print(f"Input conditions: Vsh={vsh_value}V, Vdac={vdac_value}V")
    print("\nVDD (V)\tOutput (V)")
    for result in results:
        print(f"{result['VDD']:.1f}\t{result['Vout']:.3f}")
    
    print(f"\nOutput variation range: {vout_range:.3f}V")
    print(f"Allowed variation: {tolerance:.2f}V")
    
    if test_passed:
        print("\nTest_Passed: Output variation within acceptable range")
    else:
        print("\nTest_Failed: Output variation exceeds tolerance")
    
    return test_passed

if __name__ == "__main__":
    test_comparator_psrr()