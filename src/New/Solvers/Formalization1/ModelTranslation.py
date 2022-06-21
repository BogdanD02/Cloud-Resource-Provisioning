from src.New.Core.Restriction import Restriction

"""
This file provides functions responsible with translating data
from Json to MiniZinc format.
"""

def StringToBytes(item: str) -> bytes:
    """
    Converts a given string to bytes.

    Args:
        item (str): The string to be converted

    Returns:
        bytes: The bytes conversion of the string
    """
    return bytes(item.encode('utf-8'))

def GetMiniZincSurrogateConstraints(R: Restriction):
    constraints = []

    if R.GetType() == "RequireProvide":
        constraint = "constraint requireProvide("
        constraint += R.GetElement("RequireComponent") + ", "
        constraint += R.GetElement("ProvideComponent") + ", "
        constraint += str(R.GetElement("RequireInstances")) + ", "
        constraint += str(R.GetElement("ProvideInstances")) + ");\n"
        constraints.append(constraint)
    elif R.GetType().endswith("Bound"):
        if R.GetType() == "EqualBound":
            
            constraint  = "constraint equalBound("
            for Component in R.GetElement("Components"):
                constraint += Component+ ", "
            constraint += str(R.GetElement("Bound")) + ");\n"
            constraints.append(constraint)
        elif R.GetType() == "LowerBound":
            constraint  = "constraint lowerBound("
            for Component in R.GetElement("Components"):
                constraint += Component + ", "
            constraint += str(R.GetElement("Bound")) + ");\n"
            constraints.append(constraint)
        elif R.GetType() == "UpperBound":
            constraint  = "constraint upperBound("
            for Component in R.GetElement("Components"):
                constraint += Component + ", "
            constraint += str(R.GetElement("Bound")) + ");\n"
            constraints.append(constraint)

    return constraints

def GetMiniZincConstraints(R: Restriction = None):
    constraints = []

    if not R:
        constraints.append(StringToBytes("constraint capacity(AssignmentMatrix, CompREQ, VMSpecs, VMType, HardwareREQ, NoComponents, VM);\n"))
        constraints.append(StringToBytes("constraint link(VMSpecs, VMPrice, OccupancyVector, VMType, Price, VMOffers, VM);\n"))
        constraints.append(StringToBytes("constraint occupancy(AssignmentMatrix, OccupancyVector, NoComponents, VM);\n"))

        return constraints

    if R.GetType() == "Conflict":
        constraint = "constraint conflict(AssignmentMatrix, {"

        for i, C in enumerate(R.GetElement("Components")):
            if i != len(R.GetElement("Components")) - 1:
               constraint += C + ", "
            else:
                constraint += C + "}, "
        constraint += "VM, " + R.GetElement("AlphaComponent") + ");\n"
        constraints.append(constraint)
    elif R.GetType() == "FullDeployment":
        for Component in R.GetElement("Components"):
            constraint = "constraint fullDeployment(AssignmentMatrix, {"

            try:
                for i, C in enumerate(R.GetElement("Conflicts")):
                    if i != len(R.GetElement("Conflicts")) - 1:
                        constraint += C + ", "
                    else:
                        constraint += C
                else:
                    constraint += "}, "
            except KeyError:
                constraint += "}, "
            constraint += "VM, NoComponents, " + Component + ");\n"
            constraints.append(constraint)
    elif R.GetType() == "Colocation":
        constraint = "constraint colocation(AssignmentMatrix, {"

        for i, C in enumerate(R.GetElement("Components")):
            if i != len(R.GetElement("Components")) - 1:
                constraint += C + ", "
            else:
                constraint += C
        else:
            constraint += "}, "
        constraint += "VM);\n"
        constraints.append(constraint)
    elif R.GetType() == "RequireProvide":
        constraint = "constraint requireProvide(AssignmentMatrix, VM, "
        constraint += R.GetElement("RequireComponent") + ", "
        constraint += R.GetElement("ProvideComponent") + ", "
        constraint += str(R.GetElement("RequireInstances")) + ", "
        constraint += str(R.GetElement("ProvideInstances")) + ");\n"
        constraints.append(constraint)
    elif R.GetType().endswith("Bound"):
        if R.GetType() == "EqualBound":
            
            constraint  = "constraint equalBound(AssignmentMatrix, VM, "
            for Component in R.GetElement("Components"):
                constraint += Component+ ", "
            constraint += str(R.GetElement("Bound")) + ");\n"
            constraints.append(constraint)
        elif R.GetType() == "LowerBound":
            constraint  = "constraint lowerBound(AssignmentMatrix, VM, "
            for Component in R.GetElement("Components"):
                constraint += Component + ", "
            constraint += str(R.GetElement("Bound")) + ");\n"
            constraints.append(constraint)
        elif R.GetType() == "UpperBound":
            constraint  = "constraint upperBound(AssignmentMatrix, VM, "
            for Component in R.GetElement("Components"):
                constraint += Component + ", "
            constraint += str(R.GetElement("Bound")) + ");\n"
            constraints.append(constraint)
    elif R.GetType() == "ExculsiveDeployment":
        constraint = "constraint exclusiveDeployment(AssignmentMatrix, VM, "
        constraint += R.GetElement("AlphaComponent") + ", "
        constraint += R.GetElement("BetaComponent") + ");\n"
    
    return constraints