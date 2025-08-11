import sys
from pathlib import Path
root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

from modules.OneStageAmplifier import OneStageAmplifier
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_amplifier_dc_operating_point():
    circuit = Circuit('Amplifier DC Test')
    
    # Setup power supply and bias
    vdd_value = 5.0
    vbias_value = 1.0  # Typical bias voltage
    circuit.V('dd', 'VDD', circuit.gnd, vdd_value@u_V)
    circuit.V('bias', 'Vbias', circuit.gnd, vbias_value@u_V)
    
    # Add amplifier subcircuit
    circuit.subcircuit(OneStageAmplifier(
        nmos_width=10e-6,
        nmos_length=1e-6,
        load_resistance=10@u_kΩ,
        input_capacitance=1@u_uF,
        output_capacitance=1@u_uF
    ))
    circuit.X('amp', 'OneStageAmplifier', 'Vin', 'Vbias', 'Vout', 'VDD', circuit.gnd)
    
    # Set input to 0V for DC test
    circuit.V('in', 'Vin', circuit.gnd, 0@u_V)
    
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.operating_point()
    
    # Get output voltage
    vout = analysis['Vout'].as_ndarray().item()
    
    # Expected output range (should be between VDD and ground)
    min_expected = 0.1 * vdd_value
    max_expected = 0.9 * vdd_value
    
    # Check if output is in expected range
    if min_expected <= vout <= max_expected:
        print(f"Test_Passed: Vout = {vout:.3f}V is within expected range ({min_expected:.1f}V to {max_expected:.1f}V)")
        return True
    else:
        print(f"Test_Failed: Vout = {vout:.3f}V is outside expected range ({min_expected:.1f}V to {max_expected:.1f}V)")
        return False

if __name__ == "__main__":
    test_amplifier_dc_operating_point()