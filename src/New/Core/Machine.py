
class VirtualMachine():
    """
    This class holds the specifications of a virtual machine.
    """

    def __init__(self, Specs: dict) -> None:
        """
        Creates a new virtual machine model.

        Args:
            Specs (dict): The dictionary taken from the data file
        """

        self.Price = Specs["price"]
        self.HardwareSpecifications = {}
        
        for key, value in Specs.items():
            if key != "price":
                self.HardwareSpecifications[key] = value
    
    def GetPrice(self) -> int:
        """
        Returns the price of the virtual machine

        Returns:
            int: The price of the machine
        """
        return self.Price

    def GetSpecifications(self) -> dict:
        """
        Returns a dictionary containing the Hardware specifications of the machine.

        Returns:
            dict: The hardware specifications
        """
        return self.HardwareSpecifications