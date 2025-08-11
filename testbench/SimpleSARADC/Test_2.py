import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.SimpleSARADC import SimpleSARADC
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_conversion_sequence():
    circuit = Circuit('SARADC Conversion Sequence Test')
    
    # Power supplies
    circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    circuit.V('refp', 'Vrefp', circuit.gnd, 5@u_V)
    circuit.V('refn', 'Vrefn', circuit.gnd, 0@u_V)
    
    # Input signals
    circuit.V('in', 'Vin', circuit.gnd, 3.125@u_V)  # Test input (should result in 1010)
    circuit.PulseVoltageSource('clk', 'Clk', circuit.gnd,
                              initial_value=0@u_V, pulsed_value=5@u_V,
                              pulse_width=100@u_ns, period=200@u_ns,
                              rise_time=1@u_ns, fall_time=1@u_ns)
    circuit.PulseVoltageSource('start', 'Start', circuit.gnd,
                              initial_value=0@u_V, pulsed_value=5@u_V,
                              pulse_width=10@u_ns, period=1000@u_ns,
                              rise_time=1@u_ns, fall_time=1@u_ns)
    
    # Add SARADC
    circuit.subcircuit(SimpleSARADC())
    circuit.X('1', 'SimpleSARADC', 'Vin', 'Clk', 'Vrefp', 'Vrefn', 'Start',
              'Dout0', 'Dout1', 'Dout2', 'Dout3', 'EOC', circuit.gnd, 'VDD')
    
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.transient(step_time=10@u_ns, end_time=1000@u_ns)
    
    # Check final output (after EOC goes high)
    eoc = analysis['EOC']
    final_time = analysis.time[np.where(eoc > 2.5)[0][0]]
    
    # Get digital outputs at final time
    dout0 = analysis['Dout0'].at(final_time)
    dout1 = analysis['Dout1'].at(final_time)
    dout2 = analysis['Dout2'].at(final_time)
    dout3 = analysis['Dout3'].at(final_time)
    
    # Expected output for 3.125V input (1010)
    expected_output = [1, 0, 1, 0]
    measured_output = [
        1 if dout0 > 2.5 else 0,
        1 if dout1 > 2.5 else 0,
        1 if dout2 > 2.5 else 0,
        1 if dout3 > 2.5 else 0
    ]
    
    print("\nConversion Sequence Test Results:")
    print(f"Input Voltage: 3.125V")
    print(f"Expected Output: {expected_output}")
    print(f"Measured Output: {measured_output}")
    
    if measured_output == expected_output:
        print("\nTest_Passed: Conversion sequence completed correctly")
        return True
    else:
        print("\nTest_Failed: Incorrect digital output")
        return False

if __name__ == "__main__":
    test_conversion_sequence()