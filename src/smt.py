import json
from Solvers.Core.ProblemDefinition import ManeuverProblem

def read_available_configurations(fileConfigurations):
    with open(fileConfigurations) as json_data:
        dictionary = json.load(json_data)
    availableConfigurations = []
    for key, value in dictionary.items():
        l = [key]
        l.append(value["cpu"])
        l.append(value["memory"])
        l.append(value["storage"])
        l.append(value["price"])
        availableConfigurations.append(l)
    
    return availableConfigurations


def prepareManuverProblem(problem_file_name, configurations_file_name, scaling_components):
    mp = ManeuverProblem()
    offers_list = read_available_configurations(configurations_file_name)
    try:
        if scaling_components != []:
            inst = scaling_components[0]['inst']
        else:
            inst = 0

        mp.readConfiguration(problem_file_name, offers_list, inst)
    except IOError:
        print("File '%s' doesn't exist", problem_file_name)
        exit(1)

    mp.priceOffersFile = configurations_file_name

    return mp

def getSolver(solver, formalization: int = 1):
    if formalization == 1:
        if solver == "z3":
            from Solvers.Formalization1.Z3.SMT_Solver_Z3_Int_SB_AllCombinationsOffers import Z3_SolverInt_SB_Enc_AllCombinationsOffers
            return Z3_SolverInt_SB_Enc_AllCombinationsOffers()
        elif solver == "cplex":
            from Solvers.Formalization1.CPLEX.CP_CPLEX_Solver_Enc_AllCombinationsOffers import CPlex_Solver_SB_Enc_AllCombinationsOffers
            return CPlex_Solver_SB_Enc_AllCombinationsOffers()
    elif formalization == 2:
        if solver == "z3":
            from Solvers.Formalization2.Z3.SMT_Solver_Z3_Int_SB_AllCombinationsOffers import Z3_SolverInt_SB_Enc_AllCombinationsOffers
            return Z3_SolverInt_SB_Enc_AllCombinationsOffers()
        elif solver == "cplex":
            from Solvers.Formalization2.CPLEX.CP_CPLEX_Solver_Enc_AllCombinationsOffers import CPlex_Solver_SB_Enc_AllCombinationsOffers
            return CPlex_Solver_SB_Enc_AllCombinationsOffers()