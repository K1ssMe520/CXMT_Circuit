import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.SimpleSARADC import SimpleSARADC
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_adc_linearity():
    circuit = Circuit('SARADC Linearity Test')
    
    # Power supplies
    circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    circuit.V('refp', 'Vrefp', circuit.gnd, 5@u_V)
    circuit.V('refn', 'Vrefn', circuit.gnd, 0@u_V)
    
    # Clock and start signals (fixed for this test)
    circuit.V('clk', 'Clk', circuit.gnd, 5@u_V)  # Constant high to enable conversion
    circuit.V('start', 'Start', circuit.gnd, 5@u_V)  # Constant high to start conversion
    
    # Input voltage source
    circuit.V('in', 'Vin', circuit.gnd, 0@u_V)  # Will be swept
    
    # Add SARADC
    circuit.subcircuit(SimpleSARADC())
    circuit.X('1', 'SimpleSARADC', 'Vin', 'Clk', 'Vrefp', 'Vrefn', 'Start',
              'Dout0', 'Dout1', 'Dout2', 'Dout3', 'EOC', circuit.gnd, 'VDD')
    
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    
    # Test points at mid-point of each code
    test_points = [
        (0.3125, '0000'), (0.9375, '0001'), (1.5625, '0010'), (2.1875, '0011'),
        (2.8125, '0100'), (3.4375, '0101'), (4.0625, '0110'), (4.6875, '0111')
    ]
    
    all_passed = True
    print("\nLinearity Test Results:")
    print("Vin (V)\tExpected\tMeasured\tStatus")
    
    for vin, expected in test_points:
        circuit.V('in').dc_value = vin@u_V
        analysis = simulator.operating_point()
        
        # Read digital outputs
        dout0 = 1 if analysis['Dout0'].as_ndarray().item() > 2.5 else 0
        dout1 = 1 if analysis['Dout1'].as_ndarray().item() > 2.5 else 0
        dout2 = 1 if analysis['Dout2'].as_ndarray().item() > 2.5 else 0
        dout3 = 1 if analysis['Dout3'].as_ndarray().item() > 2.5 else 0
        measured = f"{dout3}{dout2}{dout1}{dout0}"
        
        status = "PASS" if measured == expected else "FAIL"
        print(f"{vin:.4f}\t{expected}\t\t{measured}\t\t{status}")
        
        if status == "FAIL":
            all_passed = False
    
    if all_passed:
        print("\nTest_Passed: All test points within expected codes")
    else:
        print("\nTest_Failed: One or more test points outside expected codes")
    
    return all_passed

if __name__ == "__main__":
    test_adc_linearity()