# STIC Circuit Project

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview
STIC Circuit is a Python-based toolkit for analog circuit modeling, simulation, and verification. The project provides:
- LLM agent for circuit design assistance
- Circuit definitions in JSON format
- Generated circuit netlist
- Generated test codes
- A full conversation trace


## Installation
```bash
git clone https://github.com/K1ssMe-a/STIC_Circuit.git
cd STIC_Circuit
```

## Directory Structure
```
├── basic/                  - Core circuit modeling components
│   ├── __init__.py
│   ├── circuit_model.py    - Base circuit model class
│   └── LLM_interface.py    - LLM integration module
├── basic/                  - Illustrate the function of circuite
│   ├──__init__.py
│   ├──show_Inverter.py
├── model_json/             - Circuit definitions (JSON format)
├── netlist/                - Python netlist generators
├── prompts/                - LLM prompt templates
├── testbench/              - Circuit test scripts
│   ├── ClockDataRecovery/
│   ├── OneStageAmplifier/
│   ├── ...
└── STIC_Circuit.py         - Main entry point
```

## Usage
1. STIC_Circuit.py is the main interface file. In the first few lines of the file, it defines which model API to use, the json path of the circuit module, and the top-level module name of the module to be created at present 
2. For the circuit you need to generate, please refer to any file in model_json to create a json file of your own circuit, which only needs to include model_name, model_description, inputnode, output In the node part, other contents will be automatically filled with the execution of the process 
3. After that, in the first few lines of the STIC_Circuit.py file, modify the top-level module name of the current module to be created, and execute STIC_Circuit.py to complete the circuit generation.

## Notifications

1. The project has not been fully completed, and the current problem is concentrated in the circuit test part 
   1. First of all, the current commercial model is not very good at writing PySpice's test code, resulting in the inability to run the generated test script 
   2. Guiding the LLM to write test code by supplementing Tips will make Prompt very bloated 
2. The follow-up improvement method is either to teach the LLM how to write test code through pre-training, or to add a large number of test samples to the prompt template 
3. In addition, you need to modify the create_modify_parameters function and write the new parameters in the response into the netlist of topmodel.
