from src.New.Core.Component import Component
from src.New.Core.Restriction import Restriction
from os.path import exists
from json import load
from src.init import log


class Model():
    """
    A representation of the problem model.
    """

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
            dictionary = load(source)
        
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

            for key, value in list(R.items())[1:]:             
                try:
                    temp.AddElement((key, value))
                except ValueError:
                    log("PRE-TESTING", "WARN", "Found duplicate key in model. Skipping duplicates...")

            self.Restrictions.append(temp)

    def GetComponent(self, Name: str) -> Component:
        """
        Gets a component by its name.

        Args:
            Name (str): The name of the component
        
        Returns:
            Component: The component with that name.
        
        Raises:
            KeyError: Component not found
        """
        for Comp in self.Components:
            if Comp.Name == Name:
                return Comp
        
        raise KeyError

    def GetRestrictions(self) -> list:
        """
        This is used when employing symmetry breakers.
        
        Returns:
            list: A list of Restriction objects.
        """
        return self.Restrictions