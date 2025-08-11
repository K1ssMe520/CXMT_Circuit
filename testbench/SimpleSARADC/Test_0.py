import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.SimpleSARADC import SimpleSARADC
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_saradc_initialization():
    circuit = Circuit('SARADC Initialization Test')
    
    # Power supplies
    circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    circuit.V('refp', 'Vrefp', circuit.gnd, 5@u_V)
    circuit.V('refn', 'Vrefn', circuit.gnd, 0@u_V)
    
    # Input signals
    circuit.V('clk', 'Clk', circuit.gnd, 0@u_V)
    circuit.V('start', 'Start', circuit.gnd, 0@u_V)
    circuit.V('in', 'Vin', circuit.gnd, 0@u_V)
    
    # Add SARADC
    circuit.subcircuit(SimpleSARADC())
    circuit.X('1', 'SimpleSARADC', 'Vin', 'Clk', 'Vrefp', 'Vrefn', 'Start',
              'Dout0', 'Dout1', 'Dout2', 'Dout3', 'EOC', circuit.gnd, 'VDD')
    
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.operating_point()
    
    # Expected values
    expected_outputs = {
        'Dout0': 0,
        'Dout1': 0,
        'Dout2': 0,
        'Dout3': 0,
        'EOC': 0
    }
    
    tolerance = 0.1
    all_passed = True
    
    print("\nInitialization Test Results:")
    print("Node\t\tMeasured\tExpected\tStatus")
    
    for node, expected in expected_outputs.items():
        measured = analysis[node].as_ndarray().item()
        status = "PASS" if abs(measured - expected) <= tolerance else "FAIL"
        print(f"{node}\t{measured:.3f}\t\t{expected}\t\t{status}")
        
        if status == "FAIL":
            all_passed = False
    
    if all_passed:
        print("\nTest_Passed: All outputs initialized correctly")
    else:
        print("\nTest_Failed: One or more outputs not initialized properly")
    
    return all_passed

if __name__ == "__main__":
    test_saradc_initialization()