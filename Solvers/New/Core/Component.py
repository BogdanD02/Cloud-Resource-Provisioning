
class Component:
    """
    Holds the name of a component as well as its requirements.
    The requirements are contained inside a dictionary with the following meaning:
        key = The name of the requirement (e.g. CPU, Memory, Storage)
        value = The amount of requirement (e.g. 1000)
    """
    Name: str
    Requirements: dict

    def __init__(self, Name: str, Requirements: dict = {}) -> None:
        """
        Initializes a new component with the given parameters.

        Args:
            Name (str): The name of the component
            Requirements (dict, optional): A dictionary of component requirements. Defaults to {}
        """
        self.Name = Name
        self.Requirements = Requirements

    def __getitem__(self, __name: str):
        """
        Returns a specific requirement based on key.
        
        Raises:
            KeyError: No requirement with that specific name found.
        """

        if __name in self.Requirements.keys():
            return self.Requirements[__name]
        
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

        if Name not in self.Requirements.keys():
            self.Requirements[Name] = Value
        else:
            raise KeyError