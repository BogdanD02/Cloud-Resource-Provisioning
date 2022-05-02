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
include "Modules/Formalization2/GeneralVariables.mzn";
include "Modules/Formalization2/GeneralConstraints.mzn";


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
constraint basicAllocation(AssignmentMatrix, VM, VMOffers, NoComponents, {});

constraint capacity(AssignmentMatrix, CompREQ, VMSpecs, VMType, HardwareREQ, NoComponents, VM, VMOffers);

% Problem-specific constraints
constraint equalBound(AssignmentMatrix, VM, VMOffers, {Balancer}, 1);
constraint lowerBound(AssignmentMatrix, VM, VMOffers, {Apache, Ngnix}, 3);

constraint conflict(AssignmentMatrix, VM, VMOffers, Balancer, {Apache, Ngnix, IDSServer, IDSAgent});
constraint conflict(AssignmentMatrix, VM, VMOffers, IDSServer, {Balancer, Apache, Ngnix, IDSAgent});
constraint conflict(AssignmentMatrix, VM, VMOffers, Apache, {Ngnix});


constraint fullDeployment(AssignmentMatrix, VM, VMOffers, NoComponents, IDSAgent, {Balancer, IDSServer});


/***********************************
 ****                           ****
 ****      SOLVING PROBLEM      ****
 ****                           ****
 ***********************************/
constraint linkedTypes(AssignmentMatrix, VMType, VM, VMOffers, NoComponents);
constraint linkedPrice(VMType, VMPrice, Price, VM, VMOffers);
constraint uniqueType(VMType, VM, VMOffers);
constraint uniqueAlloc(AssignmentMatrix, VM, NoComponents, VMOffers);
solve minimize sum(k in 1..VM)(Price[k]);