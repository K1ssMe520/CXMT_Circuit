## Module Functionality Test Prompt

Please list the basic test items to ensure the [Model] circuit module is functioning properly, along with the corresponding PySpice code for each test item. Below is a reference template for question input and answer.

### Model Description

Model: Inverter

Description: Digital inverter, completes voltage inversion of digital levels

Input Nodes: Vin (input digital signal), VDD (positive power supply voltage), GND (ground connection)

Output Nodes: Vout (inverted output digital signal)

Structure Description: The inverter is a basic digital logic gate that inverts the input signal. It consists of a PMOS transistor connected between the power supply (VDD) and the output (Vout), and an NMOS transistor connected between the output and ground (GND). When the input (Vin) is high, the NMOS turns on and pulls the output low, while the PMOS turns off. When the input is low, the PMOS turns on and pulls the output high, while the NMOS turns off.

Parameter Description: 
- nmos_width: Channel width of the NMOS transistor, Raising this value increases the NMOS drive strength, but also enlarges the area and raises parasitic capacitances.
- pmos_width: Channel width of the PMOS transistor. Increasing it enhances the PMOS drive capability and improves the rising-edge speed, yet it expands the area and raises power consumption
- channel_length: MOSFET channel length. Shortening it boosts switching speed but aggravates short-channel effects; lengthening it reduces leakage current.
- load_capacitance: Capacitive load at the output node. Larger values slow the switching transients and increase propagation delay; setting it to 0 removes the load capacitor.


### Test Item Code

#### Test_Item 01

```markdown
Power supply condition test: The test method involves performing a DC operating point analysis. Set the input to low level (0V) and high level (Vdd) respectively. Check if the output is close to Vdd when the input is low, and close to 0V when the input is high. This verifies the static operating point of the inverter.
```

```python
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.Inverter import Inverter
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory

def test_inverter_static():
    circuit = Circuit('Inverter Static Test')
  
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    circuit.subcircuit(Inverter())
    circuit.X('1', 'Inverter01', 'Vin', 'Vout', circuit.gnd, 'VDD')
  
    input_source = circuit.V('in', 'Vin', circuit.gnd, 0@u_V)
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    test_conditions = [
        {'Vin': 0.0, 'expected_Vout': 5.0}, 
        {'Vin': 5.0, 'expected_Vout': 0.0} ]
  
    tolerance = 0.05
  
    all_passed = True
    detailed_results = []
  
    for test in test_conditions:
        input_source.dc_value = test['Vin']@u_V
  
        analysis = simulator.operating_point()
  
        vout = analysis['Vout'].as_ndarray().item()
        expected = test['expected_Vout']
  
        expected_min = expected - vdd.dc_value * tolerance
        expected_max = expected + vdd.dc_value * tolerance
  
        in_range = expected_min <= vout <= expected_max
  
        detailed_results.append({
            'Vin': test['Vin'],
            'Vout': vout,
            'expected': expected,
            'in_range': in_range,
            'min': expected_min,
            'max': expected_max
        })
  
        if not in_range:
            all_passed = False
  
    print("\nDetailed Test Results:")
    print("Vin (V)\tVout (V)\tExpected (V)\tMin (V)\tMax (V)\tStatus")
    for result in detailed_results:
        status = "PASS" if result['in_range'] else "FAIL"
        print(f"{result['Vin']:.1f}\t{result['Vout']:.3f}\t\t{result['expected']:.1f}\t\t{result['min']:.2f}\t{result['max']:.2f}\t{status}")
  
    if all_passed:
        print("\nTest_Passed: All conditions met within tolerance")
    else:
        print("\nTest_Failed: One or more conditions outside tolerance range")
  
    return all_passed

if __name__ == "__main__":
    test_inverter_static()
```

#### Test_Item 02

```markdown
Transistor threshold voltage condition test: The test method uses a DC sweep analysis to scan the input voltage from 0V to Vdd. Observe if the output voltage changes as expected. Specifically, the output should be close to Vdd when the input is below the NMOS threshold voltage, and close to 0V when the input is above the NMOS threshold voltage.
```

