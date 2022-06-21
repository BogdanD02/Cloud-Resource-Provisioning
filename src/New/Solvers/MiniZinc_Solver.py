from datetime import timedelta
import enum
import minizinc as mzn
import src.init
from os import remove, system, unlink
from os.path import exists
from src.New.Core.Solver import Solver
from src.New.Core.Instance import Instance
from tempfile import NamedTemporaryFile


class MiniZinc_Solver(Solver):
    """
    This class models MiniZinc solvers such as Chuffed or Gecode.
    
    Its purpose is to adapt the raw model to the MiniZinc format and convert
    the Instance to a MiniZinc instance which can then be run using MiniZinc solvers.
    """

    def __init__(self, keyword: str, Inst: Instance) -> None:
        """
        Creates a new MiniZinc solver.

        Args:
            keyword (str): The name of the solver to instantiate.
            Inst (Instance): The problem instance we want to solve.
        """
        super().__init__(Inst)

        self.__Solver = super()._GetMiniZincSolver(keyword)
        self.__ModelFile = NamedTemporaryFile(delete=False, suffix='.' + src.init.settings['MiniZinc']['model_ext'], dir=src.init.settings['MiniZinc']['model_path'])
        self.__DataFile = NamedTemporaryFile(delete=False, suffix='.' + src.init.settings['MiniZinc']['input_ext'], dir=src.init.settings['MiniZinc']['input_path'])
        
    def __del__(self):
        """
        Destroys the created temporary files when solver goes out of scope.
        """
        self.__ModelFile.close()
        unlink(self.__ModelFile.name)

        self.__DataFile.close()
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

    def __ComputeMiniZincModel(self):
        """
        Converts the current Model into a MiniZinc model file.
        """
        if src.init.settings['MiniZinc']['formalization'] == 1:
            from src.New.Solvers.Formalization1.ModelTranslation import GetMiniZincConstraints, StringToBytes
        else:
            from src.New.Solvers.Formalization2.ModelTranslation import GetMiniZincConstraints

        self.__ModelFile.write(StringToBytes('include "Modules/Formalization' + str(src.init.settings['MiniZinc']['formalization']) + '/GeneralVariables.mzn";\n'))
        self.__ModelFile.write(StringToBytes('include "Modules/Formalization' + str(src.init.settings['MiniZinc']['formalization']) + '/GeneralConstraints.mzn";\n\n'))

        if self._Instance.GetSB():
            self.__ModelFile.write(StringToBytes('include "Modules/Formalization' + str(src.init.settings['MiniZinc']['formalization']) + '/SymmetryBreaking.mzn";\n\n'))

        for index, Comp in enumerate(self._Instance.GetModel().Components):
            self.__ModelFile.write(StringToBytes("int: " + Comp.Name + " = " + str(index + 1) + ";\n"))
        self.__ModelFile.write(b'\n')

        for item in GetMiniZincConstraints():
            self.__ModelFile.write(item)

        OrComponents = self.__GetOrComponents()
        self.__ModelFile.write(StringToBytes("constraint basicAllocation(AssignmentMatrix, {"))
        
        for i, Component in enumerate(OrComponents):
            if i != len(OrComponents) - 1:
                self.__ModelFile.write(StringToBytes(Component + ", "))
            else:
                self.__ModelFile.write(StringToBytes(Component))
        self.__ModelFile.write(StringToBytes("}, "))
        self.__ModelFile.write(StringToBytes("S, VM);\n"))

        for Constraint in self._Instance.GetModel().GetRestrictions():
            excluded = 0

            if Constraint.GetType().endswith("Bound"):
                for C in Constraint.GetElement("Components"):
                    if C in OrComponents:
                        excluded = 1
                        break

            elif Constraint.GetType() == "RequireProvide":
                if Constraint.GetElement("ProvideComponent") in OrComponents or Constraint.GetElement("RequireComponent") in OrComponents:
                    excluded = 1

            if excluded == 1:
                excluded = 0
                continue

            for translation in GetMiniZincConstraints(Constraint):
                self.__ModelFile.write(StringToBytes(translation))

        self.__ModelFile.write(StringToBytes("solve minimize sum(k in 1..VM)(Price[k]);\n"))
        self.__ModelFile.seek(0)
    
    def __GenerateSurrogateModel(self):
        """
        Generates the surrogate model from the Json model
        """
        if src.init.settings['MiniZinc']['formalization'] == 1:
            from src.New.Solvers.Formalization1.ModelTranslation import GetMiniZincSurrogateConstraints, StringToBytes
        else:
            from src.New.Solvers.Formalization2.ModelTranslation import GetMiniZincSurrogateConstraints

        self.__ModelFile.write(StringToBytes('include "Modules/Formalization' + str(src.init.settings['MiniZinc']['formalization']) + '/SurrogateConstraints.mzn";\n\n'))

        ExcludedFromSurrogate = []
        for Constraint in self._Instance.GetModel().GetRestrictions():
            if Constraint.GetType() == "Colocation" or Constraint.GetType() == "FullDeployment":
                for Comp in Constraint.GetElement("Components"):
                    if not Comp in ExcludedFromSurrogate:
                        ExcludedFromSurrogate.append(Comp)

        for index, Comp in enumerate(self._Instance.GetModel().Components):
            if Comp.Name not in ExcludedFromSurrogate:
                self.__ModelFile.write(StringToBytes("var 0..1024: " + Comp.Name + ";\n"))
        self.__ModelFile.write(b'\n')

        OrComponents = self.__GetOrComponents()
        self.__ModelFile.write(StringToBytes("constraint basicAllocation({"))
        
        for i, Component in enumerate(self._Instance.GetModel().Components):
            if (Component.Name in OrComponents) or (Component.Name in ExcludedFromSurrogate):
                continue

            if i != len(self._Instance.GetModel().Components) - 1:
                self.__ModelFile.write(StringToBytes(Component.Name + ", "))
            else:
                self.__ModelFile.write(StringToBytes(Component.Name))
        self.__ModelFile.write(StringToBytes("});\n"))

        for Constraint in self._Instance.GetModel().GetRestrictions():

            excluded = 0
            if Constraint.GetType().endswith("Bound"):
                for C in Constraint.GetElement("Components"):
                    if C in OrComponents or C in ExcludedFromSurrogate:
                        excluded = 1
                        break

            elif Constraint.GetType() == "RequireProvide":
                if Constraint.GetElement("RequireComponent") in OrComponents or Constraint.GetElement("ProvideComponent") in OrComponents:
                    excluded = 1
                if Constraint.GetElement("RequireComponent") in ExcludedFromSurrogate or Constraint.GetElement("ProvideComponent") in ExcludedFromSurrogate:
                    excluded = 1

            if excluded == 1:
                excluded = 0
                continue

            if Constraint.GetType().endswith("Bound") or Constraint.GetType() == "RequireProvide" or Constraint.GetType() == "ExclusiveDeployment":
                for translation in GetMiniZincSurrogateConstraints(Constraint):
                    self.__ModelFile.write(StringToBytes(translation))

        self.__ModelFile.write(StringToBytes("solve minimize "))
        for index, Comp in enumerate(self._Instance.GetModel().Components):
            if Comp.Name in ExcludedFromSurrogate:
                continue

            if index != len(self._Instance.GetModel().Components) - 1:
                self.__ModelFile.write(StringToBytes(Comp.Name + " + "))
            else:
                self.__ModelFile.write(StringToBytes(Comp.Name))
        self.__ModelFile.write(StringToBytes(";"))

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
        system("pause")
        items = self.__SolveSurrogate()

        print(items)

        # This clears the file used for 
        self.__ModelFile.truncate(0)

        self.__ComputeMiniZincModel()
        self.__ConvertDataFile()

        Mzn_Instance = mzn.Instance(self.__Solver, mzn.Model(self.__ModelFile.name))
        Mzn_Instance.add_file(self.__DataFile.name)
        Mzn_Instance["VM"] = items["objective"]

        return Mzn_Instance.solve(timeout=timedelta(seconds=2400))