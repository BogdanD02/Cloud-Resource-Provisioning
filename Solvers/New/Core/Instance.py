from Solvers.New.Core.Model import Model
from json import load
from os.path import exists
#from Solvers.New.Core.Solver import Solver

class Instance:
    """
    Binds the model to a datafile and a solver
    """
    __Model: Model
    __Offers: list
    #__Solver: Solver

    def __init__(self, ModelFile, Solver) -> None:
        """
        Creates a solvable instance by binding a model to a solver.

        Args:
            ModelFile (str): A path to the model JSON file
            Solver (Solver): A JSON-type solver (typically Z3 and CPLEX)

        Raises:
            FileNotFoundError: The model file was not found
        """

        try:
            self.__Model = Model(ModelFile)
            self.__Solver = Solver

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
        
        if not exists(DataFile) or not DataFile.endswith(".json"):
            raise FileNotFoundError
        
        with open(DataFile, "r") as input:
            self.__Offers = load(input)
    
    def solve(self) -> dict:
        """
        Solves the model and returns the output.

        Returns:
            Result (dict): The output from running the model.
        """
        return self.Solver.run()