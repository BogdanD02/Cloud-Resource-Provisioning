
class Restriction():
    """
    Provides general information about a restriction, such as its type and components.
    """

    def __init__(self, Type: str) -> None:
        """
        Creates a new restriction of a specific type

        Args:
            Type (str): The type of the restriction
            Components (dict, optional): A dictionary in which the key denotes the element meaning. Defaults to to {}.
        """

        self.Type = Type
        self.Elements = {}

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

    def GetElement(self, Key: str):
        """
        Returns the value of an element in the restriction.

        Args:
            Key (str): The key of the element

        Returns:
            Any: The value of the element

        Raises:
            KeyError: No element with the specified key exists.
        """

        try:
            return self.Elements[Key]
        except KeyError:
            raise KeyError

    def GetType(self) -> str:
        """
        Returns the type of the constraint

        Returns:
            str: The type of the constraint
        """
        return self.Type