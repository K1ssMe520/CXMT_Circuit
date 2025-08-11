import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.CDAC import CDAC
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_cdac_monotonicity():
    circuit = Circuit('CDAC Monotonicity Test')
    
    # Power supplies and references
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    vrefp = circuit.V('refp', 'Vrefp', circuit.gnd, 5@u_V)
    vrefn = circuit.V('refn', 'Vrefn', circuit.gnd, 0@u_V)
    
    # Add CDAC subcircuit
    circuit.subcircuit(CDAC())
    circuit.X('cdac', 'CDAC', 'Vrefp', 'Vrefn', 
              'DacCtrl0', 'DacCtrl1', 'DacCtrl2', 'DacCtrl3',
              'Reset', 'Vdac', circuit.gnd, 'VDD')
    
    # Reset control (held low after initial reset)
    circuit.V('reset', 'Reset', circuit.gnd, 0@u_V)
    
    # Digital control signals
    ctrl_sources = []
    for i in range(4):
        ctrl_sources.append(circuit.V(f'ctrl{i}', f'DacCtrl{i}', circuit.gnd, 0@u_V))
    
    # Simulation setup
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    
    # Test all codes in sequence
    test_codes = range(16)
    previous_vdac = -1
    all_passed = True
    non_monotonic_points = []
    
    print("\nCDAC Monotonicity Test")
    print("Code\tVoltage(V)\tStatus")
    
    for code in test_codes:
        # Set control signals according to binary code
        for bit in range(4):
            ctrl_sources[bit].dc_value = ((code >> bit) & 0x1) * 5@u_V
        
        # Perform DC analysis
        analysis = simulator.operating_point()
        vdac = analysis['Vdac'].as_ndarray().item()
        
        # Check monotonicity
        if code > 0 and vdac <= previous_vdac:
            all_passed = False
            non_monotonic_points.append((code, vdac, previous_vdac))
            status = "FAIL"
        else:
            status = "PASS"
        
        print(f"{code:04b}\t{vdac:.4f}\t{status}")
        previous_vdac = vdac
    
    if all_passed:
        print("\nTest_Passed: CDAC output is perfectly monotonic")
    else:
        print("\nTest_Failed: Non-monotonic behavior detected at:")
        for point in non_monotonic_points:
            print(f"  Code {point[0]:04b}: {point[1]:.4f}V (previous: {point[2]:.4f}V)")
    
    return all_passed

if __name__ == "__main__":
    test_cdac_monotonicity()