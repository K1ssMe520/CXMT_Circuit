import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.TwoStageDifferentialOpamp import TwoStageDifferentialOpamp
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_psrr():
    circuit = Circuit('TwoStageDifferentialOpamp PSRR Test')
    
    # Initial power supply
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    
    # Add opamp
    circuit.subcircuit(TwoStageDifferentialOpamp())
    circuit.X('opamp', 'TwoStageDifferentialOpamp', 'Vinp', 'Vinn', 
              'Vbias1', 'Vbias2', 'Vbias3', 'Voutp', 'Vout', 'VDD', circuit.gnd)
    
    # Common mode input
    vcm = 2.5@u_V
    circuit.V('inp', 'Vinp', circuit.gnd, vcm)
    circuit.V('inn', 'Vinn', circuit.gnd, vcm)
    
    # Bias voltages
    circuit.V('bias1', 'Vbias1', circuit.gnd, 3.5@u_V)
    circuit.V('bias2', 'Vbias2', circuit.gnd, 3.5@u_V)
    circuit.V('bias3', 'Vbias3', circuit.gnd, 1.5@u_V)
    
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    
    # Test case 1: Nominal supply (5V)
    analysis1 = simulator.operating_point()
    vout1 = (analysis1['Voutp'].as_ndarray().item() + analysis1['Vout'].as_ndarray().item())/2
    
    # Test case 2: Reduced supply (4.9V)
    vdd.dc_value = 4.9@u_V
    analysis2 = simulator.operating_point()
    vout2 = (analysis2['Voutp'].as_ndarray().item() + analysis2['Vout'].as_ndarray().item())/2
    
    # Calculate PSRR
    delta_vdd = 0.1  # 5V to 4.9V
    delta_vout = vout2 - vout1
    psrr = 20 * np.log10(abs(delta_vdd/delta_vout)) if delta_vout != 0 else float('inf')
    
    # Expected PSRR > 60dB
    min_expected_psrr = 60
    passed = psrr > min_expected_psrr
    
    print(f"\nPSRR Test Results:")
    print(f"Supply voltage change: {delta_vdd*1000:.1f}mV")
    print(f"Output common mode change: {delta_vout*1000:.3f}mV")
    print(f"Calculated PSRR: {psrr:.1f}dB")
    
    if passed:
        print("\nTest_Passed: PSRR meets specifications")
    else:
        print("\nTest_Failed: PSRR is too low")
    
    return passed

if __name__ == "__main__":
    test_psrr()