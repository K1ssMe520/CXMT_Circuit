import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.SampleAndHold import SampleAndHold
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_sample_hold_basic():
    circuit = Circuit('Sample and Hold Basic Test')
    
    # Power supply
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    
    # Add SampleAndHold subcircuit
    circuit.subcircuit(SampleAndHold())
    circuit.X('sh', 'SampleAndHold', 'Vin', 'Clk', 'Vsh', circuit.gnd, 'VDD')
    
    # Input voltage (DC)
    input_voltage = 3.3
    circuit.V('in', 'Vin', circuit.gnd, input_voltage@u_V)
    
    # Clock signal (square wave)
    circuit.V('clk', 'Clk', circuit.gnd, 'pulse(0 5 0 1n 1n 5u 10u)')
    
    # Simulation
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.transient(step_time=0.1@u_us, end_time=30@u_us)
    
    # Extract results
    time = np.array(analysis.time)
    clk = np.array(analysis['Clk'])
    vsh = np.array(analysis['Vsh'])
    
    # Test conditions
    test_passed = True
    failure_reasons = []
    
    # Check sampling phase (clock high)
    sampling_mask = clk > 2.5
    vsh_sampling = vsh[sampling_mask]
    
    # Check holding phase (clock low)
    holding_mask = clk <= 2.5
    vsh_holding = vsh[holding_mask]
    
    # Tolerance
    tolerance = 0.05 * vdd.dc_value
    
    # 1. During sampling phase, output should follow input
    if not np.all(np.abs(vsh_sampling - input_voltage) <= tolerance):
        test_passed = False
        max_error = np.max(np.abs(vsh_sampling - input_voltage))
        failure_reasons.append(
            f"FAIL: During sampling phase, output should be {input_voltage}V ±{tolerance:.2f}V, "
            f"but max error was {max_error:.3f}V"
        )
    
    # 2. During holding phase, output should be stable
    if len(vsh_holding) > 1:
        vsh_diff = np.diff(vsh_holding)
        if np.max(np.abs(vsh_diff)) > tolerance/10:  # Stricter tolerance for stability
            test_passed = False
            max_diff = np.max(np.abs(vsh_diff))
            failure_reasons.append(
                f"FAIL: During holding phase, output should be stable, "
                f"but max variation was {max_diff:.3f}V"
            )
    
    # Print test report
    print("\n" + "="*60)
    print("Sample and Hold Basic Functionality Test Results")
    print("="*60)
    
    print(f"Test Parameters:")
    print(f"  VDD = {vdd.dc_value}V")
    print(f"  Input Voltage = {input_voltage}V")
    print(f"  Tolerance = ±{tolerance:.2f}V")
    
    print("\nTest Checks:")
    print(f"1. Sampling Phase (Clk high):")
    print(f"   Expected Vsh = {input_voltage}V ±{tolerance:.2f}V")
    print(f"   Actual range: {np.min(vsh_sampling):.3f}V to {np.max(vsh_sampling):.3f}V")
    
    print(f"\n2. Holding Phase (Clk low):")
    print(f"   Expected stable output")
    if len(vsh_holding) > 1:
        print(f"   Actual variation: {np.max(np.abs(np.diff(vsh_holding)):.3f}V")
    
    print("\n" + "-"*60)
    if test_passed:
        print("\nTest_Passed: Basic sampling and holding functionality verified")
    else:
        print("\nTest_Failed: Issues found in basic functionality")
        for reason in failure_reasons:
            print(f"  • {reason}")
    
    return test_passed

if __name__ == "__main__":
    test_sample_hold_basic()