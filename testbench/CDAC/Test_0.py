import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.CDAC import CDAC
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_cdac_reset_functionality():
    circuit = Circuit('CDAC Reset Test')
    
    # Power supplies and references
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    vrefp = circuit.V('refp', 'Vrefp', circuit.gnd, 5@u_V)
    vrefn = circuit.V('refn', 'Vrefn', circuit.gnd, 0@u_V)
    
    # Add CDAC subcircuit
    circuit.subcircuit(CDAC())
    circuit.X('cdac', 'CDAC', 'Vrefp', 'Vrefn', 
              'DacCtrl0', 'DacCtrl1', 'DacCtrl2', 'DacCtrl3',
              'Reset', 'Vdac', circuit.gnd, 'VDD')
    
    # Control signals - all initially low
    for i in range(4):
        circuit.V(f'ctrl{i}', f'DacCtrl{i}', circuit.gnd, 0@u_V)
    
    # Reset pulse
    reset_pulse = circuit.PulseVoltageSource('reset', 'Reset', circuit.gnd,
                                            initial_value=0@u_V,
                                            pulsed_value=5@u_V,
                                            pulse_width=100@u_ns,
                                            period=200@u_ns,
                                            delay_time=10@u_ns)
    
    # Simulation setup
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.transient(step_time=10@u_ns, end_time=200@u_ns)
    
    # Expected reset voltage (mid-scale)
    expected_reset_voltage = 2.5  # (Vrefp + Vrefn)/2
    tolerance = 0.05 * vrefp.dc_value
    
    # Check reset condition
    reset_time = 150@u_ns  # During reset pulse
    vdac_reset = analysis['Vdac'].at(reset_time)
    
    test_passed = abs(vdac_reset - expected_reset_voltage) <= tolerance
    
    print("\nCDAC Reset Functionality Test Results:")
    print(f"Expected reset voltage: {expected_reset_voltage:.2f}V")
    print(f"Measured reset voltage: {vdac_reset:.3f}V")
    print(f"Tolerance: ±{tolerance:.2f}V")
    
    if test_passed:
        print("\nTest_Passed: Reset functionality working correctly")
    else:
        print("\nTest_Failed: Reset voltage outside expected range")
    
    return test_passed

if __name__ == "__main__":
    test_cdac_reset_functionality()