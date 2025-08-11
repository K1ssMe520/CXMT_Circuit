import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.ClockDataRecovery import ClockDataRecovery
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_cdr_lock_range():
    circuit = Circuit('CDR Lock Range Test')
    
    # Power supply
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    
    # Add CDR circuit
    circuit.subcircuit(ClockDataRecovery())
    circuit.X('cdr', 'ClockDataRecovery', 'DataIn', 'Vctrl_Init', 
              'RecoveredClk', 'RecoveredData', circuit.gnd, 'VDD')
    
    # Test parameters
    initial_vctrl = 2.5@u_V
    min_freq = 500@u_kHz
    max_freq = 2@u_MHz
    freq_step = 100@u_kHz
    
    # Initial control voltage
    circuit.V('vctrl', 'Vctrl_Init', circuit.gnd, initial_vctrl)
    
    # Frequency sweep source
    circuit.V('data', 'DataIn', circuit.gnd, 'PULSE(0 5 0 1n 1n {} {}'.format(
        f'{(1/(2*max_freq))*1e9:.1f}n', f'{(1/max_freq)*1e9:.1f}n'))
    
    # Simulation setup
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    
    test_passed = True
    failure_reasons = []
    
    for freq in range(int(min_freq), int(max_freq)+int(freq_step), int(freq_step)):
        # Update data frequency
        period = 1/freq
        pulse_width = period/2
        circuit['Vdata'].parameters = {
            'initial_value': 0,
            'pulsed_value': 5,
            'rise_time': 1@u_ns,
            'fall_time': 1@u_ns,
            'pulse_width': pulse_width,
            'period': period
        }
        
        analysis = simulator.transient(step_time=10@u_ns, end_time=5*period)
        
        # Check lock condition (simplified)
        vctrl = analysis.internal_branches['vctrl']  # Assuming VCO control is accessible
        if min(vctrl) < 0.5 or max(vctrl) > 4.5:
            test_passed = False
            failure_reasons.append(
                f"Failed at {freq/1e6:.2f}MHz: Vctrl out of range "
                f"({min(vctrl):.2f}V to {max(vctrl):.2f}V)"
            )
    
    if test_passed:
        print(f"Test_Passed: Maintained lock from {min_freq/1e6:.1f}MHz to {max_freq/1e6:.1f}MHz")
    else:
        print("Test_Failed: Lost lock at some frequencies")
        for reason in failure_reasons:
            print(f"  • {reason}")
    
    return test_passed

if __name__ == "__main__":
    test_cdr_lock_range()