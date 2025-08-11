from dataclasses import dataclass, asdict
import os
import json
import subprocess

@dataclass
class CIRCUIT_MODEL:
    model_name: str = None
    model_description: str = None

    inputnode: str = None
    outputnode: str = None

    parameter: str = None
    parameter_description: str = None
    
    netlist: str = None
    structure_description: str = None

    testcode: list[str] = None
    testDescription: list[str] = None
    testresult: list[str] = None

    submodel_names: list[str] = None

    function_code: str = None

    def __post_init__(self):
        self.json_path = './model_json'
        self.netlist_path = './netlist'
        self.test_path = './testbench'
        self.funciton_path ='./function'

    def get_replacement(self):
        replacement = {
            'Model': self.model_name,
            'Description': self.model_description,
            'InputNode': self.inputnode,
            'OutputNode': self.outputnode,
            'Parameter': self.parameter,
            'Parameter_Des': self.parameter_description,
            'Structure_Des': self.structure_description
        }
        return replacement

    def save_all_componet(self):
        self.save_json()
        self.save_netlist()
        self.save_function_code()
        if self.testcode != None:
            for test_id in range(len(self.testcode)):
                self.save_testcode(test_id)
            

    def save_json(self):
        json_file_path = os.path.join(self.json_path, f"{self.model_name}.json")
        try:
            model_dict = asdict(self)
            with open(json_file_path, 'w') as file:
                json.dump(model_dict, file, indent=4)
            # print(f"Model saved successfully to {json_file_path}")
        except Exception as e:
            print(f"Failed to save model: {e}")


    def save_netlist(self):
        if self.netlist == None: return

        netlist_file_path = os.path.join( self.netlist_path, f"{self.model_name}.py" )
        try:
            with open(netlist_file_path, 'w') as file:
                file.write(self.netlist)
        except:
            print("Fail to write netlist to file")

    def save_function_code(self):
        if self.function_code == None: return
        function_file_path = os.path.join( self.funciton_path, f"show_{self.model_name}.py" )
        try:
            with open(function_file_path, 'w') as file:
                file.write(self.netlist)
        except:
            print("Fail to write netlist to file")


    def save_testcode(self, test_id: int):
        assert test_id < len(self.testcode), 'Exceed Testcode Count'
        test_file_path = os.path.join( self.test_path, f"{self.model_name}/Test_{test_id}.py" )
        os.makedirs(os.path.dirname(test_file_path), exist_ok=True)
        try:
            with open(test_file_path, 'w') as file:
                file.write(self.testcode[test_id])
        except:
            print("Fail to write testcode to file")

    def execute_testcode(self, test_id: int):
        self.save_netlist()
        self.save_testcode(test_id)

        testcode_file_path = os.path.join( self.test_path, f"{self.model_name}/Test_{test_id}.py" )
        result = subprocess.run(
            ['python', testcode_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        combined_output = result.stdout + result.stderr
        print(combined_output)
        if self.testresult == None: self.testresult = [ None for i in range(len(self.testcode)) ]
        self.testresult[test_id] = combined_output.replace("Warning: can't find the initialization file spinit. Unsupported Ngspice version 44", "")

    def execute_function_code(self):
        if self.function_code != None:
            self.save_function_code()
        function_file_path = os.path.join( self.funciton_path, f"show_{self.model_name}.py" )
        result = subprocess.run(
            ['python', function_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        combined_output = result.stdout + result.stderr
        print(combined_output)    


    @staticmethod
    def load_model_json(json_path: str):
        try:
            with open(json_path, 'r') as file:
                model_dict = json.load(file)
                model = CIRCUIT_MODEL()
                model.__dict__.update(model_dict)
            # print(f"Model loaded successfully from {model_path}")
            return model
        except Exception as e:
            print(f"Failed to load model: {e}")
            return None


class MODEL_SET:
    def __init__(self, json_path: str):
        self.all_models: dict[str: CIRCUIT_MODEL] = {}
        self.load_all_models(json_path)

    def save_single_model(self, model_name: str):
        self.all_models[model_name].save_all_componet()
        if self.all_models[model_name].submodel_names != None:
            for submodel in self.all_models[model_name].submodel_names:
                self.all_models[submodel].save_all_componet()

    def save_all_models(self):
        for key in self.all_models:
            self.all_models[key].save_all_componet()

    def load_all_models(self, json_path: str):
        try:
            for filename in os.listdir(json_path):
                if filename.endswith('.json'):
                    filepath = os.path.join(json_path, filename)
                    model = CIRCUIT_MODEL.load_model_json(filepath)
                    if model:
                        model_key = os.path.splitext(filename)[0]
                        self.all_models[model_key] = model
            #print(f"Loaded {len(self.all_models)} models from {model_path}")
        except Exception as e:
            print(f"Error loading models from directory: {e}")