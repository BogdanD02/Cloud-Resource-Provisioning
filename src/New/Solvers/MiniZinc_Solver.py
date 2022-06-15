from distutils import extension
import enum
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
        self.__ModelFile = NamedTemporaryFile(suffix='.mzn')
        self.__DataFile = NamedTemporaryFile(suffix='.dzn')

    def __StringToBytes(self, item: str) -> bytes:
        """
        Converts a given string to bytes.

        Args:
            item (str): The string to be converted

        Returns:
            bytes: The bytes conversion of the string
        """
        return bytes(item.encode('utf-8'))
        

    def __ComputeMiniZincModel(self):
        pass

    def __ConvertDataFile(self):
        """
        Converts the data taken from the JSON data file into a suitable MiniZinc format.
        """

        VMPrice = []
        VMSpecs = []

        for Offer in self._Instance.GetOffers():
            VMPrice.append(Offer.GetPrice())
            VMSpecs.append(Offer.GetSpecifications().values())

        self.__DataFile.write(self.__StringToBytes("VMOffers = " + str(len(VMPrice)) + ";\n"))
        self.__DataFile.write(b"VMPrice = [")

        for index, Price in enumerate(VMPrice):
            if index != len(VMPrice) - 1:
                self.__DataFile.write(self.__StringToBytes(str(Price) + ", "))
            else:
                self.__DataFile.write(self.__StringToBytes(str(Price) + "];\n"))
        
        self.__DataFile.write(b"VMSpecs = [")

        for index, Specs in enumerate(VMSpecs):
            if index != len(VMSpecs) - 1:
                self.__DataFile.write(b"|")
                
                for item in Specs:
                    self.__DataFile.write(self.__StringToBytes(str(item) + ", ")) 
                
                self.__DataFile.write(b"\n")
            else:
                self.__DataFile.write(b"|")
                
                for itemIndex, item in enumerate(Specs):
                    if itemIndex != len(Specs) - 1:
                        self.__DataFile.write(self.__StringToBytes(str(item) + ", ")) 
                    else:
                        self.__DataFile.write(self.__StringToBytes(str(item) + "|];"))

                self.__DataFile.write(b"\n") 
        self.__DataFile.seek(0)

    def _GenerateConstraints(self):
        self.__ComputeMiniZincModel()
        self.__ConvertDataFile()


        self.__DataFile.close()
        self.__ModelFile.close()