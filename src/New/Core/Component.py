
class Component():
    """
    Holds the name of a component as well as its requirements.
    The requirements are contained inside a dictionary with the following meaning:
        key = The name of the requirement (e.g. CPU, Memory, Storage)
        value = The amount of requirement (e.g. 1000)
    """

    def __init__(self, Name: str, HardwareRequirements: dict = {}) -> None:
        """
        Initializes a new component with the given parameters.

        Args:
            Name (str): The name of the component
            Requirements (dict, optional): A dictionary of component requirements. Defaults to {}
        """
        self.Name = Name
        self.HardwareRequirements = HardwareRequirements

    def __getitem__(self, __name: str):
        """
        Returns a specific requirement based on key.
        
        Raises:
            KeyError: No requirement with that specific name found.
        """

        if __name in self.HardwareRequirements.keys():
            return self.HardwareRequirements[__name]
        
        raise KeyError

    def AddRequirement(self, Name: str, Value: int) -> None:
        """
        Adds a new requirement to the component.

        Args:
            Name (str): The name of the requirement
            Value (int): The value of the requirement
        
        Raises:
            KeyError: The requirement already exists.
        """

        if Name not in self.HardwareRequirements.keys():
            self.HardwareRequirements[Name] = Value
        else:
            raise KeyError