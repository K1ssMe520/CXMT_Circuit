## Circuit Connect

I'm designing a [Model] circuit. We already have some submodules. Please help me complete the connection of this circuit and determine the submodule parameters. Below is a template for the problem input and response.

### Model Description

Model: TwoStageDifferentialOpamp

Description: A two-stage differential opamp (first stage: common-source with an active load and a tail current, second stage: common-source with an active load)

Input Nodes: Vinp (positive differential input signal), Vinn (negative differential input signal), Vbias1 (first stage bias voltage), Vbias2 (second stage bias voltage), Vbias3 (tail current bias voltage)

Output Nodes: Voutp (positive differential output signal), Vout (negative differential output signal)

### SubModels

#### SubModel 01

Model: DiffInputStage

Description: Differential pair with active load and tail current source (first stage). Converts the differential input into a single-ended signal and drives the following stage.

Input Nodes: Vinp (non-inverting input), Vinn (inverting input), Vbias1 (tail current source bias), Vbias2 (active-load current-mirror bias)

Output Nodes: Vout_int (output of the first stage, fed to the second stage)

Structure Description: The differential input stage consists of a differential pair (M1, M2) with an active load (M4, M5) and a tail current source (M3). The differential input signals (Vinp, Vinn) are converted to a single-ended output (Vout_int) through the current mirror load. The tail current source provides biasing for the differential pair, while Vbias1 controls the current mirror. The output is taken from one side of the differential pair (Node2) through an additional PMOS transistor (M6) to provide proper level shifting and drive capability for the next stage.

Parameters:

- cs_nmos_width: Channel width of the NMOS driver transistor in the common-source stage. Increasing this value boosts transconductance (gm) and gain, while raising input capacitance and power consumption. Reducing it saves power and area but degrades gain and bandwidth
- cs_pmos_width: Channel width of the PMOS active load transistor. Larger values decrease load resistance, improving output swing at the cost of higher output node capacitance. Smaller values increase gain (through higher load resistance) but limit current drive capability
- channel_length: MOSFET channel length for all transistors. Shorter lengths improve transconductance and frequency response while exacerbating short-channel effects. Longer lengths reduce leakage current and improve matching, but degrade gain and speed

#### SubModel 02

Model: CSGainStage

Description: Common-source amplifier with active load (second stage). Provides high voltage gain and drives the output node.

Input Nodes: Vin_int (input of the second stage, connected to the first-stage output), Vbias3 (active-load current-source bias)

Output Nodes: Vout (final output)

Structure Description: The common-source gain stage consists of an NMOS transistor (M1) configured as a common-source amplifier with a PMOS transistor (M2) serving as an active load. The input signal (Vin_int) drives the gate of M1, while Vbias2 controls the current through the PMOS active load. The output (Vout) is taken from the drain of both transistors. This configuration provides high voltage gain and drives the output node for subsequent stages.

Parameters:

- diff_nmos_width: Channel width of the differential pair input transistors. Increasing enhances input transconductance, CMRR and gain, while increasing input capacitance. Reducing saves power and reduces input capacitance but lowers gain and slew rate
- diff_pmos_width: Channel width of the active load current mirror transistors. Wider devices lower mirror impedance, improving output swing but adding parasitic capacitance. Narrower devices increase gain (through higher output impedance) but limit maximum output current
- channel_length: MOSFET channel length for all devices. Shorter lengths improve transconductance and gain-bandwidth product (GBW). Longer lengths reduce channel-length modulation effects, improving output impedance and DC gain

#### Parameters

```python
DiffInputStage_Param = {
    'diff_nmos_width': 10e-6,
    'diff_pmos_width': 20e-6,
    'channel_length': 0.18e-6
}

CSGainStage_Param = {
    'cs_nmos_width': 20e-6,
    'cs_pmos_width': 20e-6,
    'channel_length': 0.18e-6
}
```

#### Netlist

