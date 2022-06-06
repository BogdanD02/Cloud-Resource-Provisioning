from venv import create
from src.model import prepare_model
from minizinc import Instance, Model, Solver
from csv import DictReader, DictWriter
from time import time
from datetime import timedelta
from os.path import exists
from src.init import log, create_directory, parse_config
from src.surrogate import build_surrogate, build_components
import src.init
import src.smt

"""
This script interprets the configuration file and runs the test cases
automatically, making the necessary changes.

CONFIGURATION       INTERPRETATION

model_path          Where MiniZinc models are located
input_path          Where input files are located
input_format        The format of the DZN Files
output_path         The path where CSV output files will be placed
output_format       The format of the CSV file name
solvers             A list of the solvers to be used in testing: keywd = the phrase used in Solver.lookup()
offers              A list of possible VM Offers
sym_breaking        Denotes whether the tests should be done with symmetry breakers or not
sym_breakers        A list of symmetry breaker keywords to be used in testing if the above is true
formalization       Denotes the formalization of general constraints (1 or 2)
tests               Denotes how many tests should be performed for the same configuration (model, solver, symmetry breaker, offers)
source_refactor     Allows the script to make changes to the MiniZinc models if needed (e.g. to add symmetry breakers)
build_surrogate     Tells the script to run the surrogate scripts for use-cases
use-cases           A list of all use-cases to be tested.

This represents a brief description for all the options found in the configuration file.
For more details pleases look in the README file.
"""
   
def prepare_minizinc_instance(use_case: dict, solver: str, offer: int, scaling_components: list = []):
    """
    Prepares a Minizinc instance based off the model path and (optionally) the number of instances
    for a specific component.

    Args:
        use_case (dict): The use_case data.
        solver (str): The identifier of the solver
        offer (int): The number of VM offers
        scaling_components (list, optional): A list of scaling components and their instances. Defaults to []

    Returns:
        Minizinc_instance (Instance): A runnable instance of the model.
    """    
    inst = 0

    for item in scaling_components:
        inst += item["inst"]

    Minizinc_instance = Instance(Solver.lookup(solver), Model(f"{src.init.settings['MiniZinc']['model_path']}/{use_case['model']}.{src.init.settings['MiniZinc']['model_ext']}"))

    with open(f"{src.init.settings['MiniZinc']['surrogate_output_path']}/Surrogate.{src.init.settings['MiniZinc']['surrogate_output_ext']}", "r") as surrogate:
        reader = DictReader(surrogate)
        
        for line in reader:
            if line["Name"].find(use_case["name"]) > -1 and int(line["Instances"]) == inst:
                Minizinc_instance["VM"] = int(line["Estimated VMs"])
                break
        else:
            raise Exception("Use-case not found ! ----- " + use_case["name"])
        
    # Settable --- The name of the input DZN file
    Minizinc_instance.add_file(f"{src.init.settings['MiniZinc']['input_path']}/{use_case['model']}_Offers{offer}.dzn")

    return Minizinc_instance
   
def writeOutput(output_path: str, form: int, result, name: str, solver: str, offers: int, inst: int = 0, breaker: str = None):
    """
    Creates a CSV file with the results.

    Args:
        output_path (str): The path where to place the file
        form (int): The formalization
        result ([type]): The results of all runtimes
        name (str): The name of the use-case
        solver (str): The keyword of the solver
        offers (int): THe number of offers
        inst (int, optional): The number of instances for the scaling component. Defaults to 0.
        breaker (int, optional): The symmetry breaker used in testing. Defaults to None
    """
    output_path = f"{output_path}/Formalization{form}"

    create_directory(output_path)
    create_directory(f"{output_path}/csv")

    if breaker != None:
        create_directory(f"{output_path}/csv/{breaker}")
        output_path = f"{output_path}/csv/{breaker}"
    else:
        create_directory(f"{output_path}/csv/NoSym")
        output_path = f"{output_path}/csv/NoSym"
    create_directory(f"{output_path}/{solver}")

    if inst == 0:
        file_name = f"{output_path}/{solver}/{name}_Offers{offers}.csv"
    else:
        file_name = f"{output_path}/{solver}/{name}{inst}_Offers{offers}.csv"

    with open(file_name, "w") as file:
        writer = DictWriter(file, ["Total Price", "Price / Machine", "Runtime"])
        writer.writeheader
        writer.writerows(result)

