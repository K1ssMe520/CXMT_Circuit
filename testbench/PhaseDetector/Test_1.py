import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

from netlist.PhaseDetector import PhaseDetector
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_phase_detector_static_alignment():
    circuit = Circuit('PhaseDetector Static Alignment Test')
    
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    circuit.subcircuit(PhaseDetector())
    circuit.X('1', 'PhaseDetector', 'DataIn', 'RecoveredClk', 'PhaseError', circuit.gnd, 'VDD')
    
    # Create synchronized input signals
    data_in = circuit.PulseVoltageSource('data', 'DataIn', circuit.gnd,
                                        initial_value=0@u_V, pulsed_value=5@u_V,
                                        pulse_width=500@u_ns, period=1000@u_ns)
    clk_in = circuit.PulseVoltageSource('clk', 'RecoveredClk', circuit.gnd,
                                      initial_value=0@u_V, pulsed_value=5@u_V,
                                      pulse_width=500@u_ns, period=1000@u_ns,
                                      delay_time=0@u_ns)  # No delay = aligned
    
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.transient(step_time=10@u_ns, end_time=2000@u_ns)
    
    # Get steady-state output (ignore initial transient)
    time = np.array(analysis.time)[-100:]
    error_out = np.array(analysis['PhaseError'])[-100:]
    
    expected_midpoint = 2.5  # Midpoint of 0-5V range
    tolerance = 0.1 * vdd.dc_value  # 10% tolerance
    
    # Check if output is near midpoint
    avg_error = np.mean(error_out)
    in_range = (abs(avg_error - expected_midpoint) <= tolerance)
    
    print("\nTest Results:")
    print(f"Expected midpoint: {expected_midpoint:.2f}V ± {tolerance:.2f}V")
    print(f"Actual average output: {avg_error:.3f}V")
    
    if in_range:
        print("\nTest_Passed: Output is at midpoint for aligned inputs")
    else:
        print("\nTest_Failed: Output not at expected midpoint for aligned inputs")
    
    return in_range

if __name__ == "__main__":
    test_phase_detector_static_alignment()