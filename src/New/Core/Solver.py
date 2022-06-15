import minizinc as mzn
from src.New.Core.Instance import Instance

class Solver:
    """
    This class embodies a general solver (format - independent).

    The solvers for the MiniZinc format must be obtained via the GetMiniZincSolver() function
    as their binaries are defined elsewhere.

    The solvers for the JSON format will be classes which inherit this base class.
    """

    def __init__(self, Inst: Instance) -> None:
        self._Instance = Inst

    def _GetMiniZincSolver(self, KeyWord: str) -> mzn.Solver:
        """
        Returns a minizinc solver based on its keyword
        
        Args:
            KeyWord (str): The keyword of the solver (see solver configuration)

        Returns:
            mzn.Solver: A minizinc solver

        Raises:
            KeyError: No solver was found
        """
        
        try:
            return mzn.Solver.lookup(KeyWord)
        except LookupError:
            raise KeyError

    def _GenerateConstraints(self):
        """
        Generates the specific solver constraints.

        Args:
            model (Model): The model for which the constraints are generated.
        """
        pass

    def _SolveSurrogate(self) -> list:
        """
        Solves the surrogate model and returns a list of modified constraints.

        Returns:
            list: A list of Restriction objects which will replace the original restrictions.
        """
        pass

    def Solve(self):
        """
        Solves a specific instance.
        
        This method is overriden by JSON solvers and is not called for MiniZinc solvers,
        as they do not inherit this class.
        """
        pass