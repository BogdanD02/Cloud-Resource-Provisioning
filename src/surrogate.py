from csv import DictWriter
from minizinc import Instance, Model, Solver
import src.init

"""  
The following script runs all the surrogate problems and builds a single csv
containing the estimated number of virtual machines (VMs) for each test case.

The format of the csv file is the following:

```
Use-case Name, Instances, Estimated VMs
```

The generated csv will be placed at the location set inside the configuration file.
"""

def solve_surrogate(model: str, solver:dict, scaling_components: list = []):
    """
    This function will solve a specific surrogate instance, returning a dictionary containing
    the estimated number of virtual machines required as well as the estimated number of instances
    for each component.

    Args:
        model (str): The name of the surrogate model to solve
        solver (dict): The solver specifications
        scaling_components (list, optional): A list of components whose instances must be replaced with actual values.
    
    Returns:
        result (any): The result obtained from the surrogate.
    """
    result = None

    if solver["type"] == "MiniZinc":
        instance = prepare_minizinc_instance(model, solver["id"], scaling_components)
        result = instance.solve()

    #
    # TO DO : Add support for JSON Surrogate after refactor
    #

    return result
    

def prepare_surrogate_instance(model: str, scaling_components: list = []):
    """
    Prepares a Minizinc instance based off the model path and (optionally) the number of instances
    for a specific component.

    Args:
        model (str): The name of the model
        solver (str): The keyword of the solver
        scaling_components (list, optional): A list containing components and their number of instances. Defaults to [].
    """    
    Minizinc_instance = Instance(Solver.lookup("chuffed"), Model(f"{src.init.settings['MiniZinc']['surrogate_path']}/{model}.{src.init.settings['MiniZinc']['surrogate_ext']}"))

    for item in scaling_components:
        Minizinc_instance[item["name"]] = item["inst"]
    
    return Minizinc_instance

def prepare_minizinc_instance(model: str, solver: str, scaling_components: list = []):
    """
    Prepares a Minizinc instance based off the model path and (optionally) the number of instances
    for a specific component.

    Args:
        model (str): The name of the model
        solver (str): The keyword of the solver
        scaling_components (list, optional): A list containing components and their number of instances. Defaults to [].
    """    
    Minizinc_instance = Instance(Solver.lookup(solver), Model(f"{src.init.settings['MiniZinc']['surrogate_path']}/{model}.{src.init.settings['MiniZinc']['surrogate_ext']}"))

    for item in scaling_components:
        Minizinc_instance[item["name"]] = item["inst"]
    
    return Minizinc_instance

def build_output(content: list):
    """
    Constructs the CSV file containing the results.

    This function is now obsolete !

    Args:
        content (list): The contents of the csv file
    """
    with open(f"{src.init.settings['MiniZinc']['surrogate_output_path']}/Surrogate.{src.init.settings['MiniZinc']['surrogate_output_ext']}", "w") as outputFile:
        writer = DictWriter(outputFile, ["Name", "Instances", "Estimated VMs"])
        
        writer.writeheader()
        writer.writerows(content)
        
    if f"{src.init.settings['MiniZinc']['surrogate_output_path']}/Surrogate.{src.init.settings['MiniZinc']['surrogate_output_ext']}" != \
       f"{src.init.settings['JSON']['surrogate_output_path']}/Surrogate.{src.init.settings['JSON']['surrogate_output_ext']}":

        with open(f"{src.init.settings['JSON']['surrogate_output_path']}/Surrogate.{src.init.settings['JSON']['surrogate_output_ext']}", "w") as outputFile:
            writer = DictWriter(outputFile, ["Name", "Instances", "Estimated VMs"])
            
            writer.writeheader()
            writer.writerows(content)

def build_components(scaling_components: list, id: int = 0):
    """
    Given a list of components and their instances, this function generates all possible combinations
    between them.

    This function is now obsolete !

    Args:
        scaling_components (list, optional): A list of dictionaries for each scaling component. Defaults to []
        id (int, optional): The start of the recursion. Defaults to 0
    Returns:
        combinations (list): A list of all possible combinations
    """
    combinations = []

    if id >= len(scaling_components):
        return combinations

    rest = build_components(scaling_components, id+1)

    for inst in range(scaling_components[id]["Lower-Bound"], scaling_components[id]["Upper-Bound"] + 1):        
        if rest != []:
            for item in rest:
                item.append({"name": scaling_components[id]["Name"], "inst": inst})
            combinations = rest
        else:
            combinations.append([{"name": scaling_components[id]["Name"], "inst": inst}])
    return combinations

def build_surrogate():
    """
    Goes through each use case, and if it has a surrogate problem it runs it using
    Minizinc and appends the results to the final output. Finally it calls the construction
    of the CSV file containing all output.

    Warning: As the problem is now split into 2 different sections, this function is
    obsolete as we require an estimation for all components, not just the VM.
    """
    
    content = []
    
    for use_case in src.init.settings["Use-Cases"]:
        if "surrogate" in use_case.keys():
            if use_case["components"] != []:  
                scaling_components = build_components(use_case["components"])

                for item in scaling_components:
                    content.append({})
                    content[-1]["Name"] = use_case["name"]
                    
                    runable = prepare_surrogate_instance(use_case["surrogate"], item)
                    res = runable.solve()
                    
                    content[-1]["Instances"] = sum([x["inst"] for x in item])
                    content[-1]["Estimated VMs"] = res["objective"]
            else:
                content.append({})
                content[-1]["Name"] = use_case["name"]
                
                runable = prepare_surrogate_instance(use_case["surrogate"])
                res = runable.solve()
                
                content[-1]["Instances"] = 0
                content[-1]["Estimated VMs"] = res["objective"]
                
    build_output(content)