from src.sym_breaker import getSymmetryBreakerConstraints
import src.init

"""
This script provides a function for altering the template models for MiniZinc-type models.
It is mainly used when switching between formalizations or when adding symmetry breakers.

- prepare_constraint()      >       Switches a constraint from one formalization to another
- prepare_model()           >       Applies all constraints to a template, making the final model.
"""

def prepare_constraint(constraint: str, formalization: int = 1):
    """
    Switches a constraint from one formalization to another.

    Args:
        constraint (str): The constraint to be modified.
        formalization (int, optional): The model formalization. Defaults to 1.
    """

    common_names = ["basicAllocation", "capacity", "conflict", "lowerBound", "upperBound", "equalBound", "exclusiveDeployment", "colocation",
        "fullDeployment", "requireProvide"
    ]
    
    if formalization == 1:
        #
        # By default, constraints are in the first formalization. No changes required.
        #
        return constraint
    
    constraint = constraint[11::]   # Remove the constraint keyword so we can get the actual type
    constraint = constraint.replace("    ", "")
    
    if constraint.startswith(tuple(common_names)):
        start = constraint.find("{")
        end = constraint.find("}")
        arg_list = constraint.split(",")

        if constraint.startswith("basicAllocation"):   
            return "constraint basicAllocation(AssignmentMatrix, VM, VMOffers, NoComponents, " + constraint[start:end+1:] + ");\n"
        
        elif constraint.startswith("capacity"):
            return "constraint capacity(AssignmentMatrix, CompREQ, VMSpecs, VMType, HardwareREQ, NoComponents, VM, VMOffers);\n"
        
        elif constraint.startswith("conflict"):
            comp = arg_list[-1][1:-3:]
        
            return "constraint conflict(AssignmentMatrix, VM, VMOffers, " + comp + ", " + constraint[start:end+1:] + ");\n"
        elif constraint.startswith("lowerBound"):                   
            start = arg_list.index(" VM")
            bound = arg_list[-1][1:-3]
            temp = "constraint lowerBound(AssignmentMatrix, VM, VMOffers, {"
            
            for i in arg_list[start+1 : -1]:
                temp += i[1:]
                
                if arg_list.index(i) != len(arg_list) - 2:
                    temp += ", "
            
            return temp + "}, " + bound +");\n"
        elif constraint.startswith("equalBound"):
            start = arg_list.index(" VM")
            bound = arg_list[-1][1:-3]
            temp = "constraint equalBound(AssignmentMatrix, VM, VMOffers, {"
            
            for i in arg_list[start+1 : -1]:
                temp += i[1:]
                
                if arg_list.index(i) != len(arg_list) - 2:
                    temp += ", "
            
            return temp + "}, " + bound +");\n"
        elif constraint.startswith("upperBound"):
            start = arg_list.index(" VM")
            bound = arg_list[-1][1:-3]
            temp = "constraint upperBound(AssignmentMatrix, VM, VMOffers, {"
            
            for i in arg_list[start+1 : -1]:
                temp += i[1:]
                
                if arg_list.index(i) != len(arg_list) - 2:
                    temp += ", "
            
            return temp + "}, " + bound +");\n"
        elif constraint.startswith("colocation"):
            return "constraint colocation(AssignmentMatrix, VM, VMOffers, " + constraint[start:end+1:] + ");\n"
        elif constraint.startswith("requireProvide"):
            start = constraint.find("VM, ") + 4
            end = constraint.find(")")
            
            return "constraint requireProvide(AssignmentMatrix, VM, VMOffers, " + constraint[start:end:] + ");"
        elif constraint.startswith("fullDeployment"):
            comp = arg_list[-1][1:-3:]
            
            return "constraint fullDeployment(AssignmentMatrix, VM, VMOffers, NoComponents, " + comp + ", " + constraint[start:end+1:] + ");\n"
        elif constraint.startswith("exclusiveDeployment"):
            start = arg_list.index(" VM")
            temp = "constraint exclusiveDeployment(AssignmentMatrix, VM, VMOffers, {"
            
            for i in arg_list[start+1:]:
                temp += i[1:]
                
                if arg_list.index(i) != len(arg_list) - 1:
                    temp += ", "
            
            
            temp = temp.replace(");\n", "")
            return temp + "});\n"
        
        else:
            return ""
    elif constraint.startswith("if"):
        return "constraint if(isDeployed(AssignmentMatrix, VM, VMOffers, DNS_LoadBalancer) == 1)\n"
    
    else:
        return ""

def prepare_model(use_case: dict, formalization: int = 1, symmetry_breaker: str = None, scalable_components: list = []):
    """
    This function takes a model template and makes the necessary adjustments,
    so that it can be run for the required test.

    The adjustments made by the script include:
        - Adding / removing static symmetry breakers
        - Adding / removing component instances
        - Adjusting included modules based on formalization

    Args:
        use_case (dict): The use case details
        formalization (int, optional): The desired formalization. Defaults to 1.
        symmetry_breaker (str, optional): The desired symmetry breaker(s). Defaults to None.
        scalable_components (list, optional): A list of scalable components and their instances. Defaults to [].
    """
    with open(f"{src.init.settings['MiniZinc']['model_path']}/{use_case['model']}_template.{src.init.settings['MiniZinc']['model_ext']}", "r") as template:
        ifEncountered = 0
        headerPut = 0
        
        with open(f"{src.init.settings['MiniZinc']['model_path']}/{use_case['model']}.{src.init.settings['MiniZinc']['model_ext']}", "w") as script:
            for line in template.readlines():
                if line.find("if") > -1:
                    ifEncountered = 1
                elif line.startswith("endif"):
                    ifEncountered = 0
                
                if line.startswith("include"):
                    if symmetry_breaker != None and headerPut == 0:
                        script.write(f'include "Modules/Formalization{formalization}/SymmetryBreaking.mzn";\n')
                        headerPut = 1
                    
                    script.write(f'include "Modules/Formalization{formalization}/')
                    script.write(line[17::])
                    
                elif line.startswith("constraint"):   
                    string = prepare_constraint(line, formalization)
                    
                    script.write(string)

                elif line.startswith("solve"):
                    if formalization == 2:
                        script.write("constraint linkedTypes(AssignmentMatrix, VMType, VM, VMOffers, NoComponents);\n")
                        script.write("constraint linkedPrice(VMType, VMPrice, Price, VM, VMOffers);\n")
                        script.write("constraint uniqueType(VMType, VM, VMOffers);\n")
                        script.write("constraint uniqueAlloc(AssignmentMatrix, VM, NoComponents, VMOffers);\n")
                        
                    
                    if symmetry_breaker != None:
                        constraints = getSymmetryBreakerConstraints(symmetry_breaker, use_case['model'], scalable_components)

                        for constraint in constraints:
                            if constraint != None:
                                script.write(constraint)
                    script.write(line)

                else:
                    if ifEncountered and line.find("require") != -1:                        
                        string = prepare_constraint("constraint " + line.replace("\n", ";\n"), formalization)
                        string = string.replace("constraint ", "")
                        string = string.replace(";", "\n")
                        
                        script.write(string)
                    else:
                        for item in scalable_components:
                            if item['name'] == line[5:-2]:
                                script.write(f"int: {item['name']} = {item['inst']};\n")
                                break
                        else:
                            script.write(line)