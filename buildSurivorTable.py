"""
This scripts takes the data from the original csv files,
and builds a csv file containing the data required for
building a survivor table.

@author David Bogdan
@author <bogdan.david02@e-uvt.ro>
"""

import csv, os;

"""
Here are the application settings:
    - OffersList                        --->    A list containing the numbers of virtual machine (VM) 
                                                offers used in the testing

    - SolverList                        --->    A list of solvers used in testing
    - ProblemList                       --->    A list containg the names of the use-cases to be included
                                                when creating the survivor table

    - SymmetryBreakerList               --->    A list of the symmetry breakers used in testing
    - WordPress min / max instances     --->    The lowest / highest number of the Wordpress application instances
                                                used when testing scalabilty for the Wordpress problem.
"""
settings = {
    # General problem settings
    "OffersList" : [20],
    "SolverList" : ["or-tools"],

    # Application specific settings
    "UseCaseList" : [
        "Wordpress"
    ],

    "SymmetryBreakerList" : [
        "FV", "PR", "L", "LX",
        "FVPR", "FVL", "FVLX", "PRL", "PRLX", "LPR", "LLX",
        "FVPRL", "FVPRLX", "FVLPR", "FVLLX", "PRLLX", "LPRLX",
        "FVPRLLX", "FVLPRLX", "NoSym"
    ],

    "CsvHeaders" : [
        "Price min value",
        "Price for each machine",
        "Time"
    ],

    "Output_Directory" : "Results",

    # Problem specific settings
    "WordpressMinInstances" : 3,
    "WordpressMaxInstances" : 12
}

"""
This function creates a new directory

Given a directory name, this function first checks if
the path denotes an already existing directory and if not,
it creates a new one. 

@param      directory_path   The path + name of the directory
"""
def create_directory( directory_path: str ):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


"""
This function retrieves the data from a csv file.

The function uses `csv.DictReader` to process the data from
the file given as argument and returns the processed data.
In this specific case, the function reads the runtimes from
the csv file and outputs the median value.

@param      file_path   The path to the csv file
@return     The median of the execution times
"""
def collect_data_from_csv( file_path: str ):
    noEntries = 0
    totalRunTime = 0.0

    try:
        with open(file_path, "r") as file:
            lines = file.readlines()

            for line in lines:
                elems = line.split(",")
                
                if elems[0] == '\n':
                    continue

                totalRunTime += float(elems[-1])
                noEntries += 1
        return totalRunTime / noEntries
    except FileNotFoundError:
        return 0
    except Exception as e:
        with open(file_path, "r") as file:
            reader = csv.DictReader(file)

            for line in reader:
                #print(line)

                noEntries += 1
                totalRunTime += float(line['Time'])
            
        return totalRunTime / noEntries

"""
This function constructs the file path from the given arguments

Given a set of parameters, the function constructs the file path
using the following formula:

    ------------------------------------------------------------------------------------
    file_path = "Output/MiniZinc_Output/" 
                            + symmetry_breaker + "/" 
                            + solver + "/" 
                            + problem_name + str(no_instances) 
                            + "_Offers" + str( no_offer ) + "_" + solver + ".csv"
    ------------------------------------------------------------------------------------

and returns it.

@param      problem_name        The name of the use-case
@param      symmetry_breaker    The name of the symmetry breaker used when testing
@param      solver              The name of the solver

@param      no_instances        The number of Wordpress instances for the Wordpress use-case
                                In case of other problems, this number will be 0.

@param      no_offers           The number of VM offers for which the test was conducted

@returns    The path created by the formula above.
"""    
def build_file_path( problem_name: str, symmetry_breaker: str, solver: str, no_instances: int, no_offers: int,  ):
    try:
        if no_instances == 0:
            if os.path.exists("Output/Formalization1/csv/"
                        + symmetry_breaker + "/"
                        + solver + "/"
                        + problem_name + "_Offers"
                        + str( no_offers ) + ".csv"):
                return ( "Output/Formalization1/csv/"
                            + symmetry_breaker + "/"
                            + solver + "/"
                            + problem_name + "_Offers"
                            + str( no_offers ) + ".csv" )

        if os.path.exists( "Output/Formalization1/csv/"
                            + symmetry_breaker + "/"
                            + solver + "/"
                            + problem_name + str( no_instances ) + "_Offers"
                            + str( no_offers ) + ".csv"):
            return ( "Output/Formalization1/csv/" + symmetry_breaker + "/"
                                + solver + "/"
                                + problem_name + str( no_instances ) + "_Offers"
                                + str( no_offers ) + ".csv" )
        return ( "Output/Formalization1/csv/" + symmetry_breaker + "/"
                        + solver + "/"
                        + problem_name + str( no_instances ) + "_Offers"
                        + str( no_offers ) + "_" + solver + ".csv" )
    except Exception as e:
        print(problem_name, symmetry_breaker, solver, no_instances, no_offers)
        exit(1)

"""
This function builds an empty dictionary

Given a list of keys, this function creates a dictionary where,
each key corresponds to an empty list, and returns it.

@param      keys    The list of keys
@return     A dictionary with the property key = [] for each key in keys.
"""
def build_dictionary( keys: list ):
    temp_dict = {}

    for key in keys:
        temp_dict[key] = []
    return temp_dict

