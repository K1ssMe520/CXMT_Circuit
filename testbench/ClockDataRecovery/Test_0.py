import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.ClockDataRecovery import ClockDataRecovery
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_cdr_basic_functionality():
    circuit = Circuit('CDR Basic Functionality Test')
    
    # Power supply
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    
    # Add CDR circuit
    circuit.subcircuit(ClockDataRecovery())
    circuit.X('cdr', 'ClockDataRecovery', 'DataIn', 'Vctrl_Init', 
              'RecoveredClk', 'RecoveredData', circuit.gnd, 'VDD')
    
    # Test parameters
    data_freq = 1@u_MHz
    initial_vctrl = 2.5@u_V
    
    # Input data signal (square wave)
    circuit.V('data', 'DataIn', circuit.gnd, 'PULSE(0 5 0 1n 1n 500n 1u)')
    
    # Initial control voltage
    circuit.V('vctrl', 'Vctrl_Init', circuit.gnd, initial_vctrl)
    
    # Simulation setup
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.transient(step_time=10@u_ns, end_time=10@u_us)
    
    # Check lock condition (simplified check)
    # In a real test, we would compare phase alignment
    recovered_clk = analysis['RecoveredClk']
    data_in = analysis['DataIn']
    
    # Basic check for oscillation
    if (max(recovered_clk) - min(recovered_clk)) < 4.0:
        print("Test_Failed: Recovered clock not oscillating properly")
        return False
    
    print("Test_Passed: Basic functionality verified")
    return True

if __name__ == "__main__":
    test_cdr_basic_functionality()