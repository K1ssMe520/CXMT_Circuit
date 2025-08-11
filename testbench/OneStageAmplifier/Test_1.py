import sys
from pathlib import Path
root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

from modules.OneStageAmplifier import OneStageAmplifier
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_amplifier_ac_gain():
    circuit = Circuit('Amplifier AC Gain Test')
    
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
    circuit.X('amp', 'OneStageAmplifier', 'Vin', 'Vbias', 'Vout', 'VDD', circuit.gnd)
    
    # Setup AC input signal (1mV amplitude)
    circuit.VSIN('in', 'Vin', circuit.gnd, amplitude=1@u_mV, frequency=1@u_kHz)
    
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    
    # Run AC analysis at signal frequency
    analysis = simulator.ac(frequency=1@u_kHz, variation='dec', number_of_points=1,  start_frequency=1@u_kHz, stop_frequency=1@u_kHz)
    
    # Calculate gain (Vout/Vin)
    vout = analysis['Vout'].as_ndarray().item()
    vin = analysis['Vin'].as_ndarray().item()
    gain = vout / vin
    
    # Expected gain range (approximate)
    expected_min_gain = -20  # Conservative estimate
    expected_max_gain = -5   # Conservative estimate
    
    if expected_min_gain <= gain <= expected_max_gain:
        print(f"Test_Passed: Gain = {gain:.1f} is within expected range ({expected_min_gain} to {expected_max_gain})")
        return True
    else:
        print(f"Test_Failed: Gain = {gain:.1f} is outside expected range ({expected_min_gain} to {expected_max_gain})")
        return False

if __name__ == "__main__":
    test_amplifier_ac_gain()