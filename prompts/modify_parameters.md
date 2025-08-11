## Modify Parameters Prompt

For a complex [Model] circuit, there are already netlists for its top-module and sub-module and the parameters of each sub-module. We conducted a test on it. Please judge whether the test passes according to the test results. If not, please redesign the submodule parameters. Below is a template for the problem input and response.

### TopModule

Model: TwoStageDifferentialOpamp

Description: A two-stage differential opamp (first stage: common-source with an active load and a tail current, second stage: common-source with an active load)

Input Nodes: Vinp (positive differential input signal), Vinn (negative differential input signal), Vbias1 (first stage bias voltage), Vbias2 (second stage bias voltage), Vbias3 (tail current bias voltage)

Output Nodes: Voutp (positive differential output signal), Vout (negative differential output signal)

Structure Description: The Two-Stage Differential Opamp (CDR circuit) comprises three primary submodules interconnected as follows: A differential input stage (DiffInputStage) receives signals at Vinp/Vinn and utilizes Vbias3 for tail current biasing and Vbias1 for active load biasing, producing an intermediate output (Vout_int). This single-ended output drives two identical common-source gain stages (CSGainStage1 and CSGainStage2), both biased by Vbias2 to generate differential outputs (Voutp and Vout). A differential load capacitor (C_load) connects between these outputs to stabilize frequency response. Simplified diode-connected bias transistors (Mbias1, Mbias2, Mtail_bias) generate critical bias voltages: PMOS devices Mbias1/Mbias2 bias the input stage loads and gain stages respectively, while NMOS Mtail_bias sets the input stage tail current.


#### SubModules

#### SubModule 01

Model: DiffInputStage

Description: Differential pair with active load and tail current source (first stage). Converts the differential input into a single-ended signal and drives the following stage.

Input Nodes: Vinp (non-inverting input), Vinn (inverting input), Vbias3 (tail current source bias), Vbias1 (active-load current-mirror bias)

Output Nodes: Vout_int (output of the first stage, fed to the second stage)

Structure Description: The differential input stage consists of a differential pair (M1, M2) with an active load (M4, M5) and a tail current source (M3). The differential input signals (Vinp, Vinn) are converted to a single-ended output (Vout_int) through the current mirror load. The tail current source provides biasing for the differential pair, while Vbias1 controls the current mirror. The output is taken from one side of the differential pair (Node2) through an additional PMOS transistor (M6) to provide proper level shifting and drive capability for the next stage.

Parameter Description: 
- nmos_width: Channel width of the NMOS transistors (M1, M2, M3). Increasing this value enhances the transconductance and current drive capability of the differential pair but also increases parasitic capacitance and area.
- pmos_width: Channel width of the PMOS transistors (M4, M5, M6). Larger values improve current mirror matching and output drive strength but increase power consumption and area.
- channel_length: MOSFET channel length for all transistors. Shorter lengths improve speed but may worsen mismatch and short-channel effects; longer lengths reduce leakage current.
- tail_current: The bias current set by M3. Higher values increase the transconductance and speed of the differential pair but also raise power consumption.

#### SubModule 02

Model: CSGainStage

Description: Common-source amplifier with active load (second stage). Provides high voltage gain and drives the output node.

Input Nodes: Vin_int (input of the second stage, connected to the first-stage output), Vbias2 (active-load current-source bias)

Output Nodes: Vout (final output)

Structure Description: The common-source gain stage consists of an NMOS transistor (M1) configured as a common-source amplifier with a PMOS transistor (M2) serving as an active load. The input signal (Vin_int) drives the gate of M1, while Vbias2 controls the current through the PMOS active load. The output (Vout) is taken from the drain of both transistors. This configuration provides high voltage gain and drives the output node for subsequent stages.

Parameter Description: 
- nmos_width: Channel width of the NMOS transistor (M1). Increasing this value boosts the transconductance and gain but also increases parasitic capacitances.
- pmos_width: Channel width of the PMOS active load (M2). Larger widths provide higher output resistance (better current source) but increase area and capacitance.
- channel_length: MOSFET channel length for both transistors. Longer lengths improve output resistance but reduce speed; shorter lengths increase speed but may degrade output resistance.
- load_capacitance: Capacitive load at the output node (Vout). Larger values slow the transient response but may be necessary for stability or as part of frequency compensation.

### Parameters

```python
DiffInputStage_Param = {
    'nmos_width': 10e-6,
    'pmos_width': 20e-6,
    'channel_length': 0.18e-6,
    'tail_current': 100e-6
}
CSGainStage_Param = {
    'nmos_width': 20e-6,
    'pmos_width': 20e-6,
    'channel_length': 0.18e-6,
    'load_capacitance': 1e-12
}
```

### Test

#### Test Description

DC Operating Point Test: Verify the DC operating points of all stages are properly biased. Check that the output common-mode voltage is within expected range when inputs are at common-mode voltage. This ensures proper biasing of all transistors in the circuit.

#### Test Result

FAIL: Output common mode voltage 0.044V is not within 2.3V range

Test_Failed: One or more DC operating points are out of range

### Response

#### Pass or Fail

```markdown
Fail
```

#### Modification

```python
DiffInputStage_Param = {
    'nmos_width': 10e-6,
    'pmos_width': 20e-6,
    'channel_length': 0.18e-6,
    'tail_current': 100e-6
}
CSGainStage_Param = {
    'nmos_width': 20e-6,
    'pmos_width': 20e-6,
    'channel_length': 0.18e-6,
    'load_capacitance': 1e-12
}
```

### Tips
Additional notes not included in the response:
1. The user's input only contains TopModule, SubModules, Parameters, and Test sections. Please answer 'Pass or Fail' and Modification sections
2. In 'Pass or Fail' section, please only use the word Pass or Fail to express whether the test has passed
3. If test Passes, then there is no need to generate Modification section

Here is the specific input:

### TopModule

Model: [Model]

Description: [Description]

Input Nodes: [InputNode]

Ouput Nodes: [OutputNode]

Structure Description: [Structure_Des]


