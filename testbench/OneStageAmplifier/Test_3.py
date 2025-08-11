import sys
from pathlib import Path
root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

from modules.OneStageAmplifier import OneStageAmplifier
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_amplifier_impedances():
    circuit = Circuit('Amplifier Impedance Test')
    
    # Setup power supply and bias
    vdd_value = 5.0
    vbias_value = 1.0
    circuit.V('dd', 'VDD', circuit.gnd, vdd_value@u_V)
    circuit.V('bias', 'Vbias', circuit.gnd, vbias_value@u_V)
    
    # Add amplifier subcircuit
    rload = 10@u_kΩ
    circuit.subcircuit(OneStageAmplifier(
        nmos_width=10e-6,
        nmos_length=1e-6,
        load_resistance=rload,
        input_capacitance=1@u_uF,
        output_capacitance=1@u_uF
    ))
    
    # Test input impedance by adding series resistor
    rtest_in = 1@u_MΩ
    circuit.R('test_in', 'Vin_test', 'Vin', rtest_in)
    circuit.X('amp', 'OneStageAmplifier', 'Vin', 'Vbias', 'Vout', 'VDD', circuit.gnd)
    
    # Test output impedance by adding load resistor
    rtest_out = rload  # Same as amplifier's load for testing
    circuit.R('test_out', 'Vout', circuit.gnd, rtest_out)
    
    # AC input signal (1mV)
    circuit.VSIN('in', 'Vin_test', circuit.gnd, amplitude=1@u_mV, frequency=1@u_kHz)
    
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.ac(frequency=1@u_kHz, variation='dec', number_of_points=1, start_frequency=1@u_kHz, stop_frequency=1@u_kHz)
    
    # Calculate input impedance
    vin_test = analysis['Vin_test'].as_ndarray().item()
    vin = analysis['Vin'].as_ndarray().item()
    zin = (vin / (vin_test - vin)) * rtest_in
    
    # Calculate output impedance
    vout_open = analysis['Vout'].as_ndarray().item()  # Without Rtest_out
    # Need to run another simulation without Rtest_out to get open-circuit voltage
    circuit.remove_element('Rtest_out')
    analysis_open = simulator.ac(frequency=1@u_kHz, variation='dec', number_of_points=1, start_frequency=1@u_kHz, stop_frequency=1@u_kHz)
    vout_open = analysis_open['Vout'].as_ndarray().item()
    
    vout_loaded = analysis['Vout'].as_ndarray().item()
    zout = ((vout_open / vout_loaded) - 1) * rtest_out
    
    # Check results
    test_passed = True
    
    # Input impedance should be >> 1MΩ at 1kHz (dominated by Cin)
    if zin < 100@u_kΩ:
        test_passed = False
        print(f"Test_Failed: Input impedance {zin/1e6:.2f}MΩ is too low (expected >>100kΩ)")
    
    # Output impedance should be close to Rload
    zout_error = abs(zout - rload) / rload
    if zout_error > 0.2:  # 20% tolerance
        test_passed = False
        print(f"Test_Failed: Output impedance {zout/1e3:.1f}kΩ differs from Rload {rload/1e3:.1f}kΩ by more than 20%")
    
    if test_passed:
        print("Test_Passed: Impedances meet expectations")
        print(f"  Input impedance: {zin/1e6:.2f}MΩ")
        print(f"  Output impedance: {zout/1e3:.1f}kΩ (Rload = {rload/1e3:.1f}kΩ)")
    
    return test_passed

if __name__ == "__main__":
    test_amplifier_impedances()