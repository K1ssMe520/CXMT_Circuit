import re
import sys
from pathlib import Path
root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

from basic.LLM_interface import KIMI, DeepSeek_R1
from basic.circuit_model import *

prompt_paths = {
    'Generate_Circuit' : './prompts/circuit_generate.md',
    'Check_Promblems' : './prompts/check_problems.md',
    'Requirement_Parsing' : './prompts/requirement_parsing.md',
    'Circuit_Connect' : './prompts/circuit_connect.md',
    'Modify_Parameters' : './prompts/modify_parameters.md',
    'Function_Illustrate' : './prompts/function_illustrate.md'
}

LLM_model = DeepSeek_R1

circuit_set = MODEL_SET('./model_json')

topmodel = circuit_set.all_models['SimpleSARADC']

def generate_prompt(file_path: str, replacement: dict) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        for key, value in replacement.items():
            if value != None:
                placeholder = f"[{key}]"
                content = content.replace(placeholder, value)
        return content
    except Exception as e:
        print(f"Error: {e}") 
        raise
   

def add_submodule(prompt: str, submodel_names: list[str]):
    prompt += f"\n\n### SubModels"
    index = 0 
    for submodel_name in submodel_names:
        submodel = circuit_set.all_models[submodel_name]
        prompt += f"\n\n#### SubModel {index+1}\n"
        prompt += f"Model: {submodel.model_name}\n\n"
        prompt += f"Description: {submodel.model_description}\n\n"
        prompt += f"Input Nodes: {submodel.inputnode}\n\n"
        prompt += f"Output Nodes: {submodel.outputnode}\n\n"
        prompt += f"Structure Description: {submodel.structure_description}\n\n"
        prompt += f"Parameters:\n{submodel.parameter_description}\n\n"
        index += 1
    return prompt


def extract_code(text: str, segment_leader: str, code_leader: str):
    pattern = re.compile(
        r'###\s+' + re.escape(segment_leader) + r'\s*' + 
        r'```' + re.escape(code_leader) + r'\n(.*?)```',
        re.DOTALL
    )
    match = pattern.search(text)
    if match:
        return match.group(1).strip()
    return None

def extract_test_items(text: str):
    pattern = r'####\s+(Test_Item\s+\d+)(.*?)(?=#### Test_Item|\Z)'
    matches = re.finditer(pattern, text, re.DOTALL)
    
    test_items = []
    test_descriptions = []    
    for match in matches:
        item_name = match.group(1).strip()
        item_content = match.group(2).strip()

        markdown_match = re.search(r'```markdown\n(.*?)```', item_content, re.DOTALL)
        markdown = markdown_match.group(1).strip() if markdown_match else None

        python_match = re.search(r'```python\n(.*?)```', item_content, re.DOTALL)
        python_code = python_match.group(1).strip() if python_match else None
        
        test_items.append(python_code)
        test_descriptions.append(markdown)
    
    return test_items, test_descriptions

def extract_submodels(message: str) -> list[CIRCUIT_MODEL]:
    pattern = re.compile(
        r'###\s+Module\s+\d+\s*\n'
        r'Model:\s*(.*?)\s*\n'
        r'Description:\s*(.*?)\s*\n'
        r'Input\s+Nodes:\s*(.*?)\s*\n'
        r'Output\s+Nodes:\s*(.*?)\s*(?=\n##|$)',
        re.DOTALL | re.IGNORECASE
    )
    submodels = []
    for m in pattern.finditer(message):
        model       = m.group(1).strip()
        description = m.group(2).strip()
        inputnode   = m.group(3).strip()
        outputnode  = m.group(4).strip()
        submodels.append(
            CIRCUIT_MODEL(
                model_name=model,
                model_description=description,
                inputnode=inputnode,
                outputnode=outputnode
            )
        )
    return submodels


def create_requirement_parsing(topmodel: CIRCUIT_MODEL):
    prompt = generate_prompt(prompt_paths['Requirement_Parsing'], topmodel.get_replacement())
    print(f"\n\n{prompt}")

    response = LLM_model.get_answer(prompt)
    print(f"## Get response from {LLM_model.name}\n\n{response}")

    submodel = extract_submodels(response)

    submodel_names = [ model.model_name for model in submodel ]
    topmodel.submodel_names = submodel_names
    
    for model in submodel:
        circuit_set.all_models[model.model_name] = model


