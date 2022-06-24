from src.New.Core.Restriction import Restriction
from src.New.Core.Machine import VirtualMachine
from src.New.Core.Model import Model
from json import load
from os.path import exists

class Instance():
    """
    Binds the model to a datafile and a solver
    """

    def __init__(self, ModelFile: str, SymmetryBreaker: str = None) -> None:
        """
        Creates a solvable instance by binding a model to a solver.

        Args:
            ModelFile (str): A path to the model file
            Solver (Solver): A JSON / MiniZinc solver.
            SymmetryBreaker (str): The symmetry breaker to be employed by the solver

        Raises:
            FileNotFoundError: The model file was not found
        """

        try:
            self.__Model = Model(ModelFile)
            self.__SB = SymmetryBreaker
            self.__Offers = []

        except FileNotFoundError:
            raise FileNotFoundError

    def AddDataFile(self, DataFile: str) -> None:
        """
        Appends a list of offers to the instance. This way the same instance can be used
        on multiple offers without needing to be modified.
        
        Args:
            DataFile (str): Path to the data file

        Raises:
            FileNotFoundError: The datafile is missing or does not have JSON format.
        """
        self.__Offers.clear()

        if not exists(DataFile) or not DataFile.endswith(".json"):
            raise FileNotFoundError
        
        with open(DataFile, "r") as input:
            dictionary = load(input)

        for offer in dictionary.values():
            self.__Offers.append(VirtualMachine(offer))

    def GetModel(self) -> Model:
        """
        Makes the model accessible to the solver

        Returns:
            Model: The model of the instance
        """
        return self.__Model

    def GetOffers(self) -> list:
        """
        Makes the offer list accesible to the solver

        Returns:
            list: A list of Virtual Machine offers
        """
        return self.__Offers

    def GetSB(self) -> str:
        """
        Makes the symmetry breaker accessible to the solver

        Returns:
            str: The symmetry breaker.
        """
        return self.__SB

    def SetComponentInstances(self, CompName: str, Inst: int):
        """
        Used to set the number of instances for scaling components.

        Args:
            CompName (str): The name of the component
            Inst (int): The number of instances

        Raises:
            KeyError: Invalid component name.
        """
        try:
            temp = Restriction("EqualBound")

            temp.AddElement(("Components", [self.__Model.GetComponent(CompName).Name]))
            temp.AddElement(("Bound", Inst))

            self.__Model.GetRestrictions().append(temp)
        except KeyError:
            raise KeyError