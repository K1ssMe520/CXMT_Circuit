import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.CDAC import CDAC
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_cdac_settling_time():
    circuit = Circuit('CDAC Settling Time Test')
    
    # Power supplies and references
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    vrefp = circuit.V('refp', 'Vrefp', circuit.gnd, 5@u_V)
    vrefn = circuit.V('refn', 'Vrefn', circuit.gnd, 0@u_V)
    
    # Add CDAC subcircuit
    circuit.subcircuit(CDAC())
    circuit.X('cdac', 'CDAC', 'Vrefp', 'Vrefn', 
              'DacCtrl0', 'DacCtrl1', 'DacCtrl2', 'DacCtrl3',
              'Reset', 'Vdac', circuit.gnd, 'VDD')
    
    # Reset control (initial pulse then held low)
    reset_pulse = circuit.PulseVoltageSource('reset', 'Reset', circuit.gnd,
                                           initial_value=0@u_V,
                                           pulsed_value=5@u_V,
                                           pulse_width=100@u_ns,
                                           period=1@u_us,
                                           delay_time=10@u_ns)
    
    # Digital control signals - transition from 0000 to 1111
    for i in range(4):
        circuit.PulseVoltageSource(f'ctrl{i}', f'DacCtrl{i}', circuit.gnd,
                                  initial_value=0@u_V,
                                  pulsed_value=5@u_V,
                                  pulse_width=500@u_ns,
                                  period=1@u_us,
                                  delay_time=200@u_ns,
                                  rise_time=10@u_ns,
                                  fall_time=10@u_ns)
    
    # Simulation setup
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.transient(step_time=1@u_ns, end_time=1@u_us)
    
    # Expected final value (code 1111)
    expected_final = vrefp.dc_value
    settling_threshold = 0.01 * expected_final  # 1% settling criteria
    
    # Find settling time
    transition_start = 200@u_ns
    vdac = analysis['Vdac']
    settling_time = None
    
    for time, voltage in zip(analysis.time, vdac):
        if time > transition_start:
            if abs(voltage - expected_final) <= settling_threshold:
                settling_time = time - transition_start
                break
    
    max_settling_time = 100@u_ns  # Specification requirement
    
    test_passed = settling_time is not None and settling_time <= max_settling_time
    
    print("\nCDAC Settling Time Test Results:")
    print(f"Expected final voltage: {expected_final:.2f}V")
    print(f"Measured settling time: {settling_time*1e9:.1f}ns")
    print(f"Maximum allowed: {max_settling_time*1e9:.1f}ns")
    
    if test_passed:
        print("\nTest_Passed: CDAC settles within required time")
    else:
        print("\nTest_Failed: Settling time exceeds specification")
    
    return test_passed

if __name__ == "__main__":
    test_cdac_settling_time()