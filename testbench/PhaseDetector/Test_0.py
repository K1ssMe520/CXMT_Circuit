import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.PhaseDetector import PhaseDetector
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_phase_detector_power_supply():
    circuit = Circuit('PhaseDetector Power Supply Test')
    
    # Power supply with variable voltage
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    circuit.subcircuit(PhaseDetector())
    circuit.X('1', 'PhaseDetector', 'DataIn', 'RecoveredClk', 'PhaseError', circuit.gnd, 'VDD')
    
    # Static input signals
    data_in = circuit.V('data', 'DataIn', circuit.gnd, 0@u_V)
    clk_in = circuit.V('clk', 'RecoveredClk', circuit.gnd, 0@u_V)
    
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    
    # Test different power supply voltages
    test_conditions = [
        {'VDD': 4.5, 'expected_max': 4.5, 'expected_min': 0.0},
        {'VDD': 5.0, 'expected_max': 5.0, 'expected_min': 0.0},
        {'VDD': 5.5, 'expected_max': 5.5, 'expected_min': 0.0}
    ]
    
    tolerance = 0.05  # 5% tolerance
    
    all_passed = True
    detailed_results = []
    
    for test in test_conditions:
        vdd.dc_value = test['VDD']@u_V
        analysis = simulator.operating_point()
        
        error_out = analysis['PhaseError'].as_ndarray().item()
        
        # Check if output is within expected range
        in_range = (test['expected_min'] <= error_out <= test['expected_max'])
        
        detailed_results.append({
            'VDD': test['VDD'],
            'PhaseError': error_out,
            'expected_min': test['expected_min'],
            'expected_max': test['expected_max'],
            'in_range': in_range
        })
        
        if not in_range:
            all_passed = False
    
    print("\nDetailed Test Results:")
    print("VDD (V)\tPhaseError (V)\tMin (V)\tMax (V)\tStatus")
    for result in detailed_results:
        status = "PASS" if result['in_range'] else "FAIL"
        print(f"{result['VDD']:.1f}\t{result['PhaseError']:.3f}\t\t{result['expected_min']:.1f}\t{result['expected_max']:.1f}\t{status}")
    
    if all_passed:
        print("\nTest_Passed: All power supply conditions met within tolerance")
    else:
        print("\nTest_Failed: One or more conditions outside expected range")
    
    return all_passed

if __name__ == "__main__":
    test_phase_detector_power_supply()