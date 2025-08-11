import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.TwoStageDifferentialOpamp import TwoStageDifferentialOpamp
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_dc_operating_point():
    circuit = Circuit('TwoStageDifferentialOpamp DC Test')
    
    # Power supply
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    
    # Add opamp
    circuit.subcircuit(TwoStageDifferentialOpamp())
    circuit.X('opamp', 'TwoStageDifferentialOpamp', 'Vinp', 'Vinn', 
              'Vbias1', 'Vbias2', 'Vbias3', 'Voutp', 'Vout', 'VDD', circuit.gnd)
    
    # Input sources (common mode)
    vcm = 2.5@u_V  # Mid-supply
    circuit.V('inp', 'Vinp', circuit.gnd, vcm)
    circuit.V('inn', 'Vinn', circuit.gnd, vcm)
    
    # Bias voltages (typical values)
    circuit.V('bias1', 'Vbias1', circuit.gnd, 3.5@u_V)
    circuit.V('bias2', 'Vbias2', circuit.gnd, 3.5@u_V)
    circuit.V('bias3', 'Vbias3', circuit.gnd, 1.5@u_V)
    
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.operating_point()
    
    # Expected output common mode voltage (mid-supply)
    expected_vout_cm = 2.5
    tolerance = 0.2  # ±200mV
    
    # Get output voltages
    voutp = analysis['Voutp'].as_ndarray().item()
    vout = analysis['Vout'].as_ndarray().item()
    
    # Calculate common mode output
    vout_cm = (voutp + vout)/2
    
    # Check if outputs are within expected range
    passed = True
    if abs(vout_cm - expected_vout_cm) > tolerance:
        passed = False
        print(f"FAIL: Output common mode voltage {vout_cm:.3f}V is not within {expected_vout_cm±tolerance}V range")
    
    # Check differential output is near zero
    vdiff = voutp - vout
    if abs(vdiff) > 0.01:
        passed = False
        print(f"FAIL: Differential output {vdiff:.3f}V is not near zero with common mode inputs")
    
    if passed:
        print("\nTest_Passed: DC operating points are within expected ranges")
    else:
        print("\nTest_Failed: One or more DC operating points are out of range")
    
    return passed

if __name__ == "__main__":
    test_dc_operating_point()