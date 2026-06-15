import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.Inverter import Inverter
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_inverter_power_consumption():
    circuit = Circuit('Inverter Power Consumption Test')
    
    # Setup power supply
    vdd_value = 5.0
    vdd = circuit.V('dd', 'VDD', circuit.gnd, vdd_value@u_V)
    
    # Add inverter
    circuit.subcircuit(Inverter())
    circuit.X('inv', 'Inverter', 'Vin', 'Vout', circuit.gnd, 'VDD')
    
    # Test 1: Static power (DC analysis)
    print("Running static power test...")
    circuit.V('in_static', 'Vin', circuit.gnd, 0@u_V)  # Start with input low
    
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    static_analysis_low = simulator.operating_point()
    current_low = static_analysis_low['Vdd'].as_ndarray().item()
    
    # Change input to high
    circuit['Vin_static'].dc_value = vdd_value@u_V
    static_analysis_high = simulator.operating_point()
    current_high = static_analysis_high['Vdd'].as_ndarray().item()
    
    # Test 2: Dynamic power (transient analysis)
    print("Running dynamic power test...")
    circuit.remove_voltage_source('Vin_static')
    circuit.PulseVoltageSource('in_dyn', 'Vin', circuit.gnd,
                             initial_value=0@u_V,
                             pulsed_value=vdd_value@u_V,
                             pulse_width=500@u_ns,
                             period=1@u_us)
    
    analysis = simulator.transient(step_time=1@u_ns, end_time=2@u_us)
    time = np.array(analysis.time)
    current = np.array(analysis['Vdd'])
    
    # Calculate average dynamic current
    avg_current = np.mean(current)
    
    # Define specifications
    max_leakage = 1@u_nA  # Maximum allowed leakage current
    max_avg_current = 100@u_uA  # Maximum average current
    
    # Check test results
    test_passed = True
    failure_reasons = []
    
    if abs(current_low) > max_leakage:
        test_passed = False
        failure_reasons.append(f"Input low leakage current ({current_low*1e6:.2f}µA) exceeds {max_leakage*1e6:.2f}µA")
    
    if abs(current_high) > max_leakage:
        test_passed = False
        failure_reasons.append(f"Input high leakage current ({current_high*1e6:.2f}µA) exceeds {max_leakage*1e6:.2f}µA")
    
    if avg_current > max_avg_current:
        test_passed = False
        failure_reasons.append(f"Average dynamic current ({avg_current*1e6:.2f}µA) exceeds {max_avg_current*1e6:.2f}µA")
    
    # Print test report
    print("\n" + "="*60)
    print("Inverter Power Consumption Test Results")
    print("="*60)
    print("Static Power Measurements:")
    print(f"  Input Low (0V):  {current_low*1e6:.2f} µA")
    print(f"  Input High (5V): {current_high*1e6:.2f} µA")
    print(f"\nDynamic Power Measurement:")
    print(f"  Average current: {avg_current*1e6:.2f} µA")
    print(f"\nSpecifications:")
    print(f"  Max leakage: {max_leakage*1e6:.2f} µA")
    print(f"  Max avg current: {max_avg_current*1e6:.2f} µA")
    
    if test_passed:
        print("\nTest_Passed: All power consumption within specifications")
    else:
        print("\nTest_Failed: Power consumption violations")
        for reason in failure_reasons:
            print(f"  • {reason}")
    
    return test_passed

if __name__ == "__main__":
    test_inverter_power_consumption()