import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

from netlist.PhaseDetector import PhaseDetector
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_phase_detector_frequency_response():
    circuit = Circuit('PhaseDetector Frequency Response Test')
    
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    circuit.subcircuit(PhaseDetector())
    circuit.X('1', 'PhaseDetector', 'DataIn', 'RecoveredClk', 'PhaseError', circuit.gnd, 'VDD')
    
    # Fixed 100ns phase offset
    phase_offset = 100@u_ns
    
    # Data input (reference signal)
    data_in = circuit.PulseVoltageSource('data', 'DataIn', circuit.gnd,
                                        initial_value=0@u_V, pulsed_value=5@u_V,
                                        pulse_width=500@u_ns, period=1000@u_ns)
    
    # Clock input with phase offset
    clk_in = circuit.PulseVoltageSource('clk', 'RecoveredClk', circuit.gnd,
                                      initial_value=0@u_V, pulsed_value=5@u_V,
                                      pulse_width=500@u_ns, period=1000@u_ns,
                                      delay_time=phase_offset)
    
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    
    # Test different frequencies
    test_conditions = [
        {'frequency': 1@u_MHz, 'period': 1000@u_ns},
        {'frequency': 2@u_MHz, 'period': 500@u_ns},
        {'frequency': 5@u_MHz, 'period': 200@u_ns},
        {'frequency': 10@u_MHz, 'period': 100@u_ns}
    ]
    
    all_passed = True
    detailed_results = []
    
    for test in test_conditions:
        # Update both signals with new frequency
        data_in.period = test['period']
        data_in.pulse_width = test['period']/2
        clk_in.period = test['period']
        clk_in.pulse_width = test['period']/2
        clk_in.delay_time = phase_offset  # Maintain same phase offset in time
        
        # Run simulation for 10 cycles
        end_time = 10 * test['period']
        analysis = simulator.transient(step_time=test['period']/100, end_time=end_time)
        
        # Get steady-state output
        error_out = np.array(analysis['PhaseError'])[-50:]
        avg_error = np.mean(error_out)
        
        # Expected output should be above midpoint for positive phase offset
        expected_min = 3.0
        in_range = avg_error >= expected_min
        
        detailed_results.append({
            'frequency': test['frequency'],
            'avg_error': avg_error,
            'expected_min': expected_min,
            'in_range': in_range
        })
        
        if not in_range:
            all_passed = False
    
    print("\nDetailed Test Results:")
    print("Frequency (MHz)\tAvg Output (V)\tMin Expected (V)\tStatus")
    for result in detailed_results:
        status = "PASS" if result['in_range'] else "FAIL"
        print(f"{result['frequency']:.1f}\t\t{result['avg_error']:.3f}\t\t{result['expected_min']:.1f}\t\t{status}")
    
    if all_passed:
        print("\nTest_Passed: Phase detector operates correctly across frequency range")
    else:
        print("\nTest_Failed: Phase detector output incorrect at one or more frequencies")
    
    return all_passed

if __name__ == "__main__":
    test_phase_detector_frequency_response()