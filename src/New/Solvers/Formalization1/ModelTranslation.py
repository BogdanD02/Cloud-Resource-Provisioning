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

def GetMiniZincSurrogateConstraints(R: Restriction) -> list:
    constraints = []

    if R.GetType() == "RequireProvide":
        constraint = "constraint requireProvide("
        constraint += R.GetElement("RequireComponent") + ", "
        constraint += R.GetElement("ProvideComponent") + ", "
        constraint += str(R.GetElement("RequireInstances")) + ", "
        constraint += str(R.GetElement("ProvideInstances")) + ");\n"
        constraints.append(StringToBytes(constraint))
    elif R.GetType().endswith("Bound"):
        if R.GetType() == "EqualBound":
            
            constraint  = "constraint equalBound("
            for Component in R.GetElement("Components"):
                constraint += Component+ ", "
            constraint += str(R.GetElement("Bound")) + ");\n"
            constraints.append(StringToBytes(constraint))
        elif R.GetType() == "LowerBound":
            constraint  = "constraint lowerBound("
            for Component in R.GetElement("Components"):
                constraint += Component + ", "
            constraint += str(R.GetElement("Bound")) + ");\n"
            constraints.append(StringToBytes(constraint))
        elif R.GetType() == "UpperBound":
            constraint  = "constraint upperBound("
            for Component in R.GetElement("Components"):
                constraint += Component + ", "
            constraint += str(R.GetElement("Bound")) + ");\n"
            constraints.append(StringToBytes(constraint))

    return constraints

def GetSurrogateComponentModels(Components: list = [], Excluded: list = []) -> list:
    constraints = []

    for Comp in Components:
        if Comp.Name not in Excluded:
            constraints.append(StringToBytes("var 0..1024: " + Comp.Name + ";\n"))
    constraints.append(StringToBytes("\n"))

    return constraints

def GetHeaders(SB: str = None, isSurrogate: bool = False) -> list:
    headers = []

    if not isSurrogate:
        headers.append(StringToBytes('include "Modules/Formalization1/GeneralVariables.mzn";\n'))
        headers.append(StringToBytes('include "Modules/Formalization1/GeneralConstraints.mzn";\n'))

        if SB:
            headers.append(StringToBytes('include "Modules/Formalization1/SymmetryBreaking.mzn";\n'))

        headers.append(StringToBytes("\n"))
    else:
        headers.append(StringToBytes('include "Modules/Formalization1/SurrogateConstraints.mzn";\n\n'))

    return headers

def GetComponentModels(Components: list = []) -> list:
    constraints = []

    for index, Comp in enumerate(Components):
        constraints.append(StringToBytes("int: " + Comp.Name + " = " + str(index + 1) + ";\n"))
    constraints.append(StringToBytes("\n"))

    return constraints

def GetSurrogateBasicAllocation(Components: list, OrComponents: list, Excluded: list) -> bytes:
    constraint = "constraint basicAllocation({"

    for i, Component in enumerate(Components):
        if (Component.Name in OrComponents) or (Component.Name in Excluded):
            continue

        if i != len(Components) - 1:
            constraint += Component.Name + ", "
        else:
            constraint += Component.Name
    if constraint.endswith(", "):
        constraint = constraint[:-2]
    constraint += "});\n"
    return StringToBytes(constraint)

def GetBasicAllocation(OrComponents: list = None) -> bytes:
    constraint = "constraint basicAllocation(AssignmentMatrix, {"
        
    for i, Component in enumerate(OrComponents):
        if i != len(OrComponents) - 1:
            constraint += Component + ", "
        else:
            constraint += Component

    constraint += "}, S, VM);\n"

    return StringToBytes(constraint)


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
        constraints.append(StringToBytes(constraint))
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
            constraints.append(StringToBytes(constraint))
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
        constraints.append(StringToBytes(constraint))
    elif R.GetType() == "RequireProvide":
        constraint = "constraint requireProvide(AssignmentMatrix, VM, "
        constraint += R.GetElement("RequireComponent") + ", "
        constraint += R.GetElement("ProvideComponent") + ", "
        constraint += str(R.GetElement("RequireInstances")) + ", "
        constraint += str(R.GetElement("ProvideInstances")) + ");\n"
        constraints.append(StringToBytes(constraint))
    elif R.GetType().endswith("Bound"):
        if R.GetType() == "EqualBound":
            
            constraint  = "constraint equalBound(AssignmentMatrix, VM, "
            for Component in R.GetElement("Components"):
                constraint += Component+ ", "
            constraint += str(R.GetElement("Bound")) + ");\n"
            constraints.append(StringToBytes(constraint))
        elif R.GetType() == "LowerBound":
            constraint  = "constraint lowerBound(AssignmentMatrix, VM, "
            for Component in R.GetElement("Components"):
                constraint += Component + ", "
            constraint += str(R.GetElement("Bound")) + ");\n"
            constraints.append(StringToBytes(constraint))
        elif R.GetType() == "UpperBound":
            constraint  = "constraint upperBound(AssignmentMatrix, VM, "
            for Component in R.GetElement("Components"):
                constraint += Component + ", "
            constraint += str(R.GetElement("Bound")) + ");\n"
            constraints.append(StringToBytes(constraint))
    elif R.GetType() == "ExculsiveDeployment":
        constraint = "constraint exclusiveDeployment(AssignmentMatrix, VM, "
        constraint += R.GetElement("Components")[0] + ", "
        constraint += R.GetElement("Components")[1] + ");\n"
        constraints.append(StringToBytes(constraint))
    elif R.GetType() == "BoundedRequireProvide":
        constraint = "constraint boundedRequireProvide(AssignmentMatrix, VM, "
        constraint += R.GetElement("ProvideComponent") + ", "
        constraint += R.GetElement("RequireComponent") + ", "
        constraint += str(R.GetElement("ProvideInstances"))
        constraint += ");\n"

        constraints.append(StringToBytes(constraint))
    
    return constraints

