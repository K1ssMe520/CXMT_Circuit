import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.Inverter import Inverter
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_inverter_noise_margin():
    circuit = Circuit('Inverter Noise Margin Test')
    
    # Setup power supply
    vdd_value = 5.0
    circuit.V('dd', 'VDD', circuit.gnd, vdd_value@u_V)
    
    # Add inverter
    circuit.subcircuit(Inverter())
    circuit.X('inv', 'Inverter', 'Vin', 'Vout', circuit.gnd, 'VDD')
    
    # Setup DC sweep
    input_source = circuit.V('in', 'Vin', circuit.gnd, 0@u_V)
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.dc(Vin=slice(0, vdd_value, 0.01))
    
    # Extract VTC curve
    vin = np.array(analysis.sweep)
    vout = np.array(analysis['Vout'])
    
    # Calculate derivative (gain)
    dvout_dvin = np.diff(vout) / np.diff(vin)
    
    # Find unity gain points
    unity_gain_points = np.where(np.abs(dvout_dvin) >= 0.98)[0]  # Allow 2% tolerance
    
    if len(unity_gain_points) < 2:
        print("\nTest_Failed: Could not find two unity gain points in VTC curve")
        return False
    
    # Get noise margins
    vil = vin[unity_gain_points[0]]
    voh = vout[unity_gain_points[0]]
    vih = vin[unity_gain_points[-1]]
    vol = vout[unity_gain_points[-1]]
    
    nm_l = vil - vol  # Noise margin low
    nm_h = voh - vih  # Noise margin high
    
    # Define minimum acceptable noise margins
    min_noise_margin = 0.5  # 0.5V minimum noise margin
    
    # Check test results
    test_passed = True
    failure_reasons = []
    
    if nm_l < min_noise_margin:
        test_passed = False
        failure_reasons.append(f"Low noise margin ({nm_l:.2f}V) below {min_noise_margin}V")
    
    if nm_h < min_noise_margin:
        test_passed = False
        failure_reasons.append(f"High noise margin ({nm_h:.2f}V) below {min_noise_margin}V")
    
    # Print test report
    print("\n" + "="*60)
    print("Inverter Noise Margin Test Results")
    print("="*60)
    print("Critical Voltage Points:")
    print(f"  VIL (input low): {vil:.2f}V")
    print(f"  VIH (input high): {vih:.2f}V")
    print(f"  VOL (output low): {vol:.2f}V")
    print(f"  VOH (output high): {voh:.2f}V")
    print(f"\nNoise Margins:")
    print(f"  NM_L (low): {nm_l:.2f}V")
    print(f"  NM_H (high): {nm_h:.2f}V")
    print(f"\nSpecification: Min noise margin = {min_noise_margin}V")
    
    if test_passed:
        print("\nTest_Passed: Both noise margins meet specification")
    else:
        print("\nTest_Failed: Noise margin violations")
        for reason in failure_reasons:
            print(f"  • {reason}")
    
    return test_passed

if __name__ == "__main__":
    test_inverter_noise_margin()