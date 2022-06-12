from src.conflictGraph import getMaxClique
from json import load
import src.init

"""
This script is used when employing symmetry breaking techniques with MiniZinc Models.

The script generates the required constraints which are to be added for the respective
symmetry breaker.
"""

def addBreakerConstraint(symmetry_breaker: str = None, start: int = 0):
    """
    Constructs the constraint for symmetry breakers other than FV.

    Args:
        symmetry_breaker (str, optional): The tag of the symmetry breaker. Defaults to None.
        start (int, optional): The index of the first VM affected by the symmetry breaker. Defaults to 0.

    Returns:
        constraint (str): The constraint to be added to the model.
    """

    with open(f"{src.init.settings['MiniZinc']['symmetry_breaking_config']}", "r") as file:
        settings = load(file)

    constraint = None
    for breaker in settings["SB-Constraints"]:
        if breaker["Tag"] == symmetry_breaker:
            constraint = breaker["Constraint"]
            break
    if constraint != None:
        constraint = "constraint " + constraint
        constraint = constraint.replace("[Start]", str(start))

    return constraint

def buildComponentConstraints(component: str, inst: int, startVM: int, Clist: list = []):
    """
    Returns the list of constraints for setting the FV script
    for a specific component.

    Args:
        component (str): The name of the component
        inst      (int): The number of instances for that component
        startVM (int): The first machine to be assigned.
        Clist (list, optional): A list of components in conflict with the current component. Defaults to [].

    Returns:
        constraints (list): A list of constraints to be added
        endVM (int): The first machine free of assignment
    """

    endVM = startVM + inst
    constraints = []

    for i in range (inst):
        constraint = f"constraint AssignmentMatrix[{component},{startVM+i+1}] = 1;\n"
        constraints.append(constraint)

    for i in range(inst):
        for c in Clist:
            if component != c:
                constraints.append(f"constraint AssignmentMatrix[{c}, {startVM+i+1}] = 0;\n")

    return constraints, endVM



def getFVConstraints(use_case: str, scaling_components: list = []):
    """
    Returns a list of constraints to be inserted in the MiniZinc model.

    Args:
        use_case (str): The name of the use-case
        scaling_components (list, optional): A list of scaling components and their instances.

    Returns:
        constraints (list): A list of constraints to be added inside the MiniZinc model.
    """

    map, instances = getMaxClique(use_case, scaling_components)
    constraints = []
    clique = {}

    start = 0

    # The clique format should be as follows:
    #     { "COMP_NAME" : INST }
    for i in instances:
        for key in map.keys():
            if i in map[key]:
                try:
                    clique[key] += 1
                    break
                except KeyError:
                    clique[key] = 1
                    break

    Clist = []
    for component in clique.keys():
        Clist.append(component)

    for component in clique.keys():
        output = buildComponentConstraints(component, clique[component], start, Clist)

        for constraint in output[0]:
            constraints.append(constraint)
        start = output[1]

    return constraints, start

def getSymmetryBreakerConstraints(sym_breaker: str, use_case: str, scaling_components: list = []):
    """
    Constructs all constraints for a symmetry breaker.

    Args:
        sym_breaker (str): The tag of the symmetry breaking technique
        use_case (str): The name of the use case
        scaling_components (list, optional): A list of scaling components and their instances. Defaults to []

    Returns:
        constraints (list): A list of all additional constraints.
    """
    constraints = []
    start = 0

    if sym_breaker.startswith("FV"):
        output = getFVConstraints(use_case, scaling_components)

        for constraint in output[0]:
            constraints.append(constraint)
        sym_breaker = sym_breaker[2::]
        start = output[1]
    constraints.append(addBreakerConstraint(sym_breaker, start + 1))

    return constraints
