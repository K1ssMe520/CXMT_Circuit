## SubModel Generate Prompt

Help me generate the PySpice code for the [Model] circuit. Below is a template for the problem input and response.

### Problem

Model: PhaseDetector

Description: Detects the phase difference between the input data signal and the VCO-generated clock. Outputs an error signal proportional to the phase misalignment.

Input Nodes: DataIn (input data signal), RecoveredClk (feedback clock from VCO), VDD (positive power supply), VSS (negative power supply/ground)

Output Nodes: PhaseError (error signal indicating phase difference)

### NetList Code

```python
from PySpice.Unit import *
from PySpice.Spice.Netlist import SubCircuitFactory

class PhaseDetector(SubCircuitFactory):
    NAME = 'PhaseDetector'
    NODES = ('DataIn', 'RecoveredClk', 'PhaseError', 'VDD', 'VSS')
  
    def __init__(self, nmos_width=0.5e-6, pmos_width=1e-6, channel_length=0.18e-6, filter_capacitance=10e-15):
        super().__init__()
        # Define MOSFET models (level 1)
        self.model('nmos_model', 'nmos', level=1, kp=100e-6, vto=0.5)
        self.model('pmos_model', 'pmos', level=1, kp=40e-6, vto=-0.5)
    
        # Phase detector core - D flip-flop implementation
        # Upper PMOS transistors
        self.MOSFET('M1', 'Q', 'RecoveredClk', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        self.MOSFET('M2', 'Qbar', 'RecoveredClk', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        
        # Lower NMOS transistors
        self.MOSFET('M3', 'Q', 'RecoveredClk', 'Node1', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        self.MOSFET('M4', 'Qbar', 'RecoveredClk', 'Node2', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        self.MOSFET('M5', 'Node1', 'Qbar', 'VSS', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        self.MOSFET('M6', 'Node2', 'Q', 'VSS', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        
        # Data input stage
        self.MOSFET('M7', 'Node1', 'DataIn', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        self.MOSFET('M8', 'Node2', 'DataIn', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        
        # Output stage (charge pump)
        self.MOSFET('M9', 'PhaseError', 'Q', 'VDD', 'VDD', model='pmos_model', w=pmos_width, l=channel_length)
        self.MOSFET('M10', 'PhaseError', 'Qbar', 'VSS', 'VSS', model='nmos_model', w=nmos_width, l=channel_length)
        
        # Optional filter capacitor
        if filter_capacitance > 0:
            self.C('C1', 'PhaseError', 'VSS', filter_capacitance)
```


### Structure Description

```markdown
The phase detector works by comparing the input data signal (DataIn) with the recovered clock (RecoveredClk) and generating an error signal (PhaseError) that indicates the phase difference. The circuit consists of a D flip-flop core with additional transistors for the charge pump output stage.
```

### Parameter Explanation

```markdown
- nmos_width: Channel width of the NMOS transistor, Raising this value increases the NMOS drive strength, but also enlarges the area and raises parasitic capacitances.
- pmos_width: Channel width of the PMOS transistor. Increasing it enhances the PMOS drive capability and improves the rising-edge speed, yet it expands the area and raises power consumption
- channel_length: MOSFET channel length. Shortening it boosts switching speed but aggravates short-channel effects; lengthening it reduces leakage current.
- load_capacitance: Capacitive load at the output node. Larger values slow the switching transients and increase propagation delay; setting it to 0 removes the load capacitor.
```


### Tips

Some tips that you should not include in the response:

1. As shown above, the user input only includes the problem section. Your response should include: NetList Code, Structure Description, Parameter Explanation.
2. The module class definition should be `class [Model](SubCircuitFactory):`
3. The MOSFETs should use level 1 for simulation and only include the kp and vto parameters. When using MOSFETs, only the width-to-length ratio needs to be defined.
4. For the MOSFET definition `self.MOSFET(name, drain, gate, source, bulk, model, w=w1,l=l1)`, be careful about the parameter sequence.
5. Connect the bulk of a MOSFET to its source.
6. Other basic components include capacitors, resistors, inductors, etc. Avoid calling submodules.
7. Avoid giving any AC voltage in the sources; only consider the operating points.
8.  Ensure that the interface of the subcircuit matches the requirements.

Here is the specific input:

### Problem

Model: [Model]

Description: [Description]

Input Nodes: [InputNode]

Ouput Nodes: [OutputNode]