```python
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.Inverter import Inverter
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_inverter_threshold_condition():
    # Create circuit
    circuit = Circuit('Inverter Threshold Condition Test')
  
    # Set power supply voltage
    vdd_value = 5.0
    vdd = circuit.V('dd', 'VDD', circuit.gnd, vdd_value@u_V)
  
    # Add inverter subcircuit
    circuit.subcircuit(Inverter(
        nmos_width=0.5e-6,
        pmos_width=1e-6,
        channel_length=0.18e-6,
        load_capacitance=10e-15
    ))
    circuit.X('inv', 'Inverter', 'Vin', 'Vout', circuit.gnd, 'VDD')
  
    # Add input voltage source for DC sweep
    input_source = circuit.V('in', 'Vin', circuit.gnd, 0@u_V)
  
    # Setup simulator
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
  
    # Perform DC sweep analysis
    print("Running DC sweep analysis...")
    analysis = simulator.dc(Vin=slice(0, vdd_value, 0.01))  # 0V to VDD, 0.01V steps
  
    # Extract results
    vin = np.array(analysis.sweep)
    vout = np.array(analysis['Vout'])
  
    # Define MOSFET threshold voltages
    vth_nmos = 0.5  # NMOS threshold voltage
    vth_pmos = vdd_value - 0.5  # Effective PMOS threshold (VDD - |Vth_p|)
  
    # Analyze behavior in threshold regions
    # 1. When Vin < NMOS threshold, Vout should be near VDD
    low_vin_mask = vin < vth_nmos
    vout_low_vin = vout[low_vin_mask]
  
    # 2. When Vin > PMOS threshold, Vout should be near 0V
    high_vin_mask = vin > vth_pmos
    vout_high_vin = vout[high_vin_mask]
  
    # Set tolerance
    tolerance = 0.05 * vdd_value  # 5% tolerance
  
    # Check test results
    test_passed = True
    failure_reasons = []
  
    # Check low input voltage region
    if not np.all(vout_low_vin >= (vdd_value - tolerance)):
        test_passed = False
        min_vout = np.min(vout_low_vin)
        failure_reasons.append(
            f"FAIL: When Vin < {vth_nmos}V, output should be high (~{vdd_value}V), "
            f"but min Vout = {min_vout:.3f}V"
        )
  
    # Check high input voltage region
    if not np.all(vout_high_vin <= tolerance):
        test_passed = False
        max_vout = np.max(vout_high_vin)
        failure_reasons.append(
            f"FAIL: When Vin > {vth_pmos:.2f}V, output should be low (~0V), "
            f"but max Vout = {max_vout:.3f}V"
        )
  
    # Check transition region monotonicity
    transition_region = (vin >= vth_nmos) & (vin <= vth_pmos)
    if not np.all(np.diff(vout[transition_region]) < 0):
        test_passed = False
        failure_reasons.append("FAIL: Output voltage not monotonically decreasing in transition region")
  
    # Print detailed test report
    print("\n" + "="*60)
    print("Inverter Threshold Voltage Condition Test Results")
    print("="*60)
  
    print(f"Test Parameters:")
    print(f"  VDD = {vdd_value}V")
    print(f"  NMOS Threshold = {vth_nmos}V")
    print(f"  PMOS Threshold = {vth_pmos:.2f}V")
    print(f"  Tolerance = ±{tolerance:.2f}V")
  
    print("\nRegion Checks:")
    print(f"1. Low Input Region (Vin < {vth_nmos}V):")
    print(f"   Expected Vout > {vdd_value - tolerance:.2f}V")
    print(f"   Actual Min Vout = {np.min(vout_low_vin):.3f}V")
  
    print(f"\n2. High Input Region (Vin > {vth_pmos:.2f}V):")
    print(f"   Expected Vout < {tolerance:.2f}V")
    print(f"   Actual Max Vout = {np.max(vout_high_vin):.3f}V")
  
    print("\n3. Transition Region Monotonicity:")
    transition_vout = vout[transition_region]
    monotonic = np.all(np.diff(transition_vout) < 0)
    print(f"   Monotonic decreasing: {'Yes' if monotonic else 'No'}")
  
    print("\n" + "-"*60)
    if test_passed:
        print("\nTest_Passed: All threshold voltage conditions met")
    else:
        print("\nTest_Failed: One or more threshold conditions failed")
        for reason in failure_reasons:
            print(f"  • {reason}")
  
    return test_passed

if __name__ == "__main__":
  
    test_result = test_inverter_threshold_condition()
```

Additional notes not included in the response:

1. Users only enter the Mode Description section, and you need to answer the Test Item Code sections accordingly.
2. Each Test Item section includes a desciption (markdown) and a testcode (python)
3. The default test voltage for VDD is 5V.
4. Please do not generate code for plotting output waveforms or storing waveform data.
5. Use "Test_Passed" as the indicator if the test is successful, and "Test_Failed" if the test is unsuccessful.
6. It is forbidden to read the voltage value in this way: vout = float(analysis['Vout']).
7. Please create an AC signal in the following way: circuit.VSIN('in', 'Vin', circuit.gnd, amplitude=1@u_V, frequency=1@u_kHz)

Here is the specific input:

### Model Description

Model: [Model]

Description: [Description]

Input Nodes: [InputNode]

Ouput Nodes: [OutputNode]

Structure Description: [Structure_Des]