def create_sub_circuit(model: CIRCUIT_MODEL):
    prompt = generate_prompt(prompt_paths['Generate_Circuit'], model.get_replacement())
    print(f"\n\n{prompt}")

    response = LLM_model.get_answer(prompt)
    print(f"## Get Response from {LLM_model.name}\n\n{response}")

    model.netlist = extract_code(response, "NetList Code", 'python')
    model.structure_description = extract_code(response, "Structure Description", 'markdown')
    model.parameter_description = extract_code(response, "Parameter Explanation", 'markdown')


def create_check_problems(model: CIRCUIT_MODEL):
    prompt = generate_prompt(prompt_paths['Check_Promblems'], model.get_replacement())
    print(f"\n\n{prompt}")
    if model.submodel_names != None:
        prompt += '\n\n Parameter Description:\n'
        prompt += f'{model.parameter_description}\n\n'

    response = LLM_model.get_answer(prompt)
    print(f"## Get response from {LLM_model.name} \n\n{response}")
    model.testcode, model.testDescription = extract_test_items(response)


def create_connect_submodules(topmodule: CIRCUIT_MODEL):
    prompt = generate_prompt(prompt_paths['Circuit_Connect'], topmodule.get_replacement())
    prompt = add_submodule(prompt, topmodule.submodel_names)
    print(f"\n\n{prompt}")

    response = LLM_model.get_answer(prompt)
    print(f"## Get response from {LLM_model.name} \n\n{response}")

    topmodule.parameter = extract_code(response, "Parameters", 'python')
    topmodule.netlist = extract_code(response, "Netlist", 'python')
    topmodule.structure_description = extract_code(response, "Structure Description", 'markdown')


def create_modify_parameters(topmodule: CIRCUIT_MODEL, test_id: int) -> bool:
    prompt = generate_prompt(prompt_paths['Modify_Parameters'], topmodule.get_replacement())
    prompt = add_submodule(prompt, topmodule.submodel_names)
    prompt += "\n\n### Parameters\n\n```python" + topmodule.parameter + "\n```"
    prompt += "\n\n### Test\n\n#### Test Description\n\n" + topmodule.testDescription[test_id]
    prompt += "\n\n#### Test Result\n\n" + topmodule.testresult[test_id]
    print(f"\n\n{prompt}")

    response = LLM_model.get_answer(prompt)
    print(f"## Get response from {LLM_model.name} \n\n{response}")

    test_result = extract_code(response, "Pass or Fail", "markdown")

    if test_result == 'Pass':
        return True
    elif test_result == 'Fail':
        topmodule.parameter = extract_code(response, "Modification", 'python')

def create_funciton_illustrate(model: CIRCUIT_MODEL):
    prompt = generate_prompt(prompt_paths['Function_Illustrate'], model.get_replacement())
    print(f"\n\n{prompt}")

    response = LLM_model.get_answer(prompt)
    print(f"## Get response from {LLM_model.name} \n\n{response}")

    model.function_code = extract_code(response, "Function Illustration", "python")


if __name__ == '__main__':

    # TODO: create_modify_parameters. This part needs to be improved, so the following process is impossible.

    # topmodel = circuit_set.all_models['ClockDataRecovery']

    # create_requirement_parsing(topmodel)

    # for submodle in topmodel.submodel_names:
    #     create_sub_circuit(circuit_set.all_models[submodle])
    #     create_check_problems(circuit_set.all_models[submodle])

    # create_connect_submodules(topmodel)
    
    # create_check_problems(topmodel)

    # for test_id in range(topmodel.testcode):
    #     attempt_times = 3
    #     Pass_Test = False
    #     while attempt_times > 0:
    #         topmodel.execute_testcode(test_id)
    #         test_result=create_modify_parameters(topmodel, test_id)
    #         if test_result == True:
    #             Pass_Test = True
    #             break
    #         attempt_times -= 1
    #     if Pass_Test == False:
    #         print(f"Fail to pass test {test_id}")
    #         break
    #
    # circuit_set.save_all_models()

    # Some processes that can be run at present
    # TODO: Here is a template for generating top models
  
    # topmodel = circuit_set.all_models['SimpleSARADC']
    # create_requirement_parsing(topmodel)

    # for submodle in topmodel.submodel_names:
    #     create_sub_circuit(circuit_set.all_models[submodle])
    #     create_check_problems(circuit_set.all_models[submodle])

    # create_connect_submodules(topmodel)
    
    # create_check_problems(topmodel)

    # create_funciton_illustrate(topmodel)

    # circuit_set.save_all_models()

    # topmodel.execute_function_code()

    # Some processes that can be run at present
    # TODO: Here is a template for generating sub models
 
    model = circuit_set.all_models['Inverter']

    create_sub_circuit(model)

    create_check_problems(model)

    create_funciton_illustrate(model)

    circuit_set.save_all_models()

    model.execute_function_code()