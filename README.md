# Automated cloud deployment

The tool is used to determine a deployment plan for a series of application using a given amount of Virtual Machine (VM) offers
at its disposal. It was designed to be highly configurable and easy to use.

## Setup

This tool makes use of several python packages which must be installed with pip before attempting to use it.

- z3-solver
- docplex
- docloud
- ortools
- networkx
- minizinc

Furthermore, you need the Minzinc and CPLEX applications installed as their binaries are required to use the following solvers:

- Chuffed
- Google OR-Tools
- Gecode
- CPLEX

To install them, please use the following links:

- Minizinc [https://www.minizinc.org/]
- CPLEX [https://www.ibm.com/support/pages/downloading-ibm-ilog-cplex-optimization-studio-v1290]
- Google OR-Tools [https://developers.google.com/optimization/install/download]

## Creating your own use-case

Although the tool comes with some model use-cases, you can also add your own by following these steps:

1. Decide the format of the model (MiniZinc / JSON / Both)
2. Create the model of the application (see guide below)
3. (Optional) For MiniZinc models, create a surrogate model so the script can compute the maximum number of VMs to be used.
4. Run the script *add_useCase.py* which will configure the application for your newly created model
5. (Optional) provide a list of Virtual Machine offers, following the same format as those provided as model
    Note that the offer list must be in the same format as that of the model.

## Running the tool

There are two simple steps in running the tool:

1. Select the configuration you would like to run with (see the configuration options below)
 - **NOTE** Make sure to disable the solvers that aren't compatible with the format of your sources.
2. Run the script *runTests.py*

## Configuration

The configuration of the tool can be found inside the **config** folder, and is split into several JSON files.

### Config.json

This file stores general configuration: from paths to general options for running your tests.

- Source-Config
  Stores the configuration regarding models
  - **Type** : The type of solver the models work with
  - **Path** : The path where the models are found
  - **Extension** : The format of the models
  - **Formalization** : The way the general constraints are represented.

- Input-Config
  Stores data regarding the input fed to solvers when runnign the tests
  - **Type** : The type of solver which accepts the input files
  - **Path** : The path of the input files
  - **Extension** : The format of the input files
  - **Offer Numbers** : The amount of virtual machine offers found in an input file.

- Test-Config
  Stores data regarding the way the tests are carried out
  - **Repetitions** : How many times a specific use case is tested
  - **Symmetry Breaking** : Denotes whether static symmetry breaking techniques should be employed when running the tests
  - **Symmetry Breakers** : Denote all methods of static symmetry breaking which should be tested
  - **Output path** : Denotes where the test results should be placed. The format is *Output-Path/SymmetryBreaker/Solver/UseCase_Offers.csv*
  - **Solver Config File** : Points to where solver-related settings are stored
  - **Use Case Config File** : Points where use-case specific settings are stored

### Solvers.json

This file stores solver related configuration.

- MiniZinc-Solvers
  Stores information regarding the different SAT solvers used for testing
  - **Name** : The name of the solver
  - **Keywd** : A unique identifier of the solver
  - **Enabled** : Denotes whether tests should be run with this solver

- JSON-Solvers
  Stores information regarding the different SMT solvers used for testing
  - **Name** : The name of the solver
  - **Keywd** : A unique identifier of the solver
  - **Enabled** : Denotes whether tests should be run with this solver

### SymmetryBreaking.json

This file stores information required for the usage of symmetry breaking methods with SAT Models.

- SB-Constraints
  Stores information about what constraints should be added for different symmetry breakers.
  - **Tag** : A unique identifier of the symmetry breaking technique
  - **Constraint** : The constraint added to the model. A parameter between brackets will be replaced at runtime with an actual value.

### UseCases.json

This file stores information about each use case.

- Use-Cases
  Stores the configuration of each use-case
  - **Name** : The name of the use-case
  - **Enabled** : Denotes whether the use case should be tested.
  - **Model-Name** : The name of the model used when testing the use case.
  - **Scaling-Components** : Denotes whether the model has components which can be scaled regardless of other restrictions.
  - Components
    If the model supports scaling components, then here is stored a list of all components which can be scaled
    - **Name** : The name of the component
    - **Lower Bound** : The least amount of instances to be deployed
    - **Upper Bound** : The maximum amount instances to be deployed
  - **Surrogate-Problem** : Denotes whether the model has an associated surrogate problem which must be run first
  - **Surrogate-Model-Name** : The name of the model for the surrogate problem
