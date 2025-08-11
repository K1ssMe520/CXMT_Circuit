import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.SimpleSARADC import SimpleSARADC
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_comparator_functionality():
    circuit = Circuit('Comparator Functionality Test')
    
    # Power supplies
    circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    circuit.V('refp', 'Vrefp', circuit.gnd, 5@u_V)
    circuit.V('refn', 'Vrefn', circuit.gnd, 0@u_V)
    
    # Input signals
    circuit.V('clk', 'Clk', circuit.gnd, 0@u_V)
    circuit.V('start', 'Start', circuit.gnd, 0@u_V)
    
    # Add SARADC
    circuit.subcircuit(SimpleSARADC())
    circuit.X('1', 'SimpleSARADC', 'Vin', 'Clk', 'Vrefp', 'Vrefn', 'Start',
              'Dout0', 'Dout1', 'Dout2', 'Dout3', 'EOC', circuit.gnd, 'VDD')
    
    # Test conditions: Vin vs Vdac (simulated by setting DAC bits)
    test_conditions = [
        {'Vin': 1.0, 'DAC_bits': '0000', 'expected_CmpOut': 1},
        {'Vin': 3.0, 'DAC_bits': '1111', 'expected_CmpOut': 0},
        {'Vin': 2.5, 'DAC_bits': '1000', 'expected_CmpOut': 1},
        {'Vin': 2.5, 'DAC_bits': '1001', 'expected_CmpOut': 0}
    ]
    
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    all_passed = True
    
    print("\nComparator Functionality Test Results:")
    print("Vin (V)\tDAC Bits\tExpected\tStatus")
    
    for test in test_conditions:
        # Set input voltage
        circuit.V('in', 'Vin', circuit.gnd, test['Vin']@u_V)
        
        # Force DAC bits (this would normally be set by SAR logic)
        # Note: In actual operation, the DAC bits are controlled by SAR logic
        # For testing purposes, we're directly manipulating internal nodes
        for i, bit in enumerate(test['DAC_bits']):
            circuit.V(f'dac{i}', f'DacCtrl{i}', circuit.gnd, int(bit)@u_V)
        
        analysis = simulator.operating_point()
        
        # Comparator output is an internal node, we'll assume it's called 'CmpOut'
        try:
            cmp_out = analysis['CmpOut'].as_ndarray().item()
            expected = test['expected_CmpOut']
            status = "PASS" if (cmp_out > 2.5 and expected == 1) or (cmp_out < 2.5 and expected == 0) else "FAIL"
            print(f"{test['Vin']:.1f}\t{test['DAC_bits']}\t\t{expected}\t\t{status}")
            
            if status == "FAIL":
                all_passed = False
        except:
            print(f"{test['Vin']:.1f}\t{test['DAC_bits']}\t\t{test['expected_CmpOut']}\t\tFAIL (Node not found)")
            all_passed = False
    
    if all_passed:
        print("\nTest_Passed: Comparator functionality verified")
    else:
        print("\nTest_Failed: Comparator did not meet expectations in one or more cases")
    
    return all_passed

if __name__ == "__main__":
    test_comparator_functionality()