def run_test(use_case: dict, solver: dict, breaker: str = None, scaling_components: list = []):
    """
    This function runs conducts the tests for a specific scenario and calls
    the writeOutput() function to record the test results.

    Args:
        use_case (dict): The use-case to be tested
        breaker (str, optional): The symmetry breaker employed in testing. Defaults to None.
        solver (dict): The id solver which will carry out the tests.
        scaling_components (list, optional): A list of scaling components and their instances. Defaults to []
    """

    inst = 0

    for item in scaling_components:
        inst += item['inst']

    log("PRE-TESTING", "INFO", f"Testing with {solver['name']}")

    if solver['type'] == 'MiniZinc':
        log("PRE-TESTING", "INFO", "Applying required changes to source...")
        prepare_model(use_case, src.init.settings['MiniZinc']['formalization'], breaker, scaling_components)

        for offer in src.init.settings['MiniZinc']['offers']:
            lastOffer = offer
            results = []

            for i in range(src.init.settings['Test']['runs']):
                try:
                    log("TESTING", "INFO", "Preparing MiniZinc Instance...")
                    instance = prepare_minizinc_instance(use_case, solver['id'], offer, scaling_components)

                    log("TESTING", "INFO", "Started test case...")

                    start_time = time()
                    result = instance.solve(timeout=timedelta(seconds=2400), optimisation_level=0)
                    runtime = time() - start_time

                    if runtime > 2400:
                        log("TESTING", "WARN", "Test aborted. Timeout")
                        break
                    
                    results.append({})  
                    log("TESTING", "INFO", "Test completed. Runtime : {rt:.2f}".format(rt=runtime))

                    results[-1]["Price / Machine"] = result['Price']
                    results[-1]["Total Price"] = sum(result['Price'])
                    results[-1]["Runtime"] = runtime

                except Exception as e:
                    log("TESTING", "ERROR", "Failed to instantiate MiniZinc instance. Aborting...")
                    print(e)
                    break
            else:
                path = f"{src.init.settings['Test']['output_path']}"
                
                log("TESTING", "INFO", "Writing output...")
                writeOutput(path, src.init.settings['MiniZinc']['formalization'], results, use_case['model'], solver['id'], offer, inst, breaker)

                continue
            break

    elif solver['type'] == 'JSON':
        create_directory(f"{src.init.settings['Test']['output_path']}/Formalization{src.init.settings['JSON']['formalization']}/smt")
        create_directory(f"{src.init.settings['Test']['output_path']}/Formalization{src.init.settings['JSON']['formalization']}/lp")

        for offer in src.init.settings['JSON']['offers']:
            lastOffer = offer
            results = []

            log("PRE-TESTING", "INFO", "Loading JSON Source...")
            instance = src.smt.prepareManuverProblem(f"{src.init.settings['JSON']['model_path']}/{use_case['model']}.{src.init.settings['JSON']['model_ext']}", 
                                                 f"{src.init.settings['JSON']['input_path']}/offers_{offer}.{src.init.settings['JSON']['input_ext']}", scaling_components)
            SMTsolver = src.smt.getSolver(solver['id'], src.init.settings['JSON']['formalization'])      

            for i in range(src.init.settings['Test']['runs']):
                log("TESTING", "INFO", "Started test case...")

                getattr(SMTsolver, "init_problem")(instance, "optimize", sb_option=breaker, 
                                                    smt2lib=f"{src.init.settings['Test']['output_path']}/Formalization{src.init.settings['JSON']['formalization']}/smt/{use_case['model']}_{inst}_{offer}_{breaker}.smt",
                                                    cplexLPPath=f"{src.init.settings['Test']['output_path']}/Formalization{src.init.settings['JSON']['formalization']}/lp/{use_case['model']}_{inst}_{offer}_{breaker}.lp")
                
                price, distr, runtime, buf1, buf2 = SMTsolver.run()

                result = {}
                result["Price"] = distr

                if not runtime or runtime > 2400:
                    log("TESTING", "WARN", "Test aborted. Timeout")
                    break
                
                results.append({})  
                log("TESTING", "INFO", "Test completed. Runtime : {rt:.2f}".format(rt=runtime))

                results[-1]["Price / Machine"] = result['Price']
                results[-1]["Total Price"] = sum(result['Price'])
                results[-1]["Runtime"] = runtime
            else:
                path = f"{src.init.settings['Test']['output_path']}"
                
                log("TESTING", "INFO", "Writing output...")
                writeOutput(path, src.init.settings['JSON']['formalization'], results, use_case['model'], solver['id'], offer, inst, breaker)

                continue
            break
    return lastOffer

