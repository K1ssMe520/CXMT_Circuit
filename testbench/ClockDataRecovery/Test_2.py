import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.ClockDataRecovery import ClockDataRecovery
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_cdr_jitter_tolerance():
    circuit = Circuit('CDR Jitter Tolerance Test')
    
    # Power supply
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    
    # Add CDR circuit
    circuit.subcircuit(ClockDataRecovery())
    circuit.X('cdr', 'ClockDataRecovery', 'DataIn', 'Vctrl_Init', 
              'RecoveredClk', 'RecoveredData', circuit.gnd, 'VDD')
    
    # Test parameters
    data_freq = 1@u_MHz
    initial_vctrl = 2.5@u_V
    jitter_amount = 0.1  # 10% jitter
    
    # Jittered input signal (approximated with modulated pulse width)
    circuit.V('data', 'DataIn', circuit.gnd, 'PULSE(0 5 0 1n 1n 450n 1u)')
    
    # Initial control voltage
    circuit.V('vctrl', 'Vctrl_Init', circuit.gnd, initial_vctrl)
    
    # Simulation setup
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.transient(step_time=10@u_ns, end_time=10@u_us)
    
    # Check clock stability (simplified)
    recovered_clk = analysis['RecoveredClk']
    period_measurements = []
    
    # Measure periods between rising edges
    threshold = 2.5
    crossings = []
    for i in range(1, len(recovered_clk)):
        if recovered_clk[i-1] < threshold <= recovered_clk[i]:
            crossings.append(analysis.time[i])
    
    if len(crossings) < 3:
        print("Test_Failed: Insufficient clock cycles detected")
        return False
    
    periods = [crossings[i] - crossings[i-1] for i in range(1, len(crossings))]
    avg_period = sum(periods) / len(periods)
    max_deviation = max(abs(p - avg_period) for p in periods)
    
    if max_deviation > jitter_amount * avg_period:
        print(f"Test_Failed: Excessive output jitter ({max_deviation/avg_period*100:.1f}%)")
        return False
    
    print("Test_Passed: Output jitter within acceptable limits")
    return True

if __name__ == "__main__":
    test_cdr_jitter_tolerance()