"""
This function creates the csv for the survivor graph

The function process the data for each and processes it
so it can be used by Microsoft Excel to build a survivor graph.

@param      metric      The metric of the graph
"""
def build_surivor_graph_data( metric: str ):
    metrics = build_dictionary(settings[metric + "List"])

    print(len(metrics['chuffed']))

    for use_case in settings["UseCaseList"]:
        for symmetry_breaker in settings["SymmetryBreakerList"]:
            for solver in settings["SolverList"]:
                for no_offers in settings["OffersList"]:

                    # Loop through each possible csv file and append
                    # the processed data in the metrics dictionary

                    if use_case == "Wordpress":
                        for no_inst in range(settings["WordpressMinInstances"], settings["WordpressMaxInstances"] + 1):
                            path = build_file_path( use_case, symmetry_breaker, solver, no_inst, no_offers )
                            #print(path)

                            if collect_data_from_csv(path) != 0:
                                metrics[solver].append(collect_data_from_csv(path))
                    else:
                        path = build_file_path( use_case, symmetry_breaker, solver, 0, no_offers )

                        if collect_data_from_csv(path) != 0:
                            metrics[solver].append( collect_data_from_csv(path) )

    for runTime_list in metrics.values():
        runTime_list.sort()

    # Adding the virtual best
    metrics["virtual best"] =  []

    no_entries = 0
    for key in metrics.keys():
        if len(metrics[key]) > no_entries:
            no_entries = len(metrics[key])
    no_entries += 1

    for index in range(no_entries - 1):
        lowest = 0

        for key in metrics.keys():
            if key != "virtual best":
                if index < len(metrics[key]):
                    if metrics[key][index] != 0:
                        if metrics[key][index] < lowest or lowest == 0:
                            lowest = metrics[key][index]
        if lowest != 0:
            metrics["virtual best"].append(lowest)
    metrics["virtual best"].sort()

    for key in metrics.keys():
        for i in range(1, len(metrics[key])):
            metrics[key][i] += metrics[key][i-1]

    # Writing the final csv file
    with open(settings["Output_Directory"] + "/solver_survivor.csv", "w") as file:
        for i in range(no_entries):
            file.write(str(i))

            if i != no_entries - 1:
                file.write(",")
        file.write("\n")

        for solver in settings[metric + "List"]:
            file.write(solver + ",")

            for index in range(len(metrics[solver])):
                file.write(str(metrics[solver][index]))

                if index != len(metrics[solver]) - 1:
                    file.write(",")
            file.write("\n")
        file.write("virtual best,")

        for i in range(no_entries - 1):
            file.write( str(metrics["virtual best"][i]) )

            if i != no_entries - 2:
                file.write(",")
        file.write("\n")

"""
This function creates the csv for the survivor graph

The function process the data for each and processes it
so it can be used by Microsoft Excel to build a survivor graph.

@param      metric      The metric of the graph
@param      solver      The solver for which the graph is built
"""
def build_solver_graph_data():
    metric = "SymmetryBreaker"
    metrics = build_dictionary(settings[metric + "List"])

    for use_case in settings["UseCaseList"]:
        for solver in settings["SolverList"]:
            for sym_breaker in settings["SymmetryBreakerList"]:
                for no_offers in settings["OffersList"]:

                    # Loop through each possible csv file and append
                    # the processed data in the metrics dictionary

                    if use_case == "Wordpress":
                        for no_inst in range(settings["WordpressMinInstances"], settings["WordpressMaxInstances"] + 1):
                            path = build_file_path( use_case, sym_breaker, solver, no_inst, no_offers )

                            if collect_data_from_csv(path) != 0:
                                metrics[sym_breaker].append(collect_data_from_csv(path))
                    else:
                        path = build_file_path( use_case, sym_breaker, solver, 0, no_offers )

                        if collect_data_from_csv(path) != 0:
                            metrics[sym_breaker].append( collect_data_from_csv(path) )

    for runTime_list in metrics.values():
        runTime_list.sort()

    # Adding the virtual best

    no_entries = 0
    for key in metrics.keys():
        if len(metrics[key]) > no_entries:
            no_entries = len(metrics[key])
    no_entries += 1

    metrics["virtual best"] =  []

    for index in range(no_entries - 1):
        lowest = 0

        for key in metrics.keys():
            if key != "virtual best":
                if index < len(metrics[key]):
                    if metrics[key][index] != 0:
                        if metrics[key][index] < lowest or lowest == 0:
                            lowest = metrics[key][index]
        if lowest != 0:
            metrics["virtual best"].append(lowest)
    metrics["virtual best"].sort()

    for key in metrics.keys():
        for i in range(1, len(metrics[key])):
            metrics[key][i] += metrics[key][i-1]

    # Writing the final csv file
    with open(settings["Output_Directory"] + "/Best_SB_" + settings["SolverList"][0] + "_" + settings["UseCaseList"][0] + str(settings["OffersList"][0]) + ".csv", "w") as file:
        for i in range(no_entries):
            file.write(str(i))

            if i != no_entries - 1:
                file.write(",")
        file.write("\n")

        for solver in settings[metric + "List"]:
            file.write(solver + ",")

            for index in range(len(metrics[solver])):
                file.write(str(metrics[solver][index]))

                if index != len(metrics[solver]) - 1:
                    file.write(",")
            file.write("\n")
        file.write("virtual best,")

        for i in range(no_entries - 1):
            file.write( str(metrics["virtual best"][i]) )

            if i != no_entries - 2:
                file.write(",")
        file.write("\n")

if __name__ == '__main__':
    create_directory("Results")

   #build_surivor_graph_data("Solver")
    build_solver_graph_data()
