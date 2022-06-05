from json import load
from os.path import exists
from os import makedirs

"""
The script provides functions used in all other scripts.

- parse_config()        >   Reads the configuration files and initializes the global variables
- create_directory()    >   Creates a directory if it doesnt already exist.
- log()                 >   Logs messages to console.

For more information regarding the functions, read their documentation.
"""

def parse_config(config_path: str = "Config/config.json"):
    """
    This function opens the configuration files and extracts all the necessary settings
    for the scripts to run properly.

    Args:
        config_path (str, optional): Path to the configuration file. Defaults to "json/config.json".
    """
    global settings, use_cases

    #
    # Temporary variables
    #
    sat_settings = {}
    smt_settings = {}
    test_settings = {}
    solvers = []
    use_cases = []
    
    solver_config = 0
    use_case_config = 0

    #
    # Initializing settings
    #
    settings = {}

    with open(config_path, "r") as file:
        data = load(file)

        try:
            #
            # Loading source details
            #
            for item in data["Source-Config"]:
                if item["Type"] == "MiniZinc":
                    sat_settings["model_path"] = item["Path"]
                    sat_settings["model_ext"] = item["Extension"]
                    sat_settings["formalization"] = item["Formalization"]

                elif item["Type"] == "JSON":
                    smt_settings["model_path"] = item["Path"]
                    smt_settings["model_ext"] = item["Extension"]
                    smt_settings["formalization"] = item["Formalization"]

                else:
                    log("INIT", "ERROR", "Invalid source configuration.")
                    exit(1)

            #
            # Loading input details
            #
            for item in data["Input-Config"]:
                if item["Type"] == "MiniZinc":
                    sat_settings["input_path"] = item["Path"]
                    sat_settings["input_ext"] = item["Extension"]
                    sat_settings["offers"] = item["Offer-Numbers"]

                elif item["Type"] == "JSON":
                    smt_settings["input_path"] = item["Path"]
                    smt_settings["input_ext"] = item["Extension"]
                    smt_settings["offers"] = item["Offer-Numbers"]

                else:
                    log("INIT", "ERROR", "Invalid input configuration.")
                    exit(2)

            #
            # Loading surrogate details
            #
            for item in data["Surrogate-Config"]:
                if item["Type"] == "MiniZinc":
                    sat_settings["surrogate_output_path"] = item["Output-Path"]
                    sat_settings["surrogate_output_ext"] = item["Output-Extension"]
                    sat_settings["surrogate_path"] = item["Model-Path"]
                    sat_settings["surrogate_ext"] = item["Model-Extension"]
                    sat_settings["build_surrogate"] = item['Enabled']

                elif item["Type"] == "JSON":
                    smt_settings["surrogate_output_path"] = item["Output-Path"]
                    smt_settings["surrogate_output_ext"] = item["Output-Extension"]
                    smt_settings["surrogate_path"] = item["Model-Path"]
                    smt_settings["surrogate_ext"] = item["Model-Extension"]
                    smt_settings["build_surrogate"] = item['Enabled']

                
                else:
                    log("INIT", "ERROR", "Invalid surrogate configuration.")
                    exit(3)

            #
            # Loading testing details
            #
            item = data["Test-Config"]
            
            test_settings["runs"] = item["Repetitions"]
            test_settings["output_path"] = item["Output-Path"]

            if item["Symmetry-Breaking"] == True:
                test_settings["symmetry_breakers"] = item["Symmetry-Breaker-List"]
            else:
                test_settings["symmetry_breakers"] = []

            smt_settings["symmetry_breaking_config"] = None
            sat_settings["symmetry_breaking_config"] = item["MiniZinc-SB-File"]

            solver_config = item["Solver-Config-File"]
            use_case_config = item["Use-Case-Config-File"]

        except KeyError:
            log("INIT", "ERROR", "Unknown key in general configuration")
            exit(1)

    settings["MiniZinc"] = sat_settings
    settings["JSON"] = smt_settings
    settings["Test"] = test_settings

    with open(solver_config, "r") as file:
        try:
            data = load(file)

            for type in data["Solver-Types"]:
                for solver in data[f"{type}-Solvers"]:
                    if solver["Enabled"] == True:
                        temp = {}

                        temp["type"] = type
                        temp["name"] = solver["Name"]
                        temp["id"] = solver["Keywd"]

                        solvers.append(temp)
        except KeyError:
            log("INIT", "ERROR", "Unknown key in solver configuration")
            exit(1)
    
    with open(use_case_config, "r") as file:
        try:
            data = load(file)

            for item in data["Use-Cases"]:
                if item["Enabled"] == True:
                    temp = {}

                    temp["name"] = item["Name"]
                    temp["model"] = item["Model-Name"]
                    temp["components"] = []

                    if item["Scaling-Components"] == True:
                        for component in item["Components"]:
                            temp["components"].append(component)
                    
                    if item["Surrogate-Problem"] == True:
                        temp["surrogate"] = item["Surrogate-Model-Name"]

                    use_cases.append(temp)

        except KeyError:
            log("INIT", "ERROR", "Unknown key in use_case configuration")
            exit(1)

    settings["Solvers"] = solvers
    settings["Use-Cases"] = use_cases

def log(phase: str, severity: str, message: str):
    """
    Prints logs to console output

    Args:
        phase (str): The phase of runtime (INIT, PRE-TESTING, TESTING, POST_TESTING)
        severity (str): The severity of the log (INFO, WARN, ERROR)
        message (str): The message
    """
    print("[", phase, "]\t\t[", severity, "] > ", message)

def create_directory(directory_name):
    """
    A function that checks if the directory with provided name already exists and it creates it if it doesn't

    Args:
      directory_name: A string value that represents the name of a directory
    """
    if not exists(directory_name):
        makedirs(directory_name)