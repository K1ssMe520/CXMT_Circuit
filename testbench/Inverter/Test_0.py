import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.Inverter import Inverter
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_inverter_power_supply():
    circuit = Circuit('Inverter Power Supply Test')
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    circuit.subcircuit(Inverter())
    circuit.X('1', 'Inverter', 'Vin', 'Vout', circuit.gnd, 'VDD')
    
    input_source = circuit.V('in', 'Vin', circuit.gnd, 0@u_V)
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    
    test_conditions = [
        {'Vin': 0.0, 'expected_Vout': 5.0},
        {'Vin': 5.0, 'expected_Vout': 0.0}
    ]
    
    tolerance = 0.1  # 10% tolerance
    all_passed = True
    
    for test in test_conditions:
        input_source.dc_value = test['Vin']@u_V
        analysis = simulator.operating_point()
        vout = analysis['Vout'].as_ndarray().item()
        
        if not (abs(vout - test['expected_Vout']) <= tolerance):
            all_passed = False
            print(f"FAIL: Vin={test['Vin']}V, Vout={vout:.3f}V (expected {test['expected_Vout']}V)")
    
    if all_passed:
        print("Test_Passed: All power supply conditions met")
    else:
        print("Test_Failed: One or more power supply conditions failed")
    
    return all_passed

if __name__ == "__main__":
    test_inverter_power_supply()