def EndIf() -> bytes:
    return StringToBytes("endif;\n")

def GetORCloser(ORComps: list) -> bytes:
    constraint = "constraint "

    for i, Comp in enumerate(ORComps):
        constraint += Comp

        if i != len(ORComps) - 1:
            constraint += " + "
    constraint += ">= 1;\n"

    if ORComps != []:
        return StringToBytes(constraint)
    return StringToBytes("\n")

def GetORConstraint(R: Restriction, Surrogate: bool = True) -> bytes:
    if Surrogate:
        if R.GetType() == "RequireProvide":
            constraint = "requireProvide("
            constraint += R.GetElement("RequireComponent") + ", "
            constraint += R.GetElement("ProvideComponent") + ", "
            constraint += str(R.GetElement("RequireInstances")) + ", "
            constraint += str(R.GetElement("ProvideInstances")) + ")\n"
            return StringToBytes(constraint)
        elif R.GetType().endswith("Bound"):
            if R.GetType() == "EqualBound":
                
                constraint  = "equalBound("
                for Component in R.GetElement("Components"):
                    constraint += Component+ ", "
                constraint += str(R.GetElement("Bound")) + ")\n"
                return StringToBytes(constraint)
            elif R.GetType() == "LowerBound":
                constraint  = "lowerBound("
                for Component in R.GetElement("Components"):
                    constraint += Component+ ", "
                constraint += str(R.GetElement("Bound")) + ")\n"
                return StringToBytes(constraint)
            elif R.GetType() == "UpperBound":
                constraint  = "upperBound("
                for Component in R.GetElement("Components"):
                    constraint += Component+ ", "
                constraint += str(R.GetElement("Bound")) + ")\n"
                return StringToBytes(constraint)
    else:
        if R.GetType() == "Conflict":
            constraint = "constraint conflict(AssignmentMatrix, {"

            for i, C in enumerate(R.GetElement("Components")):
                if i != len(R.GetElement("Components")) - 1:
                    constraint += C + ", "
                else:
                    constraint += C + "}, "
            constraint += "VM, " + R.GetElement("AlphaComponent") + ")\n"
            return StringToBytes(constraint)
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
                constraint += "VM, NoComponents, " + Component + ")\n"
                return StringToBytes(constraint)
        elif R.GetType() == "Colocation":
            constraint = "constraint colocation(AssignmentMatrix, {"

            for i, C in enumerate(R.GetElement("Components")):
                if i != len(R.GetElement("Components")) - 1:
                    constraint += C + ", "
                else:
                    constraint += C
            else:
                constraint += "}, "
            constraint += "VM)\n"
            return StringToBytes(constraint)
        elif R.GetType() == "RequireProvide":
            constraint = "constraint requireProvide(AssignmentMatrix, VM, "
            constraint += R.GetElement("RequireComponent") + ", "
            constraint += R.GetElement("ProvideComponent") + ", "
            constraint += str(R.GetElement("RequireInstances")) + ", "
            constraint += str(R.GetElement("ProvideInstances")) + ")\n"
            return StringToBytes(constraint)
        elif R.GetType().endswith("Bound"):
            if R.GetType() == "EqualBound":
                
                constraint  = "constraint equalBound(AssignmentMatrix, VM, "
                for Component in R.GetElement("Components"):
                    constraint += Component+ ", "
                constraint += str(R.GetElement("Bound")) + ")\n"
                return StringToBytes(constraint)
            elif R.GetType() == "LowerBound":
                constraint  = "constraint lowerBound(AssignmentMatrix, VM, "
                for Component in R.GetElement("Components"):
                    constraint += Component + ", "
                constraint += str(R.GetElement("Bound")) + ")\n"
                return StringToBytes(constraint)
            elif R.GetType() == "UpperBound":
                constraint  = "constraint upperBound(AssignmentMatrix, VM, "
                for Component in R.GetElement("Components"):
                    constraint += Component + ", "
                constraint += str(R.GetElement("Bound")) + ")\n"
                return StringToBytes(constraint)
        elif R.GetType() == "BoundedRequireProvide":
            constraint = "constraint boundedRequireProvide(AssignmentMatrix, VM, "
            constraint += R.GetElement("ProvideComponent") + ", "
            constraint += R.GetElement("RequireComponent") + ", "
            constraint += str(R.GetElement("ProvideInstances"))
            constraint += ")\n"
            return StringToBytes(constraint)

def BeginIf(Comp: str, Surrogate: bool = True) -> bytes:
    if Surrogate:
        return StringToBytes("constraint if " + Comp + " > 0 then\n")
    else:
        return StringToBytes("constraint if isDeployed(AssignmentMatrix, VM, " + Comp + ") then\n")

def GetObjective(isSurrogate: bool = False, Components: list = [], Excluded: list = []):
    if not isSurrogate:
        return StringToBytes("solve minimize sum(k in 1..VM)(Price[k]);\n")
    else:
        constraint = "solve minimize "
        for index, Comp in enumerate(Components):
            if Comp.Name in Excluded:
                continue

            if index != len(Components) - 1:
                constraint += Comp.Name + " + "
            else:
               constraint += Comp.Name

        if constraint.endswith(" + "):
            constraint = constraint[:-3]

        constraint += ";"
        return StringToBytes(constraint)