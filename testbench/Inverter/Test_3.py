import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.Inverter import Inverter
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_inverter_power_consumption():
    circuit = Circuit('Inverter Power Test')
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    circuit.subcircuit(Inverter())
    circuit.X('1', 'Inverter', 'Vin', 'Vout', circuit.gnd, 'VDD')
    
    input_source = circuit.V('in', 'Vin', circuit.gnd, 0@u_V)
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    
    test_conditions = [
        {'Vin': 0.0, 'max_power': 1@u_uW},
        {'Vin': 5.0, 'max_power': 1@u_uW}
    ]
    
    all_passed = True
    
    for test in test_conditions:
        input_source.dc_value = test['Vin']@u_V
        analysis = simulator.operating_point()
        
        current = analysis['Vdd'].as_ndarray().item()
        power = abs(current * 5)  # P = IV
        
        if power > test['max_power']:
            all_passed = False
            print(f"FAIL: Vin={test['Vin']}V, Power={power*1e6:.2f}uW (max {test['max_power']*1e6}uW)")
    
    if all_passed:
        print("Test_Passed: Power consumption within limits")
    else:
        print("Test_Failed: Excessive power consumption detected")
    
    return all_passed

if __name__ == "__main__":
    test_inverter_power_consumption()