import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.Inverter import Inverter
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_inverter_propagation_delay():
    circuit = Circuit('Inverter Propagation Delay Test')
    
    # Setup power supply
    vdd_value = 5.0
    circuit.V('dd', 'VDD', circuit.gnd, vdd_value@u_V)
    
    # Add inverter with default parameters
    circuit.subcircuit(Inverter())
    circuit.X('inv', 'Inverter', 'Vin', 'Vout', circuit.gnd, 'VDD')
    
    # Create input pulse (1MHz square wave)
    circuit.PulseVoltageSource('in', 'Vin', circuit.gnd,
                              initial_value=0@u_V,
                              pulsed_value=vdd_value@u_V,
                              pulse_width=500@u_ns,
                              period=1@u_us)
    
    # Setup transient simulation
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.transient(step_time=1@u_ns, end_time=2@u_us)
    
    # Extract time points and signals
    time = np.array(analysis.time)
    vin = np.array(analysis['Vin'])
    vout = np.array(analysis['Vout'])
    
    # Define threshold for transition detection (50% of VDD)
    vth = vdd_value / 2
    
    # Find input rising and falling edges
    input_rising = np.where((vin[:-1] < vth) & (vin[1:] >= vth))[0]
    input_falling = np.where((vin[:-1] >= vth) & (vin[1:] < vth))[0]
    
    # Find corresponding output edges
    output_falling = np.where((vout[:-1] >= vth) & (vout[1:] < vth))[0]
    output_rising = np.where((vout[:-1] < vth) & (vout[1:] >= vth))[0]
    
    # Calculate propagation delays
    tphl = time[output_falling[0]] - time[input_rising[0]] if len(output_falling) > 0 else float('inf')
    tplh = time[output_rising[0]] - time[input_falling[0]] if len(output_rising) > 0 else float('inf')
    
    # Define maximum allowed propagation delay (200ps for this technology)
    max_delay = 200@u_ps
    
    # Check test results
    test_passed = True
    failure_reasons = []
    
    if tphl > max_delay:
        test_passed = False
        failure_reasons.append(f"tPHL ({tphl*1e9:.1f}ns) exceeds maximum allowed {max_delay*1e9:.1f}ns")
    
    if tplh > max_delay:
        test_passed = False
        failure_reasons.append(f"tPLH ({tplh*1e9:.1f}ns) exceeds maximum allowed {max_delay*1e9:.1f}ns")
    
    # Print test report
    print("\n" + "="*60)
    print("Inverter Propagation Delay Test Results")
    print("="*60)
    print(f"Measured Propagation Delays:")
    print(f"  tPHL (high-to-low): {tphl*1e9:.1f} ns")
    print(f"  tPLH (low-to-high): {tplh*1e9:.1f} ns")
    print(f"\nSpecification: Max delay = {max_delay*1e9:.1f} ns")
    
    if test_passed:
        print("\nTest_Passed: Both propagation delays within specification")
    else:
        print("\nTest_Failed: Propagation delay violations")
        for reason in failure_reasons:
            print(f"  • {reason}")
    
    return test_passed

if __name__ == "__main__":
    test_inverter_propagation_delay()