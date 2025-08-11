import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.CDAC import CDAC
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_cdac_binary_response():
    circuit = Circuit('CDAC Binary Response Test')
    
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
    
    # Test all 16 codes
    test_codes = range(16)
    tolerance = 0.02 * vrefp.dc_value  # 2% tolerance
    all_passed = True
    
    print("\nCDAC Binary Code Response Test")
    print("Code\tExpected(V)\tMeasured(V)\tStatus")
    
    for code in test_codes:
        # Set control signals according to binary code
        for bit in range(4):
            ctrl_sources[bit].dc_value = ((code >> bit) & 0x1) * 5@u_V
        
        # Perform DC analysis
        analysis = simulator.operating_point()
        vdac = analysis['Vdac'].as_ndarray().item()
        
        # Calculate expected output (LSB = Vrefp/16)
        expected = (code/15) * vrefp.dc_value
        
        # Check result
        passed = abs(vdac - expected) <= tolerance
        if not passed:
            all_passed = False
        
        print(f"{code:04b}\t{expected:.3f}\t\t{vdac:.3f}\t\t{'PASS' if passed else 'FAIL'}")
    
    if all_passed:
        print("\nTest_Passed: All codes produce correct output voltages")
    else:
        print("\nTest_Failed: One or more codes produced incorrect output")
    
    return all_passed

if __name__ == "__main__":
    test_cdac_binary_response()