def run_tests():
    """
    Goes through all use-cases and tests each of them via the run_test() function.
    
    """
    create_directory(f"{src.init.settings['Test']['output_path']}")

    if src.init.settings['Test']['symmetry_breakers'] != []:
        for breaker in src.init.settings['Test']['symmetry_breakers']:

            log("PRE-TESTING", "INFO", f"Using symmetry breaker {breaker}")

            for use_case in src.init.settings['Use-Cases']:

                log("PRE-TESTING", "INFO", "Running tests for " + use_case["name"])

                combinations = []
                if use_case["components"] != []:
                    combinations = build_components(use_case["components"])

                tresholds = {}

                if combinations != []:
                    for comb in combinations:
                        for solver in src.init.settings['Solvers']:
                            if solver['id'] in tresholds.keys() and tresholds[solver['id']] == src.init.settings[solver['type']]['offers'][0]:
                                break

                            lastOffer = run_test(use_case, solver, breaker, comb)
                
                            tresholds[solver['id']] = lastOffer
                else:
                    for solver in src.init.settings['Solvers']:
                        run_test(use_case, solver, breaker)

    else:
        log("PRE-TESTING", "INFO", "Skipping symmetry breakers...")

        for use_case in src.init.settings['Use-Cases']:

            log("PRE-TESTING", "INFO", "Running tests for " + use_case["name"])

            combinations = []
            if use_case["components"] != []:
                combinations = build_components(use_case["components"])

            tresholds = {}

            if combinations != []:
                for comb in combinations:
                    for solver in src.init.settings['Solvers']:
                        if solver['id'] in tresholds.keys() and tresholds[solver['id']] == src.init.settings[solver['type']]['offers'][0]:
                            break

                        lastOffer = run_test(use_case, solver, None, comb)
            
                        tresholds[solver['id']] = lastOffer
            else:
                for solver in src.init.settings['Solvers']:
                    run_test(use_case, solver)

                        
def main() :
    try:
        log("INIT", "INFO", "Starting script, reading config file")
        parse_config()
    except Exception as e:
        log("INIT", "ERROR", "Error parsing configuration file. Maybe invalid path or misconfiguration ?")
        exit(1)
        
    # If set, call the surrogate script
    if src.init.settings['MiniZinc']['build_surrogate'] == True:
        try:
            log("PRE-TESTING", "INFO", "Building surrogate file...")
            
            if exists(f"{src.init.settings['MiniZinc']['surrogate_output_path']}/Surrogate.{src.init.settings['MiniZinc']['surrogate_output_ext']}"):
                log("PRE-TESTING", "WARN", "Surrogate output already exists. Rewriting...")
            
            build_surrogate()

        except:
            log("PRE-TESTING", "ERROR", "Error executing surrogate script.")
            exit(1)
    elif not exists(f"{src.init.settings['MiniZinc']['surrogate_output_path']}/Surrogate.{src.init.settings['MiniZinc']['surrogate_output_ext']}"):
        log("PRE-TESTING", "ERROR", "Surrogate file not found. Please enable surrogate building and retry..")
        exit(1)
    else:
        log("PRE-TESTING", "INFO", "Skipping surrogate file generation...")
        
    run_tests()


if __name__ == '__main__':
    main()    
