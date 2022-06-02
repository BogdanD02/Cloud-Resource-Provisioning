/*
 * Secure Web Container for MiniZinc
 * ---------------------------------
 *
 * @author 
 *    David Bogdan
 *    bogdan.david02@e-uvt.ro
 */

/***********************************
 ****                           ****
 ****      EXTERNAL MODULES     ****
 ****                           ****
 ***********************************/
include "Modules/Formalization1/SymmetryBreaking.mzn";
include "Modules/Formalization1/GeneralVariables.mzn";
include "Modules/Formalization1/GeneralConstraints.mzn";


/***********************************
 ****                           ****
 ****        CONSTANTS          ****
 ****                           ****
 ***********************************/
int: Balancer = 1;
int: Apache = 2;
int: Ngnix = 3;
int: IDSServer = 4;
int: IDSAgent = 5;

           
/***********************************
 ****                           ****
 ****      MODELING PROBLEM     ****
 ****                           ****
 ***********************************/

% From the problem description, you can have 0 instances of Apache or Ngnix (but not both simulaneously) as the constraint
% refers to the total number of instances (Apache and Ngnix combined), but we left it here so
% the implementation is similar with the one used in SMT Test cases.
constraint basicAllocation(AssignmentMatrix, {}, S, VM);

constraint occupancy(AssignmentMatrix, OccupancyVector, NoComponents, VM);
constraint capacity(AssignmentMatrix, CompREQ, VMSpecs, VMType, HardwareREQ, NoComponents, VM);
constraint link(VMSpecs, VMPrice, OccupancyVector, VMType, Price, VMOffers, VM);

% Problem-specific constraints
constraint equalBound(AssignmentMatrix, VM, Balancer, 1);
constraint lowerBound(AssignmentMatrix, VM, Apache, Ngnix, 3);

constraint conflict(AssignmentMatrix, {Apache, Ngnix, IDSServer, IDSAgent}, VM, Balancer);
constraint conflict(AssignmentMatrix, {Balancer, Apache, Ngnix, IDSAgent}, VM, IDSServer);
constraint conflict(AssignmentMatrix, {Ngnix}, VM, Apache);

constraint boundedRequireProvide(AssignmentMatrix, VM, IDSServer, IDSAgent, 10);

constraint fullDeployment(AssignmentMatrix, {Balancer, IDSServer}, VM, NoComponents, IDSAgent);


/***********************************
 ****                           ****
 ****      SOLVING PROBLEM      ****
 ****                           ****
 ***********************************/
constraint AssignmentMatrix[Balancer,1] = 1;
constraint AssignmentMatrix[IDSServer, 1] = 0;
constraint AssignmentMatrix[Apache, 1] = 0;
constraint AssignmentMatrix[Ngnix, 1] = 0;
constraint AssignmentMatrix[IDSServer,2] = 1;
constraint AssignmentMatrix[Balancer, 2] = 0;
constraint AssignmentMatrix[Apache, 2] = 0;
constraint AssignmentMatrix[Ngnix, 2] = 0;
constraint AssignmentMatrix[Apache,3] = 1;
constraint AssignmentMatrix[Balancer, 3] = 0;
constraint AssignmentMatrix[IDSServer, 3] = 0;
constraint AssignmentMatrix[Ngnix, 3] = 0;
constraint AssignmentMatrix[Ngnix,4] = 1;
constraint AssignmentMatrix[Ngnix,5] = 1;
constraint AssignmentMatrix[Balancer, 4] = 0;
constraint AssignmentMatrix[IDSServer, 4] = 0;
constraint AssignmentMatrix[Apache, 4] = 0;
constraint AssignmentMatrix[Balancer, 5] = 0;
constraint AssignmentMatrix[IDSServer, 5] = 0;
constraint AssignmentMatrix[Apache, 5] = 0;
constraint LX(AssignmentMatrix, NoComponents, VM, 6);
solve minimize sum(k in 1..VM)(Price[k]);