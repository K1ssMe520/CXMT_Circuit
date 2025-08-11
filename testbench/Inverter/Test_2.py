import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.Inverter import Inverter
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_inverter_noise_margin():
    circuit = Circuit('Inverter Noise Margin Test')
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    circuit.subcircuit(Inverter())
    circuit.X('1', 'Inverter', 'Vin', 'Vout', circuit.gnd, 'VDD')
    
    input_source = circuit.V('in', 'Vin', circuit.gnd, 0@u_V)
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    
    analysis = simulator.dc(Vin=slice(0, 5, 0.01))
    
    vin = analysis.sweep.as_ndarray()
    vout = analysis['Vout'].as_ndarray()
    
    # Find transition points
    vih = vin[vout < 0.5][0]  # First point where output < 0.5V
    vil = vin[vout > 4.5][-1]  # Last point where output > 4.5V
    
    test_passed = True
    
    # Check reasonable noise margins
    if vil > 1.5:  # Typical NMOS threshold is around 0.7V
        test_passed = False
        print(f"FAIL: VIL too high ({vil:.2f}V)")
    
    if vih < 3.5:  # Typical PMOS threshold is around VDD-0.7V
        test_passed = False
        print(f"FAIL: VIH too low ({vih:.2f}V)")
    
    if test_passed:
        print(f"Test_Passed: Noise margins acceptable (VIL={vil:.2f}V, VIH={vih:.2f}V)")
    else:
        print(f"Test_Failed: Noise margin issues detected")
    
    return test_passed

if __name__ == "__main__":
    test_inverter_noise_margin()