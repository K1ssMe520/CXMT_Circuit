import sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

# Create inverter test circuit
circuit = Circuit('Inverter Testbench')

# Define MOSFET model parameters
circuit.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
circuit.model('pmos_model', 'pmos', level=1, kp=40e-6, vto=-0.5)

# Power supply configuration
circuit.V('dd', 'VDD', circuit.gnd, 1.8@u_V)  # 1.8V power supply

# Input pulse signal (period=2ns, 50% duty cycle)
circuit.PulseVoltageSource('in', 'Vin', circuit.gnd,
                          initial_value=0, pulsed_value=1.8,
                          pulse_width=1@u_ns, period=2@u_ns,
                          rise_time=10@u_ps, fall_time=10@u_ps)

# Create inverter using MOSFETs
circuit.MOSFET(1, 'Vout', 'Vin', 'VDD', 'VDD', model='pmos_model', w=1@u_um, l=0.18@u_um)
circuit.MOSFET(2, 'Vout', 'Vin', circuit.gnd, circuit.gnd, model='nmos_model', w=0.5@u_um, l=0.18@u_um)

# Simulation setup
simulator = circuit.simulator()
analysis = simulator.transient(step_time=1@u_ps, end_time=5@u_ns)

# Extract waveform results
time = np.array(analysis.time) * 1e9  # Convert to nanoseconds
vin = np.array(analysis['Vin'])
vout = np.array(analysis['Vout'])

# Plot waveforms
plt.figure(figsize=(10, 6))
plt.title('Inverter Characteristics')
plt.plot(time, vin, label='Input (Vin)')
plt.plot(time, vout, label='Output (Vout)')
plt.xlabel('Time (ns)')
plt.ylabel('Voltage (V)')
plt.legend()
plt.grid(True)

# Add annotations
plt.annotate('PMOS ON\nNMOS OFF', xy=(0.5, 1.7), xytext=(0.5, 1.3),
             arrowprops=dict(facecolor='black', shrink=0.05))
plt.annotate('PMOS OFF\nNMOS ON', xy=(1.5, 0.1), xytext=(1.5, 0.5),
             arrowprops=dict(facecolor='black', shrink=0.05))

plt.tight_layout()
plt.savefig('inverter_simulation.png')
plt.show()

# Calculate propagation delay
# Find when input crosses VDD/2 (0.9V)
input_crossings = np.where(np.diff(np.sign(vin - 0.9)))[0]
output_crossings = np.where(np.diff(np.sign(vout - 0.9)))[0]

if len(input_crossings) > 0 and len(output_crossings) > 0:
    t_phl = time[output_crossings[0]] - time[input_crossings[0]]
    t_plh = time[output_crossings[1]] - time[input_crossings[1]]
    print(f"Propagation Delay (t_PHL): {t_phl:.2f} ps")
    print(f"Propagation Delay (t_PLH): {t_plh:.2f} ps")
else:
    print("Could not calculate propagation delays - not enough crossings detected")