```python
import sys
from pathlib import Path
root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

# 2. External imports
from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory
from netlist.DiffInputStage import DiffInputStage
from netlist.CSGainStage import CSGainStage

# 3. Main class definition
class TwoStageOpamp(SubCircuitFactory):
    NAME  = 'TwoStageOpamp'
    NODES = ('Vinp', 'Vinn',   # differential inputs
             'Vbias1', 'Vbias2', 'Vbias3',  # bias voltages
             'Vout',            # single-ended output
             'VDD', 'GND')      # power rails

    def __init__(self):
        super().__init__()
        #Parameters
        DiffInputStage_Param = {
            'diff_nmos_width': 10e-6,
            'diff_pmos_width': 20e-6,
            'channel_length': 0.18e-6
        }

        CSGainStage_Param = {
            'cs_nmos_width': 20e-6,
            'cs_pmos_width': 20e-6,
            'channel_length': 0.18e-6
        }

        self.model('nmos_model', 'nmos', level=1, kp=200e-6, vto=0.5)
        self.model('pmos_model', 'pmos', level=1, kp=100e-6, vto=-0.5)

        # 3.2 Sub-circuits
        self.subcircuit(DiffInputStage(
            diff_nmos_width=DiffInputStage_Param['diff_nmos_width'],
            diff_pmos_width=DiffInputStage_Param['diff_pmos_width'],
            channel_length=DiffInputStage_Param['channel_length']))

        self.subcircuit(CSGainStage(
            cs_nmos_width=CSGainStage_Param['cs_nmos_width'],
            cs_pmos_width=CSGainStage_Param['cs_pmos_width'],
            channel_length=CSGainStage_Param['channel_length']))

        # 3.3 Circuit instantiation
        self.X('diff_stage', 'DiffInputStage',
               'Vinp', 'Vinn', 'Vbias1', 'Vbias2', 'Vout_int',
               'VDD', 'GND')

        # 3.3.2 Common-source gain stage
        self.X('cs_stage', 'CSGainStage',
               'Vout_int', 'Vbias3', 'Vout',
               'VDD', 'GND')

        # 3.4 Biasing devices
        self.M('Mbias', 'Vbias3', 'Vbias3', 'VDD', 'VDD',
               model='pmos_model',
               l=channel_length,
               w=cs_pmos_width * 0.5)      # Half the width of the load device

        # Tail-current source for the differential pair
        self.M('Mtail_bias', 'Vbias2', 'Vbias2', 'GND', 'GND',
               model='nmos_model',
               l=channel_length,
               w=diff_nmos_width * 2)      # Twice the width of the input devices

```

#### Structure Description

```markdown
The Two-Stage Differential Opamp (CDR circuit) comprises three primary submodules interconnected as follows: A differential input stage (DiffInputStage) receives signals at Vinp/Vinn and utilizes Vbias3 for tail current biasing and Vbias1 for active load biasing, producing an intermediate output (Vout_int). This single-ended output drives two identical common-source gain stages (CSGainStage1 and CSGainStage2), both biased by Vbias2 to generate differential outputs (Voutp and Vout). A differential load capacitor (C_load) connects between these outputs to stabilize frequency response. Simplified diode-connected bias transistors (Mbias1, Mbias2, Mtail_bias) generate critical bias voltages: PMOS devices Mbias1/Mbias2 bias the input stage loads and gain stages respectively, while NMOS Mtail_bias sets the input stage tail current.
```

#### Tips

Additional notes not included in the response:

1. The user's input only contains Model Description, SubModules sections. Please answer Parameters, Netlist, and Structure Description sections accordingly.
2. Please write the parameters of submodels separately in the Parameters section, and make sure that the values here are the same as the Netlist section
3. You can only call the existing submodules of SubModules. Please do not generate new modules.
4. Please also write Parameters into Netlist.

Here is the specific input:

### Model Description

Model: [Model]

Description: [Description]

Input Nodes: [InputNode]

Ouput Nodes: [OutputNode]
