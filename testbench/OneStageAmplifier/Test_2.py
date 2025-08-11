import sys
from pathlib import Path
root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

from modules.OneStageAmplifier import OneStageAmplifier
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_amplifier_frequency_response():
    circuit = Circuit('Amplifier Frequency Response Test')
    
    # Setup power supply and bias
    vdd_value = 5.0
    vbias_value = 1.0
    circuit.V('dd', 'VDD', circuit.gnd, vdd_value@u_V)
    circuit.V('bias', 'Vbias', circuit.gnd, vbias_value@u_V)
    
    # Add amplifier subcircuit with known capacitors
    cin = 1@u_uF
    cout = 1@u_uF
    rload = 10@u_kΩ
    circuit.subcircuit(OneStageAmplifier(
        nmos_width=10e-6,
        nmos_length=1e-6,
        load_resistance=rload,
        input_capacitance=cin,
        output_capacitance=cout
    ))
    circuit.X('amp', 'OneStageAmplifier', 'Vin', 'Vbias', 'Vout', 'VDD', circuit.gnd)
    
    # AC input (1mV)
    circuit.V('in', 'Vin', circuit.gnd, 0@u_V)
    circuit.Sinusoidal('in', 'Vin', circuit.gnd, amplitude=1@u_mV)
    
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    
    # Run AC analysis over wide frequency range
    analysis = simulator.ac(start_frequency=1@u_Hz, stop_frequency=100@u_MHz, number_of_points=100, variation='dec')
    
    # Find mid-band gain (should be around 1kHz)
    midband_idx = 30  # Approximately 1kHz in our sweep
    midband_gain = abs(analysis['Vout'][midband_idx] / abs(analysis['Vin'][midband_idx])
    
    # Find -3dB points
    low_freq = None
    high_freq = None
    
    for i in range(len(analysis.frequency)):
        current_gain = abs(analysis['Vout'][i] / analysis['Vin'][i])
        if current_gain < 0.707 * midband_gain:
            if analysis.frequency[i] < 1@u_kHz:
                low_freq = analysis.frequency[i]
            else:
                high_freq = analysis.frequency[i]
            break
    
    # Check if frequency response meets expectations
    test_passed = True
    
    # Check low frequency cutoff (should be below 100Hz with 1uF caps)
    if low_freq is not None and low_freq > 100:
        test_passed = False
        print(f"Test_Failed: Low frequency cutoff {low_freq:.1f}Hz is too high (expected <100Hz)")
    
    # Check high frequency cutoff (should be above 1MHz)
    if high_freq is not None and high_freq < 1@u_MHz:
        test_passed = False
        print(f"Test_Failed: High frequency cutoff {high_freq/1e6:.2f}MHz is too low (expected >1MHz)")
    
    if test_passed:
        print("Test_Passed: Frequency response meets expectations")
        print(f"  Low cutoff: {'<100Hz' if low_freq is None else f'{low_freq:.1f}Hz'}")
        print(f"  High cutoff: {'>1MHz' if high_freq is None else f'{high_freq/1e6:.2f}MHz'}")
    
    return test_passed

if __name__ == "__main__":
    test_amplifier_frequency_response()