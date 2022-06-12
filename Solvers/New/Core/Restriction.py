from Solvers.New.Core.Component import Component

class Restriction:
    """
    Provides general information about a restriction, such as its type and components.
    """
    Type: str
    Elements: dict

    def __init__(self, Type: str, Elements: dict = {}) -> None:
        """
        Creates a new restriction of a specific type

        Args:
            Type (str): The type of the restriction
            Components (dict, optional): A dictionary in which the key denotes the element meaning. Defaults to to {}.
        """

        self.Type = Type
        self.Elements = Elements

    def AddElement(self, Comp: tuple) -> None:
        """
        Adds a new component to this restriction.
        
        Args:
            Comp (tuple): A key - value pair to be added to existing elements.

        Raises:
            ValueError : The component already exists.
        """

        if Comp[0] not in self.Elements.keys():
            self.Elements[Comp[0]] = Comp[1]
        else:
            raise ValueError