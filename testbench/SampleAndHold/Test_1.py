import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.SampleAndHold import SampleAndHold
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_hold_capacitor_leakage():
    circuit = Circuit('Hold Capacitor Leakage Test')
    
    # Power supply
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    
    # Add SampleAndHold subcircuit
    circuit.subcircuit(SampleAndHold())
    circuit.X('sh', 'SampleAndHold', 'Vin', 'Clk', 'Vsh', circuit.gnd, 'VDD')
    
    # Input voltage (DC)
    input_voltage = 2.5
    circuit.V('in', 'Vin', circuit.gnd, input_voltage@u_V)
    
    # Clock signal (single pulse with long hold time)
    circuit.V('clk', 'Clk', circuit.gnd, 'pulse(0 5 0 1n 1n 1u 100u)')
    
    # Simulation
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.transient(step_time=0.1@u_us, end_time=100@u_us)
    
    # Extract results
    time = np.array(analysis.time)
    clk = np.array(analysis['Clk'])
    vsh = np.array(analysis['Vsh'])
    
    # Find hold period (after clock falls)
    hold_start_idx = np.argmax(clk < 2.5)
    hold_vsh = vsh[hold_start_idx:]
    hold_time = time[hold_start_idx:] - time[hold_start_idx]
    
    # Calculate droop rate
    initial_hold_voltage = hold_vsh[0]
    final_voltage = hold_vsh[-1]
    voltage_droop = initial_hold_voltage - final_voltage
    droop_rate = voltage_droop / (hold_time[-1] - hold_time[0])
    
    # Test conditions
    test_passed = True
    max_allowed_droop = 0.01  # 10mV droop max
    max_allowed_droop_rate = 0.1  # 0.1V/ms max droop rate
    
    failure_reasons = []
    
    # Check total droop
    if voltage_droop > max_allowed_droop:
        test_passed = False
        failure_reasons.append(
            f"FAIL: Voltage droop {voltage_droop*1000:.2f}mV exceeds maximum allowed {max_allowed_droop*1000:.0f}mV"
        )
    
    # Check droop rate
    if droop_rate > max_allowed_droop_rate:
        test_passed = False
        failure_reasons.append(
            f"FAIL: Droop rate {droop_rate*1000:.2f}mV/ms exceeds maximum allowed {max_allowed_droop_rate*1000:.0f}mV/ms"
        )
    
    # Print test report
    print("\n" + "="*60)
    print("Hold Capacitor Leakage Test Results")
    print("="*60)
    
    print(f"Test Parameters:")
    print(f"  VDD = {vdd.dc_value}V")
    print(f"  Input Voltage = {input_voltage}V")
    print(f"  Hold Duration = {hold_time[-1]*1e6:.1f}µs")
    
    print("\nTest Measurements:")
    print(f"Initial hold voltage: {initial_hold_voltage:.3f}V")
    print(f"Final hold voltage: {final_voltage:.3f}V")
    print(f"Total voltage droop: {voltage_droop*1000:.2f}mV")
    print(f"Droop rate: {droop_rate*1000:.2f}mV/ms")
    
    print("\nTest Limits:")
    print(f"Max allowed droop: {max_allowed_droop*1000:.0f}mV")
    print(f"Max allowed droop rate: {max_allowed_droop_rate*1000:.0f}mV/ms")
    
    print("\n" + "-"*60)
    if test_passed:
        print("\nTest_Passed: Hold capacitor leakage within specifications")
    else:
        print("\nTest_Failed: Excessive hold capacitor leakage detected")
        for reason in failure_reasons:
            print(f"  • {reason}")
    
    return test_passed

if __name__ == "__main__":
    test_hold_capacitor_leakage()