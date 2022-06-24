from datetime import timedelta
import minizinc as mzn
import src.init
from os import unlink
from src.New.Core.Solver import Solver
from src.New.Core.Instance import Instance
from src.New.Core.Restriction import Restriction
from tempfile import NamedTemporaryFile


class MiniZinc_Solver(Solver):
    """
    This class models MiniZinc solvers such as Chuffed or Gecode.
    
    Its purpose is to adapt the raw model to the MiniZinc format and convert
    the Instance to a MiniZinc instance which can then be run using MiniZinc solvers.
    """

    def __init__(self, keyword: str, Inst: Instance, saveFiles: bool = False) -> None:
        """
        Creates a new MiniZinc solver.

        Args:
            keyword (str): The name of the solver to instantiate.
            Inst (Instance): The problem instance we want to solve.
            saveFiles (bool, optional): Flag that tells the solver not to delete model files. Defaults to False.
        """
        super().__init__(Inst)

        self.__Solver = super()._GetMiniZincSolver(keyword)
        self.__SaveFlag = saveFiles

        if not saveFiles:
            self.__ModelFile = NamedTemporaryFile(delete=False, suffix='.' + src.init.settings['MiniZinc']['model_ext'], dir=src.init.settings['MiniZinc']['model_path'])
            self.__DataFile = NamedTemporaryFile(delete=False, suffix='.' + src.init.settings['MiniZinc']['input_ext'], dir=src.init.settings['MiniZinc']['input_path'])
        else:
            self.__ModelFile = open(f"{src.init.settings['MiniZinc']['model_path']}/{self._Instance.GetModel().Name}_{self._Instance.GetSB()}.{src.init.settings['MiniZinc']['model_ext']}", "w")
            self.__DataFile = open(f"{src.init.settings['MiniZinc']['input_path']}/{self._Instance.GetModel().Name}_Offers{len(self._Instance.GetOffers())}.{src.init.settings['MiniZinc']['input_ext']}", "w")

        self.__ModelFile.truncate(0)
        self.__DataFile.truncate(0)

    def __del__(self):
        """
        Destroys the created temporary files when solver goes out of scope.
        """
        self.__ModelFile.close()
        self.__DataFile.close()

        if not self.__SaveFlag:
            unlink(self.__ModelFile.name)
            unlink(self.__DataFile.name)

    def __GetOrComponents(self) -> list:
        """
        Returns a list of components found in exclusive deployment

        Returns:
            list: Components found in exclusive deployment
        """
        for R in self._Instance.GetModel().Restrictions:
            if R.GetType() == "ExclusiveDeployment":
                return R.GetElement("Components")
        return []

    def __GetMaxRequirements(self) -> int:
        """
        Returns the maximum number of requirements a component has.
        
        Returns:
            int: The number of requirements.
        """
        N = 0

        for Comp in self._Instance.GetModel().Components:
            if len(Comp.HardwareRequirements) > N:
                N = len(Comp.HardwareRequirements)
        return N

    def __ComputeMiniZincModel(self, surrogateResults):
        """
        Converts the current Model into a MiniZinc model file.
        """
        if src.init.settings['MiniZinc']['formalization'] == 1:
            from src.New.Solvers.Formalization1.ModelTranslation import GetMiniZincConstraints, GetHeaders, GetBasicAllocation, GetComponentModels, GetObjective, BeginIf, EndIf, GetORConstraint
        else:
            from src.New.Solvers.Formalization2.ModelTranslation import GetMiniZincConstraints, GetHeaders, GetBasicAllocation, GetComponentModels, GetObjective

        for header in GetHeaders(self._Instance.GetSB(), False):
            self.__ModelFile.write(header)

        for item in GetComponentModels(self._Instance.GetModel().Components):
            self.__ModelFile.write(item)

        for item in GetMiniZincConstraints():
            self.__ModelFile.write(item)

        OrComponents = self.__GetOrComponents()
        self.__ModelFile.write(GetBasicAllocation(OrComponents))

        CheckedComponents = []
        AditionalRestrictions = []

        for Comp in self._Instance.GetModel().Components:
            try:
                temp = Restriction("EqualBound")
                temp.AddElement(("Components", [Comp.Name]))
                temp.AddElement(("Bound", surrogateResults[Comp.Name]))

                CheckedComponents.append(Comp.Name)
                AditionalRestrictions.append(temp)
            except KeyError:
                continue

        indexes = []
        for i, Constraint in enumerate(self._Instance.GetModel().GetRestrictions()):
            if Constraint.GetType().endswith("Bound") and len(Constraint.GetElement("Components")) == 1:
                if Constraint.GetElement("Components")[0] in CheckedComponents:
                    indexes.append(i)
            elif Constraint.GetType().endswith("Bound"):
                Removed = []
                for Comp in Constraint.GetElement("Components"):
                    if Comp in CheckedComponents:
                        Removed.append(Comp)
                        Constraint.Elements["Bound"] -= surrogateResults[Comp]
                for Comp in Removed:
                    Constraint.GetElement("Components").remove(Comp)
                if Constraint.GetElement("Components") == []:
                    indexes.append(i)
            elif Constraint.GetType() == "RequireProvide" and Constraint.GetElement("RequireComponent") in CheckedComponents and Constraint.GetElement("ProvideComponent") in CheckedComponents:
                indexes.append(i)
            elif Constraint.GetType() == "BoundedRequireProvide" and Constraint.GetElement("RequireComponent") in CheckedComponents and Constraint.GetElement("ProvideComponent") in CheckedComponents:
                indexes.append(i)

        indexes.sort(reverse=True)

        print(CheckedComponents)

        for i in indexes:
            self._Instance.GetModel().GetRestrictions().pop(i)

        self._Instance.GetModel().GetRestrictions().extend(AditionalRestrictions)

        for Constraint in self._Instance.GetModel().GetRestrictions():
            for translation in GetMiniZincConstraints(Constraint):
                self.__ModelFile.write(translation)

        self.__ModelFile.write(GetObjective())
        self.__ModelFile.seek(0)

    def __checkAppearances(self, Comp) -> bool:
        for Constraint in self._Instance.GetModel().GetRestrictions():
            if Constraint.GetType().endswith("Bound"):
                for key, item in Constraint.Elements.items():
                    if key.find("Component") != -1:
                        if Comp in item:
                            return False
        return True

    def __GetExcludedComponents(self) -> list:
        compList = []

        for Constraint in self._Instance.GetModel().GetRestrictions():
            if Constraint.GetType() == "Colocation" or Constraint.GetType() == "FullDeployment":
                for Comp in Constraint.GetElement("Components"):
                    if not Comp in compList and self.__checkAppearances(Comp):
                        compList.append(Comp)
        return compList

    def __GenerateSurrogateModel(self):
        """
        Generates the surrogate model from the Json model
        """
        if src.init.settings['MiniZinc']['formalization'] == 1:
            from src.New.Solvers.Formalization1.ModelTranslation import GetMiniZincSurrogateConstraints, GetHeaders, GetSurrogateComponentModels, GetObjective, GetSurrogateBasicAllocation, BeginIf, GetORConstraint, GetORCloser, EndIf
        else:
            from src.New.Solvers.Formalization2.ModelTranslation import GetMiniZincSurrogateConstraints, GetHeaders, GetSurrogateComponentModels, GetObjective, GetSurrogateBasicAllocation

        for item in GetHeaders(isSurrogate=True):
            self.__ModelFile.write(item)

        ExcludedFromSurrogate = self.__GetExcludedComponents()

        for item in GetSurrogateComponentModels(self._Instance.GetModel().Components, ExcludedFromSurrogate):
            self.__ModelFile.write(item)

        OrComponents = self.__GetOrComponents()
        self.__ModelFile.write(GetSurrogateBasicAllocation(self._Instance.GetModel().Components, OrComponents, ExcludedFromSurrogate))

        for Constraint in self._Instance.GetModel().GetRestrictions():

            excluded = 0
            for Comp in OrComponents:
                for key, item in Constraint.Elements.items():
                    if key.find("Component") != -1 and Comp in item:
                        excluded = 1
                        break
                if excluded == 1:
                    break

            if excluded == 0:
                for Comp in ExcludedFromSurrogate:
                    for key, item in Constraint.Elements.items():
                        if key.find("Component") != -1 and Comp in item:
                            excluded = 1
                            break
                    if excluded == 1:
                        break

            if excluded == 1:
                excluded = 0
                continue

            if Constraint.GetType().endswith("Bound") or Constraint.GetType() == "RequireProvide":
                for translation in GetMiniZincSurrogateConstraints(Constraint):
                    self.__ModelFile.write(translation)

        for Comp in OrComponents:
            self.__ModelFile.write(BeginIf(Comp))

            count = 0
            for Constraint in self._Instance.GetModel().GetRestrictions():
                if Constraint.GetType().endswith("Bound"):
                    if Comp in Constraint.GetElement("Components"):
                        count += 1
                elif Constraint.GetType() == "RequireProvide":
                    if Comp in Constraint.GetElement("RequireComponent") or Comp in Constraint.GetElement("ProvideComponent"):
                        count += 1

            for Constraint in self._Instance.GetModel().GetRestrictions():
                if Constraint.GetType().endswith("Bound"):
                    if Comp in Constraint.GetElement("Components"):
                        self.__ModelFile.write(GetORConstraint(Constraint))

                        count -= 1
                        if count != 0:
                            self.__ModelFile.write(b" /\ ")
                elif Constraint.GetType() == "RequireProvide":
                    if Comp in Constraint.GetElement("RequireComponent") or Comp in Constraint.GetElement("ProvideComponent"):
                        self.__ModelFile.write(GetORConstraint(Constraint))
                
                        count -= 1
                        if count != 0:
                            self.__ModelFile.write(b" /\ ")
            self.__ModelFile.write(EndIf())

        self.__ModelFile.write(GetORCloser(OrComponents))
        self.__ModelFile.write(GetObjective(True, self._Instance.GetModel().Components, ExcludedFromSurrogate))

        self.__ModelFile.seek(0)

    def __ConvertDataFile(self):
        """
        Converts the data taken from the JSON data file into a suitable MiniZinc format.
        """

        VMPrice = []
        VMSpecs = []

        for Offer in self._Instance.GetOffers():
            VMPrice.append(Offer.GetPrice())
            VMSpecs.append(Offer.GetSpecifications().values())

        if src.init.settings['MiniZinc']['formalization'] == 1:
            from src.New.Solvers.Formalization1.ModelTranslation import StringToBytes
        else:
            from src.New.Solvers.Formalization2.ModelTranslation import StringToBytes

        self.__DataFile.write(StringToBytes("NoComponents = " + str(len(self._Instance.GetModel().Components)) + ";\n"))
        self.__DataFile.write(StringToBytes("HardwareREQ = " + str(self.__GetMaxRequirements()) + ";\n"))
        self.__DataFile.write(StringToBytes("VMOffers = " + str(len(VMPrice)) + ";\n"))
        self.__DataFile.write(StringToBytes("CompREQ = ["))

        for index, Comp in enumerate(self._Instance.GetModel().Components):
            if index != len(self._Instance.GetModel().Components) - 1:
                self.__DataFile.write(b'|')
                for item in Comp.HardwareRequirements.values():
                    self.__DataFile.write(StringToBytes(str(item) + ", "))
                self.__DataFile.write(StringToBytes("\n"))
            else:
                self.__DataFile.write(b'|')
                for i, item in enumerate(Comp.HardwareRequirements.values()):
                    if i != len(Comp.HardwareRequirements.values()) - 1:
                        self.__DataFile.write(StringToBytes(str(item) + ", "))
                    else:
                        self.__DataFile.write(StringToBytes(str(item)))
                self.__DataFile.write(StringToBytes("|];\n"))

        self.__DataFile.write(b"VMPrice = [")

        for index, Price in enumerate(VMPrice):
            if index != len(VMPrice) - 1:
                self.__DataFile.write(StringToBytes(str(Price) + ", "))
            else:
                self.__DataFile.write(StringToBytes(str(Price) + "];\n"))
        
        self.__DataFile.write(b"VMSpecs = [")

        for index, Specs in enumerate(VMSpecs):
            if index != len(VMSpecs) - 1:
                self.__DataFile.write(b"|")
                
                for item in Specs:
                    self.__DataFile.write(StringToBytes(str(item) + ", ")) 
                
                self.__DataFile.write(b"\n")
            else:
                self.__DataFile.write(b"|")
                
                for itemIndex, item in enumerate(Specs):
                    if itemIndex != len(Specs) - 1:
                        self.__DataFile.write(StringToBytes(str(item) + ", ")) 
                    else:
                        self.__DataFile.write(StringToBytes(str(item) + "|];"))

                self.__DataFile.write(b"\n") 
        self.__DataFile.seek(0)

    def __SolveSurrogate(self):
        """
        Solves the surrogate model
        """
        Mzn_Instance = mzn.Instance(self.__Solver, mzn.Model(self.__ModelFile.name))

        return Mzn_Instance.solve(timeout=timedelta(seconds=2400))

    def Solve(self):
        self.__GenerateSurrogateModel()
        items = self.__SolveSurrogate()

        self.__ModelFile.truncate(0)

        self.__ComputeMiniZincModel(items)
        self.__ConvertDataFile()

        Mzn_Instance = mzn.Instance(self.__Solver, mzn.Model(self.__ModelFile.name))
        Mzn_Instance.add_file(self.__DataFile.name)
        Mzn_Instance["VM"] = items["objective"]

        return Mzn_Instance.solve(timeout=timedelta(seconds=2400))