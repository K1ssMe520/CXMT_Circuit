import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.TwoStageDifferentialOpamp import TwoStageDifferentialOpamp
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_cmrr():
    circuit = Circuit('TwoStageDifferentialOpamp CMRR Test')
    
    # Power supply
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    
    # Add opamp
    circuit.subcircuit(TwoStageDifferentialOpamp())
    circuit.X('opamp', 'TwoStageDifferentialOpamp', 'Vinp', 'Vinn', 
              'Vbias1', 'Vbias2', 'Vbias3', 'Voutp', 'Vout', 'VDD', circuit.gnd)
    
    # Common mode voltage variations (2.4V to 2.6V)
    vcm1 = 2.4@u_V
    vcm2 = 2.6@u_V
    
    # Bias voltages
    circuit.V('bias1', 'Vbias1', circuit.gnd, 3.5@u_V)
    circuit.V('bias2', 'Vbias2', circuit.gnd, 3.5@u_V)
    circuit.V('bias3', 'Vbias3', circuit.gnd, 1.5@u_V)
    
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    
    # Test case 1
    circuit.V('inp', 'Vinp', circuit.gnd, vcm1)
    circuit.V('inn', 'Vinn', circuit.gnd, vcm1)
    analysis1 = simulator.operating_point()
    vout_diff1 = analysis1['Voutp'].as_ndarray().item() - analysis1['Vout'].as_ndarray().item()
    
    # Test case 2
    circuit.V('inp', 'Vinp', circuit.gnd, vcm2)
    circuit.V('inn', 'Vinn', circuit.gnd, vcm2)
    analysis2 = simulator.operating_point()
    vout_diff2 = analysis2['Voutp'].as_ndarray().item() - analysis2['Vout'].as_ndarray().item()
    
    # Calculate CMRR
    delta_vcm = vcm2 - vcm1
    delta_vout_diff = vout_diff2 - vout_diff1
    cmrr = 20 * np.log10(abs(delta_vcm/delta_vout_diff)) if delta_vout_diff != 0 else float('inf')
    
    # Expected CMRR > 60dB
    min_expected_cmrr = 60
    passed = cmrr > min_expected_cmrr
    
    print(f"\nCMRR Test Results:")
    print(f"Common mode change: {delta_vcm*1000:.1f}mV")
    print(f"Differential output change: {delta_vout_diff*1000:.3f}mV")
    print(f"Calculated CMRR: {cmrr:.1f}dB")
    
    if passed:
        print("\nTest_Passed: CMRR meets specifications")
    else:
        print("\nTest_Failed: CMRR is too low")
    
    return passed

if __name__ == "__main__":
    test_cmrr()