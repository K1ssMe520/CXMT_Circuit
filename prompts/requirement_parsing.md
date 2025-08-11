## Requirement Parsing

We need to design a complex [Model] circuit，please help me determine the sub-module required. Below is a template for the problem input and response.

### Model Description

Model: TwoStageDifferentialOpamp
Description: A two-stage differential opamp (first stage: common-source with an active load and a tail current, second stage: common-source with an active load)
Input Nodes: Vinp (positive differential input signal), Vinn (negative differential input signal), Vbias1 (first stage bias voltage), Vbias2 (second stage bias voltage), Vbias3 (tail current bias voltage)
Output Nodes: Voutp (positive differential output signal), Vout (negative differential output signal)

### Module 01

Model: DiffInputStage
Description: Differential pair with active load and tail current source (first stage). Converts the differential input into a single-ended signal and drives the following stage.
Input Nodes: Vinp (non-inverting input), Vinn (inverting input), Vbias1 (tail current source bias), Vbias2 (active-load current-mirror bias)
Output Nodes: Vout_int (output of the first stage, fed to the second stage)

### Module 02

Model: CSGainStage
Description: Common-source amplifier with active load (second stage). Provides high voltage gain and drives the output node.
Input Nodes: Vin_int (input of the second stage, connected to the first-stage output), Vbias3 (active-load current-source bias)
Output Nodes: Vout (final output)

### Tips

Additional notes not included in the response:

1. User input only contains the Model Description section, and you need to generate sub-modules sections accordingly.
2. There is no need to generate circuits for submodules.
3. You donnot need to use **** to emphsize anything in markdown.

Here is the specific input:

### Model Description

Model: [Model]

Description: [Description]

Input Nodes: [InputNode]

Ouput Nodes: [OutputNode]
