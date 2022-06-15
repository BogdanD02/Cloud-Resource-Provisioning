from src.New.Core.Restriction import Restriction
from src.New.Core.Model import Model
from src.New.Core.Component import Component
from src.New.Core.SymmetryBreaking.ConflictGraph import GetMaxClique

def GetFV_Constraints(model: Model, preCompute: bool = False):
    """
    This script generates the FV constraints obtained for a specific model.

    Args:
        model (Model): The model for which to generate the constraints
    
    Returns:
        constraints (list): A list of Restriction objects.
    """
    Constraints = []
    CurrentVM = 0
    Clique, Map = GetMaxClique(model)
    
    for Element in Clique:
        Temp = Restriction("FixComponent")
        Temp.AddElement(("VM", CurrentVM))
        Temp.AddElement(("Component", Map[Element]))
        Temp.AddElement(("Value", 1))
        Constraints.append(Temp)

        Seen = {Map[Element]}
        for Component in Map.values():
            if Component not in Seen:
                Temp = Restriction("FixComponent")
                Temp.AddElement(("VM", CurrentVM))
                Temp.AddElement(("Component", Component))
                Temp.AddElement(("Value", 0))

                Constraints.append(Temp)
                Seen.add(Component)
        CurrentVM += 1

    if preCompute:
        AdditionalConstraints = []

        for Constraint in Constraints:
            CurrentVM = Constraint.GetElement("VM")

            for Restr in model.GetRestrictions():
                if Restr.GetType() == "Conflict" and Restr.GetElement("AlphaComponent") == Constraint.GetElement("Component"):
                    for ConflictingComponent in Restr.GetElement("Components"):
                        if ConflictingComponent not in Map.values():
                            Temp = Restriction("FixComponent")
                            Temp.AddElement(("VM", CurrentVM))
                            Temp.AddElement(("Component", ConflictingComponent))
                            Temp.AddElement(("Value", 0))

                            AdditionalConstraints.append(Temp)
                elif Restr.GetType() == "Conflict" and Constraint.GetElement("Component") in Restr.GetElement("Components"):
                    if Restr.GetElement("AlphaComponent") not in Map.values():
                        Temp = Restriction("FixComponent")
                        Temp.AddElement(("VM", CurrentVM))
                        Temp.AddElement(("Component", Restr.GetElement("AlphaComponent")))
                        Temp.AddElement(("Value", 0))

                        AdditionalConstraints.append(Temp)
                elif Restr.GetType() == "Colocation" and Constraint.GetElement("Component") in Restr.GetElement("Components"):
                    for Colocator in Restr.GetElement("Components"):
                        if Colocator not in Map.keys():
                            Temp = Restriction("FixComponent")
                            Temp.AddElement(("VM", CurrentVM))
                            Temp.AddElement(("Component", Colocator))
                            Temp.AddElement(("Value", 1))

                            AdditionalConstraints.append(Temp)
                elif Restr.GetType() == "FullDeployment":
                    for Comp in Restr.GetElement("Components"):
                        if Comp not in Map.values() and FreeOfConflicts(Comp, CurrentVM):
                            Temp = Restriction("FixComponent")
                            Temp.AddElement(("VM", CurrentVM))
                            Temp.AddElement(("Component", Comp))
                            Temp.AddElement(("Value", 1))

                            AdditionalConstraints.append(Temp)

    return Constraints

def FreeOfConflicts(Comp: Component, VM: int, Assignments: list) -> bool:
    pass