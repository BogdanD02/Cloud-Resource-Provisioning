from Solvers.New.Core.Component import Component
from Solvers.New.Core.Restriction import Restriction
from os.path import exists
from json import load
from src.init import log


class Model:
    """
    A representation of the JSON problem model.
    """
    Name: str
    Components: list
    Restrictions: list

    def __init__(self, ModelFile: str) -> None:
        """
        Reads the JSON Model file and sets the components and restrictions.

        Args:
            ModelFile (str): The path to the JSON model file.
        
        Raises:
            FileNotFoundError: The path specified is invalid or the file is not in the JSON format.
        """

        if not exists(ModelFile) or not ModelFile.endswith(".json"):
            raise FileNotFoundError

        with open(ModelFile, "r") as source:
            dictionary = load(ModelFile)
        
        self.Name = dictionary["Application"]
        self.Components = []
        self.Restrictions = []

        #
        # Setting Components
        #
        for Comp in dictionary["Components"]:
            self.Components.append(
                Component(Comp["Name"], Comp["Restrictions"])
            )

        #
        # Setting Restrictions
        #
        for R in dictionary["Restrictions"]:
            temp = Restriction(R["Type"])

            skip = 1
            for key, value in R:
                if skip == 1:
                    skip = 0
                    continue
                
                try:
                    temp.AddElement((key, value))
                except KeyError:
                    log("PRE-TESTING", "WARN", "Found duplicate key in model. Skipping duplicates...")
            self.Restrictions.append(temp)
