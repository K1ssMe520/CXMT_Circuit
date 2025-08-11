import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

from netlist.PhaseDetector import PhaseDetector
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_phase_detector_sensitivity():
    circuit = Circuit('PhaseDetector Sensitivity Test')
    
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    circuit.subcircuit(PhaseDetector())
    circuit.X('1', 'PhaseDetector', 'DataIn', 'RecoveredClk', 'PhaseError', circuit.gnd, 'VDD')
    
    # Common parameters for both signals
    period = 1000@u_ns
    pulse_width = 500@u_ns
    
    # Data input (reference signal)
    data_in = circuit.PulseVoltageSource('data', 'DataIn', circuit.gnd,
                                        initial_value=0@u_V, pulsed_value=5@u_V,
                                        pulse_width=pulse_width, period=period)
    
    # Clock input with variable phase offset
    clk_in = circuit.PulseVoltageSource('clk', 'RecoveredClk', circuit.gnd,
                                      initial_value=0@u_V, pulsed_value=5@u_V,
                                      pulse_width=pulse_width, period=period)
    
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    
    # Test different phase offsets
    test_conditions = [
        {'delay': 0@u_ns, 'expected_dir': 'mid'},
        {'delay': 100@u_ns, 'expected_dir': 'up'},
        {'delay': 200@u_ns, 'expected_dir': 'up'},
        {'delay': -100@u_ns, 'expected_dir': 'down'},
        {'delay': -200@u_ns, 'expected_dir': 'down'}
    ]
    
    all_passed = True
    detailed_results = []
    
    for test in test_conditions:
        clk_in.delay_time = test['delay']
        
        analysis = simulator.transient(step_time=10@u_ns, end_time=2000@u_ns)
        
        # Get steady-state output
        error_out = np.array(analysis['PhaseError'])[-100:]
        avg_error = np.mean(error_out)
        
        # Determine if output matches expected direction
        if test['expected_dir'] == 'mid':
            expected_range = (2.0, 3.0)  # Midpoint range
            in_range = expected_range[0] <= avg_error <= expected_range[1]
            status = "MID" if in_range else "NOT MID"
        elif test['expected_dir'] == 'up':
            in_range = avg_error > 3.0
            status = "UP" if in_range else "NOT UP"
        else:  # 'down'
            in_range = avg_error < 2.0
            status = "DOWN" if in_range else "NOT DOWN"
        
        detailed_results.append({
            'delay': test['delay'],
            'avg_error': avg_error,
            'expected': test['expected_dir'],
            'status': status
        })
        
        if not in_range:
            all_passed = False
    
    print("\nDetailed Test Results:")
    print("Delay (ns)\tAvg Output (V)\tExpected\tStatus")
    for result in detailed_results:
        print(f"{result['delay']:.0f}\t\t{result['avg_error']:.3f}\t\t{result['expected']}\t\t{result['status']}")
    
    if all_passed:
        print("\nTest_Passed: Phase detector responds correctly to phase differences")
    else:
        print("\nTest_Failed: Phase detector response incorrect for one or more test cases")
    
    return all_passed

if __name__ == "__main__":
    test_phase_detector_sensitivity()