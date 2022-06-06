from networkx import Graph, find_cliques
from minizinc import Model, Instance, Solver
import src.init

"""
This script constructs the conflict graph for a specific
use-case scenario.
"""

def solve_surrogate(model: str, comp: str = None, inst: int = None):
    """
    For a specific use-case, it solves the surrogate problem in order to get a list
    of the required components.

    Args:
        model (str): The name of the use-case
        comp (str, optional): The name of the scaling component. Defaults to None.
        inst (int, optional): The number of instances for the scaling component. Defaults to 0.
    """

    IModel = Model(f"{src.init.surrogate_path}/{model}_Surrogate.mzn")
    IInst = Instance(Solver.lookup("gecode"), IModel)

    if comp != None:
        IInst[comp] = inst
        
    return IInst.solve()

def get_conflicts(model: str):
    """
    Given a model, the function scans for conflict constraints and returns
    a list of conflicts between components.
    """
    listOfConflicts = {}

    with open(f"{src.init.model_path}/MiniZinc/{model}_template.mzn", "r") as modelFile:
        lines = modelFile.readlines()

        for line in lines:
            if line.startswith("constraint conflict"):
                args = line[20::].split(",")

                component = args[-1][1:-3]
                conflicts = args[1:-2]

                for i in range(len(conflicts)):
                    conflicts[i] = conflicts[i][1::]

                    if i == 0:
                        conflicts[i] = conflicts[i][1::]
                    if i == len(conflicts) - 1:
                        conflicts[i] = conflicts[i][:-1:]

                for conflict in conflicts:
                    if conflict in listOfConflicts.keys():
                        conflicts.remove(conflict)

                listOfConflicts[component] = conflicts

    return listOfConflicts

def getGraphComponents(model: str, comp: str = None, inst: int = 0):
    """
    Gets the list of component and their instances, as well as the list of conflicts between
    components.

    Args:
        model (str): The name of the minizinc model.
        comp (str, optional): The name of the scaling component for the surrogate problem.
        inst (int, optional): The number of instances for the scaling component.
    """

    result = str(solve_surrogate(model, comp, inst))[9:-1].split(", ")[1:-1:]
    components = {}

    startIndex = 0

    #
    # Looping through the components so that, they will respect the following format:
    #    "Component_name" : List of instances
    #
    # e.g. "Wordpress" : [0,1,2,3]
    #
    for i in range(len(result)):
        splitter = result[i].find("=")
        name = result[i][:splitter]
        Cinst = int(result[i][splitter+1:])

        components[name] = []

        if not (name.find("LoadBalancer") != -1 and model=='Wordpress' and inst < 8):
            for i in range(Cinst):
                components[name].append(startIndex)
                startIndex += 1

    conflicts = get_conflicts(model)

    return components, conflicts

def buildConflictGraph(model: str, comp: str = None, inst: int = 0):
    """
    Given a model, this function constructs the conflict graph for the use-case.
    """
    graph = Graph()

    elements = getGraphComponents(model, comp, inst)

    for value in elements[0].values():
        graph.add_nodes_from(value)
    
    for start in elements[1].keys():
        for node in elements[0][start]:
            
            # Add conflicts between different components
            for endPoint in elements[1][start]:
                for endNode in elements[0][endPoint]:
                    graph.add_edge(node, endNode)

    for start in elements[0].values():
        for node in start:
            
            # Add conflicts between instances of the same component
            instance = node + 1
            while instance in start:
                graph.add_edge(node, instance)
                instance += 1

    return elements[0], graph

def buildConflictGraph(elements):
    """
    Given a model, this function constructs the conflict graph for the use-case.
    """
    graph = Graph()

    for value in elements[0].values():
        graph.add_nodes_from(value)
    
    for start in elements[1].keys():
        for node in elements[0][start]:
            
            # Add conflicts between different components
            for endPoint in elements[1][start]:
                for endNode in elements[0][endPoint]:
                    graph.add_edge(node, endNode)

    for start in elements[0].values():
        for node in start:
            
            # Add conflicts between instances of the same component
            instance = node + 1
            while instance in start:
                graph.add_edge(node, instance)
                instance += 1

    return elements[0], graph


def getMaxClique(model: str, comp: str = None, inst: int = 0):
    """
    Returns the clique with maximum deployment size as well as a
    dictionary to map it to components.
    """

    dictionary, graph = buildConflictGraph(model, comp, inst)

    #
    # Sometimes there may be cliques of equivalent sizes, but one
    # clique might have more components than the other, and thus more
    # variables are set.
    #
    # Clique1 = {Wordpress}
    #               1
    # 
    # Clique2 = {MySQL, Varnsih , ...}
    #               1 0 0 0 0 0 0 0
    #
    #

    max_length = len(max(list(find_cliques(graph)), key=lambda x: len(x)))
    filtered_cliques = []

    for clique in list(find_cliques(graph)):
        if len(clique) == max_length:
            filtered_cliques.append(clique)

    #
    # After we found the cliques with maximal deployment size, we count
    # the number of different components and choose the clique with highest one.
    #
    final_cliques = []

    for clique in filtered_cliques:
        maximum = 0

        for item in clique:
            seen = []
            count = 0

            for key in dictionary.keys():
                if item in dictionary[key]:
                    if key not in seen:
                        seen.append(key)
                        count += 1
                    break
        if count > maximum:
            maximum = count
            final_cliques = []
            final_cliques.append(clique)
        elif count == maximum:
            final_cliques.append(clique)

    return dictionary, final_cliques[0]

def getMaxClique(elements):
    """
    Returns the clique with maximum deployment size as well as a
    dictionary to map it to components.
    """

    dictionary, graph = buildConflictGraph(elements)

    #
    # Sometimes there may be cliques of equivalent sizes, but one
    # clique might have more components than the other, and thus more
    # variables are set.
    #
    # Clique1 = {Wordpress}
    #               1
    # 
    # Clique2 = {MySQL, Varnsih , ...}
    #               1 0 0 0 0 0 0 0
    #
    #

    max_length = len(max(list(find_cliques(graph)), key=lambda x: len(x)))
    filtered_cliques = []

    for clique in list(find_cliques(graph)):
        if len(clique) == max_length:
            filtered_cliques.append(clique)

    #
    # After we found the cliques with maximal deployment size, we count
    # the number of different components and choose the clique with highest one.
    #
    final_cliques = []

    for clique in filtered_cliques:
        maximum = 0

        for item in clique:
            seen = []
            count = 0

            for key in dictionary.keys():
                if item in dictionary[key]:
                    if key not in seen:
                        seen.append(key)
                        count += 1
                    break
        if count > maximum:
            maximum = count
            final_cliques = []
            final_cliques.append(clique)
        elif count == maximum:
            final_cliques.append(clique)

    return dictionary, final_cliques[0]