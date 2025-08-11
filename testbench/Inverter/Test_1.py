import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from netlist.Inverter import Inverter
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

def test_inverter_transient():
    circuit = Circuit('Inverter Transient Test')
    vdd = circuit.V('dd', 'VDD', circuit.gnd, 5@u_V)
    circuit.subcircuit(Inverter())
    circuit.X('1', 'Inverter', 'Vin', 'Vout', circuit.gnd, 'VDD')
    
    input_source = circuit.PulseVoltageSource(
        'in', 'Vin', circuit.gnd,
        initial_value=0@u_V, pulsed_value=5@u_V,
        pulse_width=500@u_ns, period=1@u_us
    )
    
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.transient(step_time=10@u_ns, end_time=2@u_us)
    
    # Check output inversion
    time = analysis.time.as_ndarray()
    vin = analysis['Vin'].as_ndarray()
    vout = analysis['Vout'].as_ndarray()
    
    test_passed = True
    
    # Check high-to-low transition
    high_time = time[(vin > 2.5) & (vout > 2.5)]
    if len(high_time) > 0:
        test_passed = False
        print(f"FAIL: Output remains high when input is high for {len(high_time)} points")
    
    # Check low-to-high transition
    low_time = time[(vin < 2.5) & (vout < 2.5)]
    if len(low_time) > 0:
        test_passed = False
        print(f"FAIL: Output remains low when input is low for {len(low_time)} points")
    
    if test_passed:
        print("Test_Passed: Transient response meets inversion requirements")
    else:
        print("Test_Failed: Transient response issues detected")
    
    return test_passed

if __name__ == "__main__":
    test_inverter_transient()