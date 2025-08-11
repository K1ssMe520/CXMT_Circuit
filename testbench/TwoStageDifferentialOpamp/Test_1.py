import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.TwoStageDifferentialOpamp import TwoStageDifferentialOpamp
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_differential_gain():
    circuit = Circuit('TwoStageDifferentialOpamp Gain Test')
    
    # Power supply
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    
    # Add opamp
    circuit.subcircuit(TwoStageDifferentialOpamp())
    circuit.X('opamp', 'TwoStageDifferentialOpamp', 'Vinp', 'Vinn', 
              'Vbias1', 'Vbias2', 'Vbias3', 'Voutp', 'Vout', 'VDD', circuit.gnd)
    
    # Common mode voltage
    vcm = 2.5@u_V
    # Small differential input (10mV)
    vdiff = 0.01@u_V
    
    # Input sources
    circuit.V('inp', 'Vinp', circuit.gnd, vcm + vdiff/2)
    circuit.V('inn', 'Vinn', circuit.gnd, vcm - vdiff/2)
    
    # Bias voltages
    circuit.V('bias1', 'Vbias1', circuit.gnd, 3.5@u_V)
    circuit.V('bias2', 'Vbias2', circuit.gnd, 3.5@u_V)
    circuit.V('bias3', 'Vbias3', circuit.gnd, 1.5@u_V)
    
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.operating_point()
    
    # Get output voltages
    voutp = analysis['Voutp'].as_ndarray().item()
    vout = analysis['Vout'].as_ndarray().item()
    
    # Calculate differential output
    vout_diff = voutp - vout
    
    # Calculate gain
    gain = vout_diff / vdiff
    
    # Expected gain > 100
    min_expected_gain = 100
    passed = abs(gain) > min_expected_gain
    
    print(f"\nDifferential Gain Test Results:")
    print(f"Input differential voltage: {vdiff*1000:.1f}mV")
    print(f"Output differential voltage: {vout_diff*1000:.1f}mV")
    print(f"Calculated gain: {gain:.1f}")
    
    if passed:
        print("\nTest_Passed: Differential gain meets specifications")
    else:
        print("\nTest_Failed: Differential gain is too low")
    
    return passed

if __name__ == "__main__":
    test_differential_gain()