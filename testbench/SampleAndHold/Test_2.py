import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.SampleAndHold import SampleAndHold
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_ac_signal_tracking():
    circuit = Circuit('AC Signal Tracking Test')
    
    # Power supply
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    
    # Add SampleAndHold subcircuit
    circuit.subcircuit(SampleAndHold())
    circuit.X('sh', 'SampleAndHold', 'Vin', 'Clk', 'Vsh', circuit.gnd, 'VDD')
    
    # AC input signal (sine wave)
    circuit.VSIN('in', 'Vin', circuit.gnd, amplitude=1@u_V, frequency=1@u_kHz)
    
    # Clock signal (sampling at 10kHz)
    circuit.V('clk', 'Clk', circuit.gnd, 'pulse(0 5 0 1n 1n 50u 100u)')
    
    # Simulation
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.transient(step_time=0.1@u_us, end_time=500@u_us)
    
    # Extract results
    time = np.array(analysis.time)
    vin = np.array(analysis['Vin'])
    clk = np.array(analysis['Clk'])
    vsh = np.array(analysis['Vsh'])
    
    # Test conditions
    test_passed = True
    tolerance = 0.05 * vdd.dc_value
    failure_reasons = []
    
    # Find sampling and holding periods
    sampling_mask = clk > 2.5
    holding_mask = clk <= 2.5
    
    # 1. Check sampling phase accuracy
    sampling_error = np.abs(vsh[sampling_mask] - vin[sampling_mask])
    max_sampling_error = np.max(sampling_error)
    
    if max_sampling_error > tolerance:
        test_passed = False
        failure_reasons.append(
            f"FAIL: Max sampling error {max_sampling_error*1000:.2f}mV exceeds tolerance {tolerance*1000:.0f}mV"
        )
    
    # 2. Check holding phase stability
    if np.sum(holding_mask) > 1:
        holding_variation = np.max(np.abs(np.diff(vsh[holding_mask])))
        if holding_variation > tolerance/10:
            test_passed = False
            failure_reasons.append(
                f"FAIL: Holding phase variation {holding_variation*1000:.2f}mV exceeds limit {tolerance*1000/10:.0f}mV"
            )
    
    # Print test report
    print("\n" + "="*60)
    print("AC Signal Tracking Test Results")
    print("="*60)
    
    print(f"Test Parameters:")
    print(f"  VDD = {vdd.dc_value}V")
    print(f"  Input Signal: 1V amplitude, 1kHz sine wave")
    print(f"  Sampling Rate: 10kHz")
    print(f"  Tolerance: ±{tolerance*1000:.0f}mV")
    
    print("\nTest Measurements:")
    print(f"Max sampling error: {max_sampling_error*1000:.2f}mV")
    if np.sum(holding_mask) > 1:
        print(f"Max holding variation: {holding_variation*1000:.2f}mV")
    
    print("\n" + "-"*60)
    if test_passed:
        print("\nTest_Passed: AC signal tracking performance meets requirements")
    else:
        print("\nTest_Failed: Issues found in AC signal tracking")
        for reason in failure_reasons:
            print(f"  • {reason}")
    
    return test_passed

if __name__ == "__main__":
    test_ac_signal_tracking()