from json import load, dump

"""
This scripts adds a new use_case to the configuration file.
"""

# Settings
original = {}

def import_settings():
    """
    Imports the original settings
    """
    global original, configPath
    
    with open("Config/config.json", "r") as f:
        configPath = load(f)["Use-Case-Config-File"]
        
    with open(configPath, "r") as f:
        original = load(f)
        
def update():
    """
    Replaces the old json settings with the new ones
    """
    global original
    
    with open("config/config.json", "w") as f:
        dump(configPath, f)

if __name__ == '__main__':
    import_settings()
    
    useCase = {}
    useCase["name"] = input("Enter the name of the use-case > ")
    useCase["enabled"] = True
    useCase["model_name"] = input("Enter the name of the MiniZinc model > ")
    
    multi_inst = input("Does the use-case have a scaling component ? [Y / N] > ")
    if multi_inst == "Y":
        useCase["multi_inst"] = True
        useCase["low_inst"] = int(input("Enter the lowest amount of instances > "))
        useCase["high_inst"] = int(input("Enter the highest amount of instances > "))
    else:
        useCase["multi_inst"] = False
    
    has_surr = input("Does the use-case have a Surrogate problem ? [Y / N] > ")
    if has_surr == "Y":
        useCase["has_surrogate"] = True
        useCase["surrogate_model"] = input("Please enter the name of the surrogate model > ")
    else:
        useCase["has_surrogate"] = False
    original["use_cases"].append(useCase)
